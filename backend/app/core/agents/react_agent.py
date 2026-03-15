"""
React Agent - LangGraph based ReAct agent with streaming support
"""
import time
from loguru import logger
from typing import List, Dict, Any, AsyncGenerator, NotRequired, TypedDict, Union, Optional
from langchain_core.language_models import BaseChatModel
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.types import StreamWriter
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, AIMessageChunk, AIMessage, HumanMessage


# Define stream event payload structure
class StreamEventData(TypedDict, total=False):
    """Stream event data structure for LangGraph 'custom' stream_mode"""
    title: str
    status: str  # e.g., "START", "END", "ERROR"
    message: str


# Define full stream output structure
class StreamOutput(TypedDict):
    type: str  # e.g., "event", "response_chunk"
    timestamp: float
    data: Union[StreamEventData, Dict[str, str]]


# Optimized state type
class ReactAgentState(MessagesState):
    """LangGraph state, inherits from MessagesState"""
    tool_call_count: NotRequired[int]
    model_call_count: NotRequired[int]


# --- Core ReactAgent Class ---

class ReactAgent:
    """
    A ReAct agent based on LangGraph.
    Supports streaming output and sends custom events during tool execution and model reasoning.
    """

    def __init__(
        self,
        model: BaseChatModel,
        system_prompt: Optional[str] = None,
        tools: List[BaseTool] = []
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools

        # LangGraph instance
        self.graph: Optional[StateGraph] = None

    def _wrap_stream_output(self, type: str, data: Dict[str, Any]) -> StreamOutput:
        """
        Unified stream output wrapper.
        """
        return {
            "type": type,
            "timestamp": time.time(),
            "data": data
        }

    async def _init_agent(self):
        """Lazy initialization of LangGraph."""
        if self.graph is None:
            self.graph = await self._setup_react_graph()

    def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool instance by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    # --- LangGraph Node Definition and Graph Setup ---

    async def _setup_react_graph(self):
        """Set up the agent graph with nodes and edges."""

        workflow = StateGraph(ReactAgentState)

        # Node definition
        workflow.add_node("call_model", self._call_model_node)
        workflow.add_node("execute_tool", self._execute_tool_node)

        # Edges and conditional edges
        workflow.add_edge(START, "call_model")
        workflow.add_conditional_edges("call_model", self._should_continue)
        workflow.add_edge("execute_tool", "call_model")  # Tool result -> model reasoning again

        return workflow.compile()

    # --- LangGraph Node Functions ---

    async def _should_continue(self, state: ReactAgentState) -> Union[str, Any]:
        """Conditional edge: determine if tool needs to be executed."""
        last_message = state["messages"][-1]

        # If model has tool_calls, continue to execute tool
        if last_message.tool_calls:
            return "execute_tool"

        return END

    async def _call_model_node(
        self,
        state: ReactAgentState,
        writer: StreamWriter
    ) -> Dict[str, List[BaseMessage]]:
        """
        Call the model to decide if tools are needed, and send tool selection events.
        """
        is_first_call = state.get("tool_call_count", 0) == 0

        # Status message
        select_tool_message = (
            "开始分析用户问题" if is_first_call else
            f"继续分析（已调用工具 {state['tool_call_count']} 次）"
        )

        # Send tool analysis start event
        writer(self._wrap_stream_output("event", {
            "title": select_tool_message,
            "status": "START",
            "message": "正在分析需要使用的工具..."
        }))

        # Bind tools and invoke model
        tool_invocation_model = self.model.bind_tools(self.tools)
        response: AIMessage = await tool_invocation_model.ainvoke(state["messages"])

        # Check if there are tools to call
        if response.tool_calls:
            tool_call_names = sorted(list(set(tool_call["name"] for tool_call in response.tool_calls)))
            # Send tool selection complete event
            writer(self._wrap_stream_output("event", {
                "title": select_tool_message,
                "status": "END",
                "message": f"将调用工具: {', '.join(tool_call_names)}"
            }))

            state["messages"].append(response)
            return {"messages": state["messages"]}
        else:
            # Send no tool available event
            writer(self._wrap_stream_output("event", {
                "title": select_tool_message,
                "status": "END",
                "message": "模型选择直接回复"
            }))

            # Add final model response to messages, LangGraph will end via END
            state["messages"].append(response)
            return {"messages": state["messages"]}

    async def _execute_tool_node(
        self,
        state: ReactAgentState,
        writer: StreamWriter
    ) -> Dict[str, Any]:
        """Execute tools and return results to the model."""
        last_message = state["messages"][-1]
        tool_calls = last_message.tool_calls
        tool_messages: List[BaseMessage] = []

        if not tool_calls:
            logger.warning("Execute tool node reached without tool calls.")
            return {"messages": state["messages"], "tool_call_count": state.get("tool_call_count", 0)}

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            tool_title = f"执行工具: {tool_name}"

            try:
                # Send tool execution start event
                writer(self._wrap_stream_output("event", {
                    "status": "START",
                    "title": tool_title,
                    "message": f"参数: {tool_args}"
                }))

                current_tool = self.get_tool_by_name(tool_name)

                if current_tool is None:
                    tool_result = f"Error: Tool '{tool_name}' not found."
                    raise ValueError(tool_result)

                # Execute tool - use ainvoke for both sync and async tools
                tool_result = await current_tool.ainvoke(tool_args)

                # Ensure result is string or convertible to string
                tool_result_str = str(tool_result)

                # Send tool execution complete event
                writer(self._wrap_stream_output("event", {
                    "status": "END",
                    "title": tool_title,
                    "message": f"执行完成"
                }))

                tool_messages.append(
                    ToolMessage(content=tool_result_str, name=tool_name, tool_call_id=tool_call_id)
                )
                logger.info(f"Tool {tool_name} executed. Args: {tool_args}, Result: {tool_result_str[:100]}...")

            except Exception as err:
                error_message = f"执行工具 {tool_name} 失败: {str(err)}"
                # Send tool execution error event
                writer(self._wrap_stream_output("event", {
                    "status": "ERROR",
                    "title": tool_title,
                    "message": error_message
                }))

                logger.error(f"Execute Tool {tool_name} Error: {str(err)}")
                tool_messages.append(
                    ToolMessage(content=error_message, name=tool_name, tool_call_id=tool_call_id)
                )

        state["messages"].extend(tool_messages)
        new_tool_count = state.get("tool_call_count", 0) + 1

        return {"messages": state["messages"], "tool_call_count": new_tool_count}

    # --- Main Invocation Method ---

    async def astream(
        self,
        messages: List[BaseMessage]
    ) -> AsyncGenerator[StreamOutput, None]:
        """Main streaming invocation method."""

        # Message preprocessing (System Prompt)
        if not messages or not isinstance(messages[-1], (HumanMessage, AIMessage, ToolMessage)):
            logger.warning("Input messages list is empty or last message type is unexpected.")
            return

        if self.system_prompt and not any(isinstance(m, SystemMessage) for m in messages):
            messages.insert(0, SystemMessage(self.system_prompt))

        # Initialize Graph
        await self._init_agent()

        response_content = ""
        initial_state = {"messages": messages, "tool_call_count": 0, "model_call_count": 0}

        try:
            # Use 'messages' mode for response content, 'custom' mode for events
            async for typ, token in self.graph.astream(
                input=initial_state,
                stream_mode=["messages", "custom"],
            ):
                # Handle custom events
                if typ == "custom":
                    yield self._wrap_stream_output("event", token)
                # Handle AIMessageChunk (model content streaming)
                if typ == "messages" and isinstance(token[0], AIMessageChunk):
                    response_content += token[0].content
                    yield self._wrap_stream_output("response_chunk", {
                        "chunk": token[0].content,
                        "accumulated": response_content
                    })

        # Error handling
        except Exception as err:
            logger.error(f"Agent Execution Error: {err}")

            # If empty response, send error message
            if not response_content:
                error_chunk = "处理您的请求时发生错误，请稍后重试。"
                yield self._wrap_stream_output("response_chunk", {
                    "chunk": error_chunk,
                    "accumulated": response_content + error_chunk
                })
