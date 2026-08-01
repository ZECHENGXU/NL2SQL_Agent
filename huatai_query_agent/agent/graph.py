from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.nodes import m1_nodes
from huatai_query_agent.agent.state import AgentState, add_trace, new_agent_state
from huatai_query_agent.executors.duckdb_executor import DuckDBExecutor
from huatai_query_agent.llm.client import case_deadline
from huatai_query_agent.llm.sql_generator import TextToSqlGenerator
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever

try:  # pragma: no cover - optional dependency in the current workspace
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when dependency is absent
    END = "__end__"
    START = "__start__"
    StateGraph = None
    LANGGRAPH_AVAILABLE = False


Node = Callable[[AgentState], dict[str, Any]]


def _merge(state: AgentState, update: dict[str, Any]) -> AgentState:
    merged: AgentState = dict(state)  # type: ignore[assignment]
    merged.update(update)
    return merged


def route_after_slot_check(state: AgentState) -> str:
    if state.get("case_timed_out"):
        return "human_review_or_explain"
    return "ask_clarification" if state.get("blocking_missing_slots") else "resolve_product"


def route_after_product_resolve(state: AgentState) -> str:
    if state.get("case_timed_out"):
        return "human_review_or_explain"
    product_ambiguity = state.get("ambiguities", {}).get("product")
    return "ask_clarification" if product_ambiguity else "plan_sql"


def route_after_sql_validation(state: AgentState) -> str:
    if state.get("case_timed_out"):
        return "human_review_or_explain"
    if state.get("llm_error") and not str(state.get("candidate_sql") or "").strip():
        return "human_review_or_explain"
    report = state.get("validation_report", {})
    if report.get("passed"):
        return "execute_sql"
    if int(state.get("retry_count", 0)) < int(state.get("max_retries", 2)):
        return "repair_sql"
    return "human_review_or_explain"


def route_after_execution(state: AgentState) -> str:
    if state.get("case_timed_out"):
        return "human_review_or_explain"
    result = state.get("execution_result", {})
    if result.get("success"):
        return "validate_result"
    if int(state.get("retry_count", 0)) < int(state.get("max_retries", 2)):
        return "repair_sql"
    return "human_review_or_explain"


def route_after_result_validation(state: AgentState) -> str:
    if state.get("case_timed_out"):
        return "human_review_or_explain"
    if state.get("result_check", {}).get("passed") and float(state.get("confidence", 0)) >= 0.5:
        return "render_answer"
    if int(state.get("retry_count", 0)) < int(state.get("max_retries", 2)):
        return "repair_sql"
    return "human_review_or_explain"


class QueryAgent:
    def __init__(
        self,
        *,
        db_path: Path | None = None,
        repo: DemoCaseRepository | None = None,
        retriever: HybridMetadataRetriever | None = None,
        llm_generator: TextToSqlGenerator | None = None,
        sql_mode: str = "demo",
        preview_limit: int = 20,
        use_langgraph: bool | None = None,
    ) -> None:
        if sql_mode not in {"demo", "llm"}:
            raise ValueError("sql_mode must be 'demo' or 'llm'.")
        self.repo = repo or DemoCaseRepository()
        self.retriever = retriever or HybridMetadataRetriever()
        self.sql_mode = sql_mode
        self.llm_generator = llm_generator or (TextToSqlGenerator.from_env() if sql_mode == "llm" else None)
        self.executor = DuckDBExecutor(db_path) if db_path else DuckDBExecutor()
        self.preview_limit = preview_limit
        self.use_langgraph = LANGGRAPH_AVAILABLE if use_langgraph is None else use_langgraph
        self._compiled_graph = self._compile_graph() if self.use_langgraph and LANGGRAPH_AVAILABLE else None
        self._thread_summaries: dict[str, dict[str, Any]] = {}

    def run(
        self,
        *,
        question: str = "",
        query_id: str | None = None,
        thread_id: str = "default",
        max_retries: int = 2,
        continue_with_assumptions: bool = False,
        request_context: dict[str, Any] | None = None,
        case_timeout_seconds: float | None = None,
    ) -> AgentState:
        state = self._new_run_state(
            question=question,
            query_id=query_id,
            thread_id=thread_id,
            max_retries=max_retries,
            continue_with_assumptions=continue_with_assumptions,
            request_context=request_context,
            case_timeout_seconds=case_timeout_seconds,
        )

        with case_deadline(case_timeout_seconds):
            if self._compiled_graph is not None:
                config = {"configurable": {"thread_id": thread_id}}
                result = self._compiled_graph.invoke(state, config=config)
            else:
                result = self._run_fallback(state)

        self._remember_thread_summary(result)
        return result

    def prepare(
        self,
        *,
        question: str = "",
        query_id: str | None = None,
        thread_id: str = "default",
        max_retries: int = 2,
        continue_with_assumptions: bool = False,
        request_context: dict[str, Any] | None = None,
        case_timeout_seconds: float | None = None,
    ) -> AgentState:
        """Generate and validate SQL without opening a database connection."""
        state = self._new_run_state(
            question=question,
            query_id=query_id,
            thread_id=thread_id,
            max_retries=max_retries,
            continue_with_assumptions=continue_with_assumptions,
            request_context=request_context,
            case_timeout_seconds=case_timeout_seconds,
        )
        with case_deadline(case_timeout_seconds):
            return self._prepare_fallback(state)

    def execute_prepared(
        self,
        prepared_state: AgentState,
        *,
        case_timeout_seconds: float | None = None,
    ) -> AgentState:
        """Revalidate and execute the exact SQL approved by the user."""
        state: AgentState = dict(prepared_state)  # type: ignore[assignment]
        timeout_seconds = (
            case_timeout_seconds
            if case_timeout_seconds is not None
            else float(state.get("case_timeout_seconds", 0.0) or 0.0) or None
        )
        nodes = self._nodes()
        state["next_action"] = "execute_sql"
        state = _merge(
            state,
            add_trace(
                state,
                "approve_sql",
                message="User approved the generated SQL for execution.",
            ),
        )

        with case_deadline(timeout_seconds):
            state = _merge(state, nodes["validate_sql"](state))
            if not state.get("validation_report", {}).get("passed"):
                state["next_action"] = "regenerate_sql"
                state = _merge(state, nodes["human_review_or_explain"](state))
                return self._persist_result(state, nodes)

            state = _merge(state, nodes["execute_sql"](state))
            if not state.get("execution_result", {}).get("success"):
                state["next_action"] = "regenerate_sql"
                state = _merge(state, nodes["human_review_or_explain"](state))
                return self._persist_result(state, nodes)

            state = _merge(state, nodes["validate_result"](state))
            if not state.get("result_check", {}).get("passed"):
                state["next_action"] = "regenerate_sql"
                state = _merge(state, nodes["human_review_or_explain"](state))
                return self._persist_result(state, nodes)

            state = _merge(state, nodes["render_answer"](state))
            state["next_action"] = "completed"
            return self._persist_result(state, nodes)

    def _new_run_state(
        self,
        *,
        question: str,
        query_id: str | None,
        thread_id: str,
        max_retries: int,
        continue_with_assumptions: bool,
        request_context: dict[str, Any] | None,
        case_timeout_seconds: float | None,
    ) -> AgentState:
        if query_id and not question:
            question = self.repo.get(query_id).question
        state = new_agent_state(
            question=question,
            thread_id=thread_id,
            max_retries=max_retries,
            continue_with_assumptions=continue_with_assumptions,
            request_context=request_context,
            case_timeout_seconds=case_timeout_seconds,
        )
        state["sql_mode"] = self.sql_mode
        if thread_id in self._thread_summaries:
            state["thread_summary"] = dict(self._thread_summaries[thread_id])
        if query_id:
            state["matched_query_id"] = query_id
        return state

    def _remember_thread_summary(self, state: AgentState) -> None:
        if state.get("thread_summary"):
            self._thread_summaries[state.get("thread_id", "default")] = dict(state["thread_summary"])

    def _persist_result(self, state: AgentState, nodes: dict[str, Node]) -> AgentState:
        result = _merge(state, nodes["persist_state"](state))
        self._remember_thread_summary(result)
        return result

    def _nodes(self) -> dict[str, Node]:
        return {
            "init_run": m1_nodes.init_run,
            "load_thread_context": m1_nodes.load_thread_context,
            "normalize_question": m1_nodes.normalize_question,
            "detect_followup": m1_nodes.detect_followup,
            "parse_intent": m1_nodes.parse_intent(
                self.repo,
                generator=self.llm_generator,
                sql_mode=self.sql_mode,
                allow_unmatched=self.sql_mode == "llm",
            ),
            "check_intent_slots": m1_nodes.check_intent_slots,
            "retrieve_metadata": m1_nodes.retrieve_metadata(self.repo, self.retriever),
            "fill_slots": m1_nodes.fill_slots(
                generator=self.llm_generator,
                sql_mode=self.sql_mode,
            ),
            "resolve_product": m1_nodes.resolve_product,
            "plan_sql": m1_nodes.plan_sql(
                generator=self.llm_generator,
                sql_mode=self.sql_mode,
            ),
            "generate_sql": m1_nodes.generate_sql(
                self.repo,
                generator=self.llm_generator,
                sql_mode=self.sql_mode,
            ),
            "validate_sql": m1_nodes.validate_sql,
            "execute_sql": m1_nodes.execute_sql(self.executor, preview_limit=self.preview_limit),
            "validate_result": m1_nodes.validate_result,
            "repair_sql": lambda state: m1_nodes.repair_sql(
                state,
                generator=self.llm_generator,
                sql_mode=self.sql_mode,
            ),
            "ask_clarification": m1_nodes.ask_clarification,
            "human_review_or_explain": m1_nodes.human_review_or_explain,
            "render_answer": m1_nodes.render_answer(
                generator=self.llm_generator,
                sql_mode=self.sql_mode,
            ),
            "persist_state": m1_nodes.persist_state,
        }

    def _run_fallback(self, state: AgentState) -> AgentState:
        nodes = self._nodes()
        for name in (
            "init_run",
            "load_thread_context",
            "normalize_question",
            "detect_followup",
            "parse_intent",
            "retrieve_metadata",
            "fill_slots",
            "check_intent_slots",
        ):
            state = _merge(state, nodes[name](state))

        if state.get("case_timed_out"):
            state = _merge(state, nodes["human_review_or_explain"](state))
            return _merge(state, nodes["persist_state"](state))

        if route_after_slot_check(state) == "ask_clarification":
            state = _merge(state, nodes["ask_clarification"](state))
            return _merge(state, nodes["persist_state"](state))

        state = _merge(state, nodes["resolve_product"](state))
        if route_after_product_resolve(state) == "ask_clarification":
            state = _merge(state, nodes["ask_clarification"](state))
            return _merge(state, nodes["persist_state"](state))

        for name in ("plan_sql", "generate_sql"):
            state = _merge(state, nodes[name](state))

        if state.get("llm_error") and not str(state.get("candidate_sql") or "").strip():
            state = _merge(state, nodes["human_review_or_explain"](state))
            return _merge(state, nodes["persist_state"](state))

        while True:
            state = _merge(state, nodes["validate_sql"](state))
            sql_route = route_after_sql_validation(state)
            if sql_route == "repair_sql":
                state = _merge(state, nodes["repair_sql"](state))
                continue
            if sql_route == "human_review_or_explain":
                state = _merge(state, nodes["human_review_or_explain"](state))
                return _merge(state, nodes["persist_state"](state))

            state = _merge(state, nodes["execute_sql"](state))
            execution_route = route_after_execution(state)
            if execution_route == "repair_sql":
                state = _merge(state, nodes["repair_sql"](state))
                continue
            if execution_route == "human_review_or_explain":
                state = _merge(state, nodes["human_review_or_explain"](state))
                return _merge(state, nodes["persist_state"](state))

            state = _merge(state, nodes["validate_result"](state))
            result_route = route_after_result_validation(state)
            if result_route == "render_answer":
                state = _merge(state, nodes["render_answer"](state))
                return _merge(state, nodes["persist_state"](state))
            if result_route == "human_review_or_explain":
                state = _merge(state, nodes["human_review_or_explain"](state))
                return _merge(state, nodes["persist_state"](state))
            state = _merge(state, nodes["repair_sql"](state))

    def _prepare_fallback(self, state: AgentState) -> AgentState:
        nodes = self._nodes()
        for name in (
            "init_run",
            "load_thread_context",
            "normalize_question",
            "detect_followup",
            "parse_intent",
            "retrieve_metadata",
            "fill_slots",
            "check_intent_slots",
        ):
            state = _merge(state, nodes[name](state))

        if state.get("case_timed_out"):
            state = _merge(state, nodes["human_review_or_explain"](state))
            return self._persist_result(state, nodes)

        if route_after_slot_check(state) == "ask_clarification":
            state = _merge(state, nodes["ask_clarification"](state))
            return self._persist_result(state, nodes)

        state = _merge(state, nodes["resolve_product"](state))
        if route_after_product_resolve(state) == "ask_clarification":
            state = _merge(state, nodes["ask_clarification"](state))
            return self._persist_result(state, nodes)

        for name in ("plan_sql", "generate_sql"):
            state = _merge(state, nodes[name](state))

        if state.get("llm_error") and not str(state.get("candidate_sql") or "").strip():
            state["next_action"] = "regenerate_sql"
            state = _merge(state, nodes["human_review_or_explain"](state))
            return self._persist_result(state, nodes)

        while True:
            state = _merge(state, nodes["validate_sql"](state))
            sql_route = route_after_sql_validation(state)
            if sql_route == "repair_sql":
                state = _merge(state, nodes["repair_sql"](state))
                continue
            if sql_route == "human_review_or_explain":
                state["next_action"] = "regenerate_sql"
                state = _merge(state, nodes["human_review_or_explain"](state))
                return self._persist_result(state, nodes)

            state["next_action"] = "execute_sql"
            return _merge(
                state,
                add_trace(
                    state,
                    "await_execution",
                    status="pending",
                    message="SQL passed validation and is waiting for user approval.",
                ),
            )

    def _compile_graph(self) -> Any:
        graph = StateGraph(AgentState)
        nodes = self._nodes()
        for name, node in nodes.items():
            graph.add_node(name, node)

        graph.add_edge(START, "init_run")
        graph.add_edge("init_run", "load_thread_context")
        graph.add_edge("load_thread_context", "normalize_question")
        graph.add_edge("normalize_question", "detect_followup")
        graph.add_edge("detect_followup", "parse_intent")
        graph.add_edge("parse_intent", "retrieve_metadata")
        graph.add_edge("retrieve_metadata", "fill_slots")
        graph.add_edge("fill_slots", "check_intent_slots")
        graph.add_conditional_edges("check_intent_slots", route_after_slot_check)
        graph.add_conditional_edges("resolve_product", route_after_product_resolve)
        graph.add_edge("plan_sql", "generate_sql")
        graph.add_edge("generate_sql", "validate_sql")
        graph.add_conditional_edges("validate_sql", route_after_sql_validation)
        graph.add_edge("repair_sql", "validate_sql")
        graph.add_conditional_edges("execute_sql", route_after_execution)
        graph.add_conditional_edges("validate_result", route_after_result_validation)
        graph.add_edge("ask_clarification", "persist_state")
        graph.add_edge("human_review_or_explain", "persist_state")
        graph.add_edge("render_answer", "persist_state")
        graph.add_edge("persist_state", END)
        return graph.compile()

    def close(self) -> None:
        close = getattr(self.retriever, "close", None)
        if callable(close):
            close()
