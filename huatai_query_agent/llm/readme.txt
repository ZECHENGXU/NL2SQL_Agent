本目录集中管理大模型连接、模型配置、提示词和 SQL 生成逻辑。

文件说明：
- client.py：OpenAI 兼容接口的模型客户端。
- config.py：LLM、超时和生成参数配置。
- prompts.py：意图识别、规划、SQL 生成和修复提示词。
- sql_generator.py：调用 LLM 生成和修复 SQL 的封装。
- check_connection.py：模型连接和健康检查脚本。
- __init__.py：LLM 子包初始化文件。
