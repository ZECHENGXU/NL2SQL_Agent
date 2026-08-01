from __future__ import annotations

import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from huatai_query_agent.web.server import DemoRuntime, _llm_connectivity_error


class WebLlmHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = object.__new__(DemoRuntime)
        self.runtime.llm_health_cache = None
        self.runtime.llm_health_lock = threading.Lock()
        self.settings = SimpleNamespace(
            base_url="https://api.example.test",
            model="sql-model",
        )

    def test_successful_model_check_is_cached(self) -> None:
        client = Mock()
        client.list_models.return_value = ["sql-model"]
        with (
            patch("huatai_query_agent.web.server.LlmSettings.from_env", return_value=self.settings),
            patch("huatai_query_agent.web.server.OpenAICompatibleChatClient", return_value=client),
        ):
            first = self.runtime.check_llm()
            second = self.runtime.check_llm()
            forced = self.runtime.check_llm(force=True)

        self.assertTrue(first["ok"])
        self.assertTrue(second["ok"])
        self.assertTrue(forced["ok"])
        self.assertEqual(2, client.list_models.call_count)

    def test_connection_error_names_network_permissions(self) -> None:
        message = _llm_connectivity_error(
            RuntimeError("Connection error."),
            "https://api.example.test",
        )

        self.assertIn("无法连接 LLM 服务", message)
        self.assertIn("网络权限", message)


if __name__ == "__main__":
    unittest.main()
