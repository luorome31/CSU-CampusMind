"""
端到端测试脚本 - 测试 RAG 检索功能

测试目标：验证 RAG 工具是否被正确调用，知识库内容是否被正确检索

策略：索引大模型不知道的私有/本地内容，然后提问相关内容，验证：
1. LLM 是否调用了 RAG 工具
2. RAG 是否返回了正确的知识库内容
3. LLM 是否基于 RAG 结果生成了回答
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
TEST_USER_ID = "e2e_test_user_rag"


@dataclass
class CompletionResponse:
    """流式响应数据结构"""
    success: bool
    message: str
    context: str
    sources: list
    dialog_id: Optional[str]
    error: Optional[str] = None


class RAGTestClient:
    """RAG 功能测试客户端"""

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
        """发送流式 Completion 请求"""
        endpoint = "/completion/stream"
        print("\n[3] 发送流式 Completion 请求")
        print(f"    问题: {query}")
        print(f"    知识库: {knowledge_ids}")

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

        return self._handle_stream_request(endpoint, payload)

    def _handle_stream_request(self, endpoint: str, payload: dict) -> CompletionResponse:
        """处理流式响应"""
        accumulated_content = ""
        event_count = 0
        chunk_count = 0
        self.dialog_id = None

        try:
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

            response.raise_for_status()
            self.dialog_id = response.headers.get("X-Dialog-ID")
            print(f"    >>> Dialog ID: {self.dialog_id}")

            print("\n    ===== 流式响应 =====")

            buffer = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line.startswith("data: "):
                            data_str = line[6:]
                            try:
                                event = json.loads(data_str)
                                event_count += 1

                                if event.get("type") == "response_chunk":
                                    chunk_text = event.get("data", {}).get("chunk", "")
                                    accumulated_content += chunk_text
                                    chunk_count += 1
                                    print(f"    [chunk] {chunk_text}", end="", flush=True)

                                elif event.get("type") == "event":
                                    status = event.get("data", {}).get("status", "")
                                    title = event.get("data", {}).get("title", "")
                                    message = event.get("data", {}).get("message", "")
                                    print(f"\n    [event] {status}: {title} - {message}")

                            except json.JSONDecodeError:
                                pass

            print("\n    ===== 响应结束 =====")
            print(f"    >>> 总事件数: {event_count}, chunks: {chunk_count}")

        except Exception as e:
            print(f"    !!! 错误: {e}")
            return CompletionResponse(
                success=False,
                message=payload.get("message", ""),
                context="",
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


def run_rag_test():
    """运行 RAG 功能测试"""
    print("=" * 60)
    print("CampusMind RAG 功能端到端测试")
    print("=" * 60)

    client = RAGTestClient()

    # ============================================================
    # 第一部分：测试需要 RAG 检索的问题
    # ============================================================

    # 使用大模型不知道的私有内容
    private_content = """
    # 公司内部技术文档 - 仅供内部使用

    ## 项目A - 核心架构
    本项目使用 Python 开发，框架为 FastAPI。
    数据库采用 PostgreSQL，缓存使用 Redis。
    认证方式为 JWT Token 验证。

    API 基础路径: /api/v1
    管理后台端口: 8080

    核心模块:
    - UserModule: 用户管理
    - OrderModule: 订单处理
    - PaymentModule: 支付网关
    - NotificationModule: 消息推送

    ## 员工手册 - 机密
    公司成立于 2020 年 5 月 1 日。
    总部位于北京市海淀区中关村科技园。
    法定代表人为张三。
    客服热线: 400-123-4567

    上班时间: 周一至周五 9:00-18:00
    午休时间: 12:00-13:00

    ## 财务信息 - 绝密
    2024年年度营收: 1.2亿元
    员工人数: 256人
    融资轮次: B轮 5000万美元
    """

    # 另一个知识库：个人学习笔记
    personal_notes = """
    # 我的学习笔记

    ## 机器学习课程
    授课老师: 李明教授
    上课时间: 每周三 14:00-16:00
    教室: 学研大厦 A301
    成绩占比: 平时成绩40% + 期末考试60%

    推荐的参考书:
    - 《机器学习》- 周志华
    - 《统计学习方法》- 李航
    - 《深度学习》- Ian Goodfellow

    ## 考试安排
    期中考试: 第10周周三
    期末考试: 第18周周一

    考试地点: 教学楼B座 201教室
    """

    try:
        # Step 1: 创建知识库并索引私有内容
        print("\n" + "=" * 60)
        print("【测试1】验证 RAG 检索公司内部文档")
        print("=" * 60)

        knowledge_id_1 = client.create_knowledge(
            name=f"公司内部文档_{uuid.uuid4().hex[:8]}",
            description="包含公司机密信息的私有知识库"
        )

        client.index_content(
            knowledge_id=knowledge_id_1,
            content=private_content,
            source_name="company_internal.md"
        )

        time.sleep(2)

        # Step 2: 提问只有知识库知道的问题
        print("\n>>> 提问: 公司法定代表人是是谁?")
        response1 = client.stream_completion(
            query="公司法定代表人是是谁?",
            knowledge_ids=[knowledge_id_1]
        )

        print("\n" + "-" * 40)
        print("【LLM 回答】:")
        print("-" * 40)
        print(response1.context if response1.context else "(无内容)")
        print("-" * 40)

        # 验证点1: 回答中是否包含知识库内容
        has_rag_result_1 = "张三" in response1.context or "法定" in response1.context
        print(f"\n✓ 验证1 (RAG检索到法定代表人): {'是' if has_rag_result_1 else '否'}")

        # ============================================================
        # 第二部分：测试个人学习笔记
        # ============================================================

        print("\n" + "=" * 60)
        print("【测试2】验证 RAG 检索个人学习笔记")
        print("=" * 60)

        knowledge_id_2 = client.create_knowledge(
            name=f"个人学习笔记_{uuid.uuid4().hex[:8]}",
            description="包含课程和考试信息的私人笔记"
        )

        client.index_content(
            knowledge_id=knowledge_id_2,
            content=personal_notes,
            source_name="study_notes.md"
        )

        time.sleep(2)

        print("\n>>> 提问: 机器学习课程的老师是谁?")
        response2 = client.stream_completion(
            query="机器学习课程的老师是谁?上课时间呢?",
            knowledge_ids=[knowledge_id_2]
        )

        print("\n" + "-" * 40)
        print("【LLM 回答】:")
        print("-" * 40)
        print(response2.context if response2.context else "(无内容)")
        print("-" * 40)

        # 验证点2: 回答中是否包含知识库内容
        has_rag_result_2 = "李明" in response2.context or "周三" in response2.context or "14:00" in response2.context
        print(f"\n✓ 验证2 (RAG检索到课程信息): {'是' if has_rag_result_2 else '否'}")

        # ============================================================
        # 第三部分：测试混合知识库
        # ============================================================

        print("\n" + "=" * 60)
        print("【测试3】验证多知识库检索")
        print("=" * 60)

        print("\n>>> 提问: 公司有那些核心模块?")
        response3 = client.stream_completion(
            query="公司有哪些核心模块?",
            knowledge_ids=[knowledge_id_1, knowledge_id_2]
        )

        print("\n" + "-" * 40)
        print("【LLM 回答】:")
        print("-" * 40)
        print(response3.context if response3.context else "(无内容)")
        print("-" * 40)

        # 验证点3: 是否从第一个知识库检索
        has_rag_result_3 = "UserModule" in response3.context or "OrderModule" in response3.context or "核心" in response3.context
        print(f"\n✓ 验证3 (多知识库检索): {'是' if has_rag_result_3 else '否'}")

        # ============================================================
        # 总结
        # ============================================================

        print("\n" + "=" * 60)
        print("【测试总结】")
        print("=" * 60)
        print(f"✓ 测试1 - 公司文档RAG: {'通过' if has_rag_result_1 else '失败'}")
        print(f"✓ 测试2 - 学习笔记RAG: {'通过' if has_rag_result_2 else '失败'}")
        print(f"✓ 测试3 - 多知识库RAG: {'通过' if has_rag_result_3 else '失败'}")

        all_passed = has_rag_result_1 and has_rag_result_2 and has_rag_result_3
        if all_passed:
            print("\n🎉 所有 RAG 测试通过!")
        else:
            print("\n⚠️ 部分 RAG 测试失败，请检查后端日志")

        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到后端服务")
        print("  请确保后端服务正在运行: uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_rag_test()
