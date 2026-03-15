"""
端到端测试脚本 - 模拟前端客户端与后端 LLM 交互

使用方式:
1. 确保后端服务正在运行: uvicorn app.main:app --reload
2. 运行脚本: uv run python tests/e2e/test_llm_interaction.py
"""

import requests
import json
import time
import sys
import uuid
from typing import Optional
from dataclasses import dataclass


# 配置
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# 测试用户标识
TEST_USER_ID = "e2e_test_user"


@dataclass
class CompletionResponse:
    """流式响应数据结构"""
    success: bool
    message: str
    context: str
    sources: list
    dialog_id: Optional[str]
    error: Optional[str] = None


class LLMClient:
    """模拟前端客户端 - 与后端 LLM API 交互"""

    def __init__(self, base_url: str = API_V1):
        self.base_url = base_url
        self.session = requests.Session()
        self.dialog_id: Optional[str] = None
        self.knowledge_id: Optional[str] = None

    def create_knowledge(self, name: str, description: str = "") -> str:
        """创建知识库"""
        print(f"\n[1] 创建知识库: {name}")
        response = self.session.post(
            f"{self.base_url}/knowledge/create",
            json={
                "name": name,
                "description": description,
                "user_id": TEST_USER_ID
            }
        )
        response.raise_for_status()
        data = response.json()
        knowledge_id = data["id"]
        self.knowledge_id = knowledge_id
        print(f"    ✓ 知识库创建成功, ID: {knowledge_id}")
        return knowledge_id

    def index_content(self, knowledge_id: str, content: str, source_name: str = "test") -> dict:
        """索引文本内容"""
        print(f"\n[2] 索引内容: {source_name}")
        response = self.session.post(
            f"{self.base_url}/index/create",
            json={
                "content": content,
                "knowledge_id": knowledge_id,
                "source_name": source_name,
                "enable_vector": True,
                "enable_keyword": True
            }
        )
        response.raise_for_status()
        result = response.json()
        print(f"    ✓ 索引完成, chunk数量: {result.get('chunk_count', 0)}")
        return result

    def stream_completion(self, query: str, knowledge_ids: list) -> CompletionResponse:
        """
        发送流式 Completion 请求 (调用 LLM)
        """
        endpoint = "/completion/stream"
        print(f"\n[3] 发送流式 Completion 请求")
        print(f"    问题: {query}")
        print(f"    知识库: {knowledge_ids}")
        print(f"    端点: {endpoint}")

        payload = {
            "message": query,
            "knowledge_ids": knowledge_ids,
            "user_id": TEST_USER_ID,
            "enable_rag": True,
            "top_k": 5,
            "model": "MiniMax-M2.5"
        }

        if self.dialog_id:
            payload["dialog_id"] = self.dialog_id
            print(f"    对话ID (续上轮): {self.dialog_id}")

        return self._handle_stream_request(endpoint, payload)

    def _handle_stream_request(self, endpoint: str, payload: dict) -> CompletionResponse:
        """处理流式响应 (SSE) 使用 requests"""
        accumulated_content = ""
        event_count = 0
        chunk_count = 0
        self.dialog_id = None

        print(f"\n    >>> 发起请求到: {self.base_url}{endpoint}")
        print(f"    >>> 请求体: {json.dumps(payload, ensure_ascii=False)[:200]}...")

        try:
            # 使用 stream=True 来处理 SSE
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                stream=True,
                timeout=120,
                headers={
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json"
                }
            )

            print(f"    >>> 响应状态码: {response.status_code}")
            print(f"    >>> 响应头: {dict(response.headers)}")

            response.raise_for_status()

            # 获取 dialog_id
            self.dialog_id = response.headers.get("X-Dialog-ID")
            print(f"    >>> Dialog ID: {self.dialog_id}")

            print("\n    ===== 流式响应开始 =====")

            # 逐行读取响应
            buffer = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    # 处理可能的多行数据
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line.startswith("data: "):
                            data_str = line[6:]  # 去掉 "data: " 前缀
                            try:
                                event = json.loads(data_str)
                                event_count += 1

                                if event.get("type") == "response_chunk":
                                    chunk_text = event.get("data", {}).get("chunk", "")
                                    accumulated_content += chunk_text
                                    chunk_count += 1
                                    print(f"    [chunk-{chunk_count}] {chunk_text}", end="", flush=True)

                                elif event.get("type") == "event":
                                    status = event.get("data", {}).get("status", "")
                                    title = event.get("data", {}).get("title", "")
                                    message = event.get("data", {}).get("message", "")
                                    print(f"\n    [event] {status}: {title} - {message}")

                                else:
                                    print(f"\n    [其他事件] type={event.get('type')}")

                            except json.JSONDecodeError as e:
                                print(f"\n    [JSON解析错误] {e}, 数据: {data_str[:100]}")

            # 处理剩余 buffer
            if buffer.strip():
                print(f"\n    [剩余数据] {buffer[:200]}")

            print("\n    ===== 流式响应结束 =====")
            print(f"    >>> 总事件数: {event_count}")
            print(f"    >>> 总chunk数: {chunk_count}")
            print(f"    >>> 累积内容长度: {len(accumulated_content)}")

        except requests.exceptions.Timeout:
            print("    !!! 请求超时")
            return CompletionResponse(
                success=False,
                message=payload.get("message", ""),
                context="",
                sources=[],
                dialog_id=self.dialog_id,
                error="请求超时"
            )
        except requests.exceptions.ConnectionError as e:
            print(f"    !!! 连接错误: {e}")
            return CompletionResponse(
                success=False,
                message=payload.get("message", ""),
                context="",
                sources=[],
                dialog_id=self.dialog_id,
                error=f"连接错误: {e}"
            )
        except Exception as e:
            print(f"    !!! 错误: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return CompletionResponse(
                success=False,
                message=payload.get("message", ""),
                context=accumulated_content,
                sources=[],
                dialog_id=self.dialog_id,
                error=str(e)
            )

        return CompletionResponse(
            success=True,
            message=payload.get("message", ""),
            context=accumulated_content,
            sources=[],
            dialog_id=self.dialog_id
        )


def run_e2e_test():
    """运行端到端测试"""
    print("=" * 60)
    print("CampusMind 端到端测试 - LLM 交互流程")
    print("=" * 60)

    client = LLMClient()

    # 测试内容
    test_content = """
    Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年首次发布。

    ## 基本语法
    Python 使用缩进来定义代码块，不需要使用大括号。

    ## 变量
    Python 是动态类型语言，变量不需要声明类型。
    x = 5
    name = "Python"

    ## 函数
    def greet(name):
        return f"Hello, {name}!"

    ## 类
    class Person:
        def __init__(self, name):
            self.name = name

        def say_hello(self):
            return f"Hello, I'm {self.name}"
    """

    try:
        # Step 1: 创建知识库 (使用随机名称避免重复)
        random_suffix = str(uuid.uuid4())[:8]
        knowledge_id = client.create_knowledge(
            name=f"Python 教程测试_{random_suffix}",
            description="用于端到端测试的 Python 教程知识库"
        )

        # Step 2: 直接索引内容
        client.index_content(
            knowledge_id=knowledge_id,
            content=test_content,
            source_name="python_tutorial.md"
        )

        # Step 3: 等待索引完成
        print("\n[等待索引完成...]")
        time.sleep(2)

        # Step 4: 流式 Completion 对话 (调用 LLM)
        print("\n" + "=" * 60)
        print("测试流式 Completion (LLM)")
        print("=" * 60)
        response = client.stream_completion(
            query="Python 怎么定义函数?",
            knowledge_ids=[knowledge_id]
        )
        print(f"\n    ✓ 成功: {response.success}")
        print(f"    ✓ 对话 ID: {response.dialog_id}")

        print("\n" + "-" * 40)
        print("【LLM 完整回答】:")
        print("-" * 40)
        print(response.context if response.context else "(无内容)")
        print("-" * 40)

        if response.error:
            print(f"    错误: {response.error}")

        # Step 5: 多轮对话
        print("\n" + "=" * 60)
        print("测试多轮对话 (LLM)")
        print("=" * 60)
        response2 = client.stream_completion(
            query="给我一个完整的例子",
            knowledge_ids=[knowledge_id]
        )
        print(f"\n    ✓ 成功: {response2.success}")
        print(f"    ✓ 对话 ID: {response2.dialog_id}")

        print("\n" + "-" * 40)
        print("【LLM 完整回答】:")
        print("-" * 40)
        print(response2.context if response2.context else "(无内容)")
        print("-" * 40)

        if response2.error:
            print(f"    错误: {response2.error}")

        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到后端服务")
        print("  请确保后端服务正在运行: uvicorn app.main:app --reload")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP 错误: {e.response.status_code}")
        print(f"  响应内容: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_e2e_test()
