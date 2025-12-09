import re
from typing import Optional, Dict, Any, cast, List, Callable

from loguru import logger
from strands.agent import AgentResult
from strands.hooks import HookProvider
from strands.multiagent.graph import GraphState
from strands.session import SessionManager
from strands.tools.decorator import DecoratedFunctionTool
from strands.types.tools import AgentTool

from hatchify.common.domain.entity.agent_card import AgentCard
from hatchify.common.domain.entity.agent_node_spec import AgentNode
from hatchify.common.domain.entity.function_node_spec import FunctionNode
from hatchify.common.domain.entity.graph_spec import GraphSpec, ConditionRule, Edge
from hatchify.common.domain.enums.agent_category import AgentCategory
from hatchify.core.factory.agent_factory import create_agent_by_agent_card
from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.graph.graph_wrapper import GraphBuilderAdapter
from hatchify.core.graph.nodes.function_node import FunctionNodeWrapper


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
            execution_timeout: int = 600,
            session_manager: Optional[SessionManager] = None,
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
        self.session_manager = session_manager

    def build_graph(self, graph_spec: GraphSpec) -> Any:
        """根据 GraphSpec 构建可执行的 Strands Graph

        Args:
            graph_spec: Graph 规范对象（包含 agents, functions, edges 等）

        Returns:
            构建好的 Strands Graph 实例

        Raises:
            ValueError: 节点名称重复、边引用的节点不存在、工具不存在等错误
        """
        self._validate_unique_node_names(graph_spec)

        builder = GraphBuilderAdapter()

        created_nodes: Dict[str, Any] = {}

        # 步骤 1: 添加所有 Agent 节点
        for agent_node in graph_spec.agents:
            agent = self._create_agent_node(agent_node)
            builder.add_node(agent, agent_node.name)
            created_nodes[agent_node.name] = agent

        # 步骤 2: 添加所有 Function 节点
        for function_node_spec in graph_spec.functions:
            function_node = self._create_function_node(function_node_spec)
            builder.add_node(function_node, function_node_spec.name)
            created_nodes[function_node_spec.name] = function_node

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

            from_agent_spec = self._get_agent_spec_by_name(graph_spec, edge.from_node)

            condition = None

            # 优先使用自定义规则/JSONLogic 条件
            if edge.json_logic:
                condition = self._create_json_logic_condition(edge, from_agent_spec)
            elif edge.rules:
                condition = self._create_rules_condition(edge, from_agent_spec)
            elif from_agent_spec and from_agent_spec.category == AgentCategory.ROUTER:
                condition = self._create_router_condition(edge.from_node, edge.to_node)
            elif from_agent_spec and from_agent_spec.category == AgentCategory.ORCHESTRATOR:
                condition = self._create_orchestrator_condition(edge.from_node, edge.to_node)

            if condition:
                builder.add_edge(edge.from_node, edge.to_node, condition=condition)
            else:
                builder.add_edge(edge.from_node, edge.to_node)

        if graph_spec.entry_point not in created_nodes:
            raise ValueError(
                f"入口点 '{graph_spec.entry_point}' 不存在于 Graph 中。"
                f"可用节点: {list(created_nodes.keys())}"
            )

        builder.set_entry_point(graph_spec.entry_point)

        if self.hooks:
            builder.set_hook_providers(self.hooks)

        if self.execution_timeout:
            builder.set_execution_timeout(self.execution_timeout)

        if self.session_manager:
            builder.set_session_manager(self.session_manager)

        graph = builder.build()
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
    def _apply_json_logic(expr: Any, data: Dict[str, Any]) -> Any:
        """最小实现的 JSONLogic 解析，覆盖常用运算符"""

        def get_var(path: Any, default: Any = None) -> Any:
            if path is None:
                return data
            if not isinstance(path, str):
                return data.get(path, default)
            cur = data
            for key in path.split("."):
                if isinstance(cur, dict) and key in cur:
                    cur = cur[key]
                else:
                    return default
            return cur

        def resolve(val: Any) -> Any:
            if isinstance(val, dict):
                return eval_expr(val)
            if isinstance(val, list):
                return [resolve(v) for v in val]
            return val

        def eval_expr(obj: Any) -> Any:
            if not isinstance(obj, dict) or len(obj) != 1:
                return obj
            op, args = next(iter(obj.items()))
            if not isinstance(args, list):
                args = [args]

            if op in {"var"}:
                path = args[0] if args else None
                default = args[1] if len(args) > 1 else None
                return get_var(path, default)

            if op in {"==", "eq"}:
                a, b = resolve(args[0]), resolve(args[1])
                return a == b
            if op in {"!=", "neq"}:
                a, b = resolve(args[0]), resolve(args[1])
                return a != b
            if op in {">", "gt"}:
                a, b = resolve(args[0]), resolve(args[1])
                return a > b
            if op in {">=", "gte"}:
                a, b = resolve(args[0]), resolve(args[1])
                return a >= b
            if op in {"<", "lt"}:
                a, b = resolve(args[0]), resolve(args[1])
                return a < b
            if op in {"<=", "lte"}:
                a, b = resolve(args[0]), resolve(args[1])
                return a <= b
            if op in {"!", "not"}:
                return not bool(resolve(args[0]))
            if op == "and":
                return all(bool(resolve(arg)) for arg in args)
            if op == "or":
                return any(bool(resolve(arg)) for arg in args)
            if op == "in":
                a, b = resolve(args[0]), resolve(args[1])
                try:
                    return a in b
                except Exception as e:
                    logger.warning(f"{type(e).__name__}: {e}")
                    return False
            if op == "if":
                # args: [cond1, val1, cond2, val2, ..., else]
                pairs = list(zip(args[0::2], args[1::2]))
                for cond, val in pairs[:-1]:
                    if bool(resolve(cond)):
                        return resolve(val)
                if len(args) % 2 == 1:
                    # last default
                    return resolve(args[-1])
                # even number: evaluate last pair
                cond, val = pairs[-1]
                return resolve(val) if bool(resolve(cond)) else None
            if op == "regex":
                pattern = resolve(args[0])
                target = resolve(args[1])
                return (
                        isinstance(pattern, str)
                        and isinstance(target, str)
                        and re.search(pattern, target) is not None
                )

            # 未支持的运算符，直接返回 False
            logger.warning(f"JSONLogic 未支持的运算符 '{op}'")
            return False

        return eval_expr(expr)

    @staticmethod
    def _create_json_logic_condition(edge: Edge, from_agent_spec: Optional[AgentNode]) -> Callable[[GraphState], bool]:
        """使用 JSONLogic 表达式创建条件函数"""

        def condition(state: GraphState) -> bool:
            node_result = state.results.get(edge.from_node)
            if not node_result:
                return False

            agent_result = node_result.result
            if not isinstance(agent_result, AgentResult):
                return False

            structured_output = agent_result.structured_output
            if not structured_output:
                logger.warning(
                    f"节点 '{edge.from_node}' 没有 structured_output，无法应用 JSONLogic 路由"
                )
                return False

            output = structured_output.model_dump()

            # Orchestrator COMPLETE 信号直接终止
            if (
                    from_agent_spec
                    and from_agent_spec.category == AgentCategory.ORCHESTRATOR
                    and isinstance(output.get("next_node"), str)
                    and output.get("next_node").upper() == "COMPLETE"
            ):
                logger.info(
                    f"Orchestrator '{edge.from_node}' 发出 COMPLETE 信号，跳过边 {edge.from_node} -> {edge.to_node}"
                )
                return False

            try:
                decision = bool(DynamicGraphBuilder._apply_json_logic(edge.json_logic, output))
                if decision:
                    logger.debug(
                        f"JSONLogic 命中，from='{edge.from_node}' -> to='{edge.to_node}', expr={edge.json_logic}"
                    )
                return decision
            except Exception as exc:
                logger.warning(
                    f"JSONLogic 计算失败: expr={edge.json_logic}, output={output}",
                    exc_info=exc
                )
                return False

        return condition

    @staticmethod
    def _create_rules_condition(edge: Edge, from_agent_spec: Optional[AgentNode]) -> Callable[[GraphState], bool]:
        """根据 Edge.rules 构造条件函数，支持 and/or 组合"""
        logic = (edge.logic or "and").lower()
        if logic not in {"and", "or"}:
            logger.warning(f"未知逻辑运算符 '{edge.logic}'，使用 'and' 代替")
            logic = "and"

        def eval_rule(rule: ConditionRule, output: Dict[str, Any]) -> bool:
            left = output.get(rule.field)
            right = rule.value
            op = (rule.op or "").lower()

            handlers: Dict[str, Callable[[Any, Any], bool]] = {
                "==": lambda l, r: l == r,
                "eq": lambda l, r: l == r,
                "!=": lambda l, r: l != r,
                "neq": lambda l, r: l != r,
                ">": lambda l, r: l is not None and r is not None and l > r,
                "gt": lambda l, r: l is not None and r is not None and l > r,
                ">=": lambda l, r: l is not None and r is not None and l >= r,
                "gte": lambda l, r: l is not None and r is not None and l >= r,
                "<": lambda l, r: l is not None and r is not None and l < r,
                "lt": lambda l, r: l is not None and r is not None and l < r,
                "<=": lambda l, r: l is not None and r is not None and l <= r,
                "lte": lambda l, r: l is not None and r is not None and l <= r,
                "in": lambda l, r: r is not None and l in r,
                "not_in": lambda l, r: r is None or l not in r,
                "contains": lambda l, r: l is not None and r in l,
                "not_contains": lambda l, r: l is None or r not in l,
                "startswith": lambda l, r: isinstance(l, str) and isinstance(r, str) and l.startswith(r),
                "endswith": lambda l, r: isinstance(l, str) and isinstance(r, str) and l.endswith(r),
                "regex": lambda l, r: isinstance(l, str) and isinstance(r, str) and re.search(r, l) is not None,
                "regex_not": lambda l, r: isinstance(l, str) and isinstance(r, str) and re.search(r, l) is None,
                "between": lambda l, r: (
                        l is not None
                        and isinstance(r, (list, tuple))
                        and len(r) == 2
                        and r[0] <= l <= r[1]
                ),
                "is_true": lambda l, _: bool(l) is True,
                "is_false": lambda l, _: bool(l) is False,
                "exists": lambda l, _: l is not None,
                "not_exists": lambda l, _: l is None,
            }

            try:
                handler = handlers.get(op)
                if not handler:
                    logger.warning(f"不支持的比较运算符 '{rule.op}'")
                    return False
                return handler(left, right)
            except Exception as exc:
                logger.warning(
                    f"规则计算失败：field={rule.field}, op={rule.op}, value={rule.value}, left={left}",
                    exc_info=exc
                )
                return False

        def condition(state: GraphState) -> bool:
            node_result = state.results.get(edge.from_node)
            if not node_result:
                return False

            agent_result = node_result.result
            if not isinstance(agent_result, AgentResult):
                return False

            structured_output = agent_result.structured_output
            if not structured_output:
                logger.warning(
                    f"节点 '{edge.from_node}' 没有 structured_output，无法应用规则路由"
                )
                return False

            output = structured_output.model_dump()

            # Orchestrator COMPLETE 信号直接终止
            if (
                    from_agent_spec
                    and from_agent_spec.category == AgentCategory.ORCHESTRATOR
                    and isinstance(output.get("next_node"), str)
                    and output.get("next_node").upper() == "COMPLETE"
            ):
                logger.info(
                    f"Orchestrator '{edge.from_node}' 发出 COMPLETE 信号，跳过边 {edge.from_node} -> {edge.to_node}"
                )
                return False

            rules = edge.rules or []
            if not rules:
                return True

            results = [eval_rule(rule, output) for rule in rules]
            decision = any(results) if logic == "or" else all(results)

            if decision:
                logger.debug(
                    f"规则命中，from='{edge.from_node}' -> to='{edge.to_node}', logic={logic}, rules={rules}"
                )

            return decision

        return condition

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
            output = structured_output.model_dump()

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
            output = structured_output.model_dump()

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
