from typing import Optional, Dict, Any, cast, List, Callable

from loguru import logger
from strands.agent import AgentResult
from strands.hooks import HookProvider
from strands.multiagent import GraphBuilder
from strands.multiagent.graph import GraphState
from strands.tools.decorator import DecoratedFunctionTool
from strands.types.tools import AgentTool

from app.common.domain.entity.agent_card import AgentCard
from app.common.domain.entity.agent_node_spec import AgentNode
from app.common.domain.entity.function_node_spec import FunctionNode
from app.common.domain.entity.graph_spec import GraphSpec
from app.common.domain.enums.agent_category import AgentCategory
from app.core.factory.agent_factory import create_agent_by_agent_card
from app.core.factory.tool_factory import ToolRouter
from app.core.nodes.function_node import FunctionNodeWrapper


class DynamicGraphBuilder:
    """根据 GraphSpec 动态构建 Strands Graph

    将 LLM 生成的 GraphSpec（JSON 格式）转换为可执行的 Strands Graph。

    Example:
        ```python
        from app.core.manager.tool_manager import tool_router
        from app.core.manager.function_manager import function_router

        builder = DynamicGraphBuilder(
            tool_router=tool_router,
            function_router=function_router
        )

        graph = builder.build_graph(graph_spec)
        result = graph("输入任务")
        ```
    """

    def __init__(
            self,
            tool_router: ToolRouter[AgentTool],
            function_router: ToolRouter[DecoratedFunctionTool],
            hooks: Optional[List[HookProvider]] = None,
            execution_timeout: int = 600
    ):
        """初始化 DynamicGraphBuilder

        Args:
            tool_router: Agent 工具路由器（来自 tool_manager，接受所有 AgentTool）
            function_router: Function 工具路由器（来自 function_manager，只接受 DecoratedFunctionTool）
            hooks: 可选的 Hook Providers 列表
            execution_timeout: Graph 执行超时时间（秒），默认 600 秒（10 分钟）
        """
        self.tool_router = tool_router
        self.function_router = function_router
        self.hooks = hooks or []
        self.execution_timeout = execution_timeout

    def build_graph(self, graph_spec: GraphSpec) -> Any:
        """根据 GraphSpec 构建可执行的 Strands Graph

        Args:
            graph_spec: Graph 规范对象（包含 agents, functions, edges 等）

        Returns:
            构建好的 Strands Graph 实例

        Raises:
            ValueError: 节点名称重复、边引用的节点不存在、工具不存在等错误
        """
        logger.info(f"开始构建 Graph: {graph_spec.name}")

        # 验证节点名称唯一性
        self._validate_unique_node_names(graph_spec)

        # 创建 GraphBuilder
        builder = GraphBuilder()

        # 存储已创建的节点（用于验证边）
        created_nodes: Dict[str, Any] = {}

        # 步骤 1: 添加所有 Agent 节点
        for agent_node in graph_spec.agents:
            logger.info(f"创建 Agent 节点: {agent_node.name}")
            agent = self._create_agent_node(agent_node)
            builder.add_node(agent, agent_node.name)
            created_nodes[agent_node.name] = agent

        # 步骤 2: 添加所有 Function 节点
        for function_node_spec in graph_spec.functions:
            logger.info(f"创建 Function 节点: {function_node_spec.name}")
            function_node = self._create_function_node(function_node_spec)
            builder.add_node(function_node, function_node_spec.name)
            created_nodes[function_node_spec.name] = function_node

        # 步骤 3: 验证并添加所有边（支持 Router 条件边）
        for edge in graph_spec.edges:
            if edge.from_node not in created_nodes:
                raise ValueError(
                    f"边的起始节点 '{edge.from_node}' 不存在于 Graph 中。"
                    f"可用节点: {list(created_nodes.keys())}"
                )
            if edge.to_node not in created_nodes:
                raise ValueError(
                    f"边的目标节点 '{edge.to_node}' 不存在于 Graph 中。"
                    f"可用节点: {list(created_nodes.keys())}"
                )

            # 检查 from_node 是否是 Router/Orchestrator
            from_agent_spec = self._get_agent_spec_by_name(graph_spec, edge.from_node)

            if from_agent_spec and from_agent_spec.category == AgentCategory.ROUTER:
                # Router 节点：添加条件边
                condition = self._create_router_condition(edge.from_node, edge.to_node)
                logger.debug(f"添加 Router 条件边: {edge.from_node} -> {edge.to_node}")
                builder.add_edge(edge.from_node, edge.to_node, condition=condition)

            elif from_agent_spec and from_agent_spec.category == AgentCategory.ORCHESTRATOR:
                # Orchestrator 节点：添加条件边（支持 COMPLETE）
                condition = self._create_orchestrator_condition(edge.from_node, edge.to_node)
                logger.debug(f"添加 Orchestrator 条件边: {edge.from_node} -> {edge.to_node}")
                builder.add_edge(edge.from_node, edge.to_node, condition=condition)

            else:
                # General Agent/Function：添加静态边
                logger.debug(f"添加静态边: {edge.from_node} -> {edge.to_node}")
                builder.add_edge(edge.from_node, edge.to_node)

        # 步骤 4: 设置入口点
        if graph_spec.entry_point not in created_nodes:
            raise ValueError(
                f"入口点 '{graph_spec.entry_point}' 不存在于 Graph 中。"
                f"可用节点: {list(created_nodes.keys())}"
            )
        builder.set_entry_point(graph_spec.entry_point)
        logger.info(f"设置入口点: {graph_spec.entry_point}")

        # 步骤 5: 设置 hooks（如果有）
        if self.hooks:
            builder.set_hook_providers(self.hooks)
            logger.debug(f"设置 {len(self.hooks)} 个 Hook Providers")

        # 步骤 6: 设置执行超时
        builder.set_execution_timeout(self.execution_timeout)
        logger.debug(f"设置执行超时: {self.execution_timeout} 秒")

        # 步骤 7: 构建 Graph
        graph = builder.build()
        logger.info(f"Graph 构建完成: {graph_spec.name}")

        return graph

    def _create_agent_node(self, agent_node: AgentNode) -> Any:
        """从 AgentNode 创建 Agent 实例

        Args:
            agent_node: Agent 节点规范

        Returns:
            创建好的 Agent 实例

        Raises:
            KeyError: 工具不存在
        """
        # 步骤 1: 创建 AgentCard
        agent_card = AgentCard(
            name=agent_node.name,
            model=agent_node.model,
            instruction=agent_node.instruction,
            description=f"Agent for {agent_node.name}",
            tools=agent_node.tools
        )

        # 步骤 2: 获取 structured_output_model
        # 这是一个 @computed_field，会自动将 JSON Schema 转换为 BaseModel
        structured_output_model = agent_node.structured_output_model

        if structured_output_model:
            logger.debug(
                f"Agent '{agent_node.name}' 使用 structured_output_model: "
                f"{structured_output_model.__name__}"
            )

        # 步骤 3: 验证工具是否存在
        for tool_name in agent_node.tools:
            try:
                self.tool_router.get_tool(tool_name)
            except KeyError:
                available_tools = list(self.tool_router.get_all_tools().keys())
                raise ValueError(
                    f"Agent '{agent_node.name}' 引用的工具 '{tool_name}' 不存在。"
                    f"可用工具: {available_tools}"
                )

        # 步骤 4: 创建 Agent
        # 注意：不再需要 FilterReasoningContentHook，因为：
        # - GeminiModel 原生支持 reasoningContent
        # - OpenAIModel 和其他模型不会产生 reasoningContent
        agent = create_agent_by_agent_card(
            agent_card=agent_card,
            structured_output_model=structured_output_model,
            hooks=None
        )

        # 步骤 5: 如果是 Router 或 Orchestrator，注入完成指令
        if agent_node.category in [AgentCategory.ROUTER, AgentCategory.ORCHESTRATOR]:
            completion_instruction = (
                "\n\nIMPORTANT: When you determine that the workflow is complete "
                "and all necessary agents have been executed, "
                'output {"next_node": "COMPLETE"} to signal completion. '
                'Otherwise, continue routing to the appropriate next agent.'
            )

            # 注入到 Agent 的 system_prompt
            original_prompt = agent.system_prompt
            agent.system_prompt = original_prompt + completion_instruction

            logger.info(
                f"注入 COMPLETE 指令到 {agent_node.category.value} Agent: {agent_node.name}"
            )
            logger.debug(f"原始指令长度: {len(original_prompt)} 字符")
            logger.debug(f"注入后指令长度: {len(agent.system_prompt)} 字符")

        return agent

    def _create_function_node(self, function_node_spec: FunctionNode) -> FunctionNodeWrapper:
        """从 FunctionNodeSpec 创建 FunctionNodeWrapper 实例

        Args:
            function_node_spec: Function 节点规范

        Returns:
            创建好的 FunctionNodeWrapper 实例

        Raises:
            KeyError: Function 类型对应的工具不存在
        """
        # 步骤 1: 从 function_router 获取 tool
        try:
            tool = self.function_router.get_tool(function_node_spec.function_ref)
        except KeyError:
            available_functions = list(self.function_router.get_all_tools().keys())
            raise ValueError(
                f"Function '{function_node_spec.name}' 引用的类型 '{function_node_spec.function_ref}' 不存在。"
                f"可用 Function: {available_functions}"
            )

        # 步骤 2: 创建 FunctionNodeWrapper
        # 注意：不要在节点级别传递 hooks，hooks 应该在 GraphBuilder 级别设置
        function_node = FunctionNodeWrapper(
            tool=cast(DecoratedFunctionTool, tool),
            hooks=None,
            _id=function_node_spec.name  # 使用 function_node_spec.name 作为节点 ID
        )

        logger.debug(
            f"Function '{function_node_spec.name}' 使用工具: {function_node_spec.function_ref}"
        )

        return function_node

    @staticmethod
    def _validate_unique_node_names(graph_spec: GraphSpec) -> None:
        """验证所有节点名称是唯一的

        Args:
            graph_spec: Graph 规范对象

        Raises:
            ValueError: 节点名称重复
        """
        all_node_names = [
            node.name for node in graph_spec.agents
        ] + [
            node.name for node in graph_spec.functions
        ]

        duplicates = [name for name in all_node_names if all_node_names.count(name) > 1]

        if duplicates:
            raise ValueError(
                f"Graph 中存在重复的节点名称: {set(duplicates)}"
            )

        # 验证 graph_spec.nodes 是否与实际节点一致
        expected_nodes = set(all_node_names)
        declared_nodes = set(graph_spec.nodes)

        if expected_nodes != declared_nodes:
            missing = expected_nodes - declared_nodes
            extra = declared_nodes - expected_nodes
            error_msg = []
            if missing:
                error_msg.append(f"GraphSpec.nodes 缺少节点: {missing}")
            if extra:
                error_msg.append(f"GraphSpec.nodes 包含多余节点: {extra}")

            logger.warning("; ".join(error_msg))

    @staticmethod
    def _get_agent_spec_by_name(graph_spec: GraphSpec, node_name: str) -> Optional[AgentNode]:
        """根据节点名称获取 AgentNode Spec

        Args:
            graph_spec: Graph 规范对象
            node_name: 节点名称

        Returns:
            AgentNode 或 None（如果节点不是 Agent）
        """
        for agent_node in graph_spec.agents:
            if agent_node.name == node_name:
                return agent_node
        return None

    @staticmethod
    def _create_router_condition(router_name: str, target_node: str) -> Callable[[GraphState], bool]:
        """为 Router 创建条件函数

        条件函数读取 Router Agent 的 structured_output["next_node"]，
        判断是否等于目标节点名称。

        Args:
            router_name: Router 节点名称
            target_node: 目标节点名称

        Returns:
            条件函数，接受 GraphState，返回 bool
        """
        def condition(state: GraphState) -> bool:
            # 1. 获取 Router 的执行结果
            router_result = state.results.get(router_name)
            if not router_result:
                return False

            # 2. 提取 AgentResult
            agent_result = router_result.result
            if not isinstance(agent_result, AgentResult):
                return False

            # 3. 获取 structured_output
            structured_output = agent_result.structured_output
            if not structured_output:
                logger.warning(
                    f"Router '{router_name}' 没有 structured_output，无法路由"
                )
                return False

            # 4. 转换为 dict（可能是 Pydantic model）
            if hasattr(structured_output, 'model_dump'):
                output = structured_output.model_dump()
            else:
                output = structured_output

            # 5. 读取 next_node 字段
            next_node = output.get("next_node")

            if not next_node:
                logger.warning(
                    f"Router '{router_name}' 的 structured_output 缺少 'next_node' 字段"
                )
                return False

            # 6. 判断是否匹配目标节点
            is_match = next_node == target_node

            if is_match:
                logger.debug(
                    f"Router '{router_name}' 路由到 '{target_node}' (next_node={next_node})"
                )

            return is_match

        return condition

    @staticmethod
    def _create_orchestrator_condition(orch_name: str, target_node: str) -> Callable[[GraphState], bool]:
        """为 Orchestrator 创建条件函数

        与 Router 类似，但额外处理 COMPLETE 信号。

        Args:
            orch_name: Orchestrator 节点名称
            target_node: 目标节点名称

        Returns:
            条件函数，接受 GraphState，返回 bool
        """
        def condition(state: GraphState) -> bool:
            # 1. 获取 Orchestrator 的执行结果
            orch_result = state.results.get(orch_name)
            if not orch_result:
                return False

            # 2. 提取 AgentResult
            agent_result = orch_result.result
            if not isinstance(agent_result, AgentResult):
                return False

            # 3. 获取 structured_output
            structured_output = agent_result.structured_output
            if not structured_output:
                logger.warning(
                    f"Orchestrator '{orch_name}' 没有 structured_output，无法路由"
                )
                return False

            # 4. 转换为 dict（可能是 Pydantic model）
            if hasattr(structured_output, 'model_dump'):
                output = structured_output.model_dump()
            else:
                output = structured_output

            # 5. 读取 next_node 字段
            next_node = output.get("next_node")

            if not next_node:
                logger.warning(
                    f"Orchestrator '{orch_name}' 的 structured_output 缺少 'next_node' 字段"
                )
                return False

            # 6. 处理 COMPLETE 信号
            if next_node.upper() == "COMPLETE":
                logger.info(
                    f"Orchestrator '{orch_name}' 发出 COMPLETE 信号，工作流即将终止"
                )
                return False  # 所有条件边都返回 False，Graph 自然终止

            # 7. 判断是否匹配目标节点
            is_match = next_node == target_node

            if is_match:
                logger.debug(
                    f"Orchestrator '{orch_name}' 路由到 '{target_node}' (next_node={next_node})"
                )

            return is_match

        return condition
