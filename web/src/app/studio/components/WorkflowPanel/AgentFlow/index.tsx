import {
	addEdge,
	ControlButton,
	Controls,
	type Edge,
	MarkerType,
	MiniMap,
	type Node,
	ReactFlow,
	useEdgesState,
	useNodesState,
} from "@xyflow/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useTheme } from "@/hooks/useTheme";
import AgentNode from "./AgentNode";
import ProcessorNode from "./ProcessorsNode";

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];
import "@xyflow/react/dist/style.css";
import { ScreenFullview2Off, ScreenFullview2On } from "@hatchify/icons";
import type { Connection } from "@xyflow/react";
import { useWorkflowDetail } from "@/hooks/useWorkflow";
import { computeDAGPositions } from "./layout";

const nodeTypes = {
	agentNode: AgentNode,
	processorNode: ProcessorNode,
};

export default function AgentFlow({
	isFullscreen,
	setIsFullscreen,
}: {
	isFullscreen: boolean;
	setIsFullscreen: (isFullscreen: boolean) => void;
}) {
	const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
	const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

	const { workflow } = useWorkflowDetail({ enabled: true });

	const [pollResponse, _setPollResponse] = useState<any | null>(null);

	const running = pollResponse?.status === "running";
	const _steps = pollResponse?.full_trace?.steps ?? [];

	useEffect(() => {
		if (!workflow) return;

		const agents = workflow?.current_spec?.agents || [];

		const edges = workflow?.current_spec?.edges || [];
		const _entry_point = workflow?.current_spec?.entry_point || "";
		const _nodes = workflow?.current_spec?.nodes || [];

		// just get agent names
		const agentNames = new Set(agents.map((a) => a.name));
		const orchestrationEdges = edges.filter(
			(e: any) => agentNames.has(e.from_node) && agentNames.has(e.to_node),
		);

		const flowEdges: Edge[] = orchestrationEdges.map((edge, index: number) => ({
			id: `e${index}`,
			source: edge.from_node,
			target: edge.to_node,
			type: "default",
			animated: false,
			style: {},
			markerEnd: { type: MarkerType.Arrow },
		}));

		// based on DAG simple hierarchical layout (no third-party dependency)
		const nodeIds = Array.from(agentNames);
		const incomingSet = new Set<string>();
		const outgoingSet = new Set<string>();
		for (const e of flowEdges) {
			incomingSet.add(e.target);
			outgoingSet.add(e.source);
		}
		const idToPosition = computeDAGPositions(
			nodeIds,
			orchestrationEdges.map((e: any) => ({
				from_node: e.from_node,
				to_node: e.to_node,
			})),
		);

		// generate nodes (with layout position), here we don't bind execution_trace, to avoid position refresh when polling
		const agentNodes: Node[] = agents.map((agent) => ({
			id: agent.name,
			name: agent.name,
			type: "agentNode",
			position: idToPosition.get(agent.name) || { x: 0, y: 200 },
			data: {
				...agent,
				hasIncomingConnection: incomingSet.has(agent.name),
				hasOutgoingConnection: outgoingSet.has(agent.name),
			},
		}));

		// const processorsNodes: Node[] = workflow.processors.map((processor, index) => ({
		//   id: processor.instance_name,
		//   name: processor.instance_name,
		//   type: 'processorNode',
		//   data: processor,
		//   position: { x: index * 100, y: 0 },
		// }))

		setNodes([...agentNodes]);
		setEdges(flowEdges);
	}, [setNodes, setEdges, workflow]);

	// only update node data when execution changes, not change position
	// useEffect(() => {
	//   if (!steps?.length) return

	//   const stepByAgent = new Map(steps.map((s) => [s.agent_name, s] as const))

	//   setNodes((prev) =>
	//     prev.map((n) => {
	//       const nextTrace = stepByAgent.get((n.data as any).name) as ExecutionStep | undefined
	//       const prevTrace = (n.data as any).execution_trace as ExecutionStep | undefined

	//       const unchanged =
	//         prevTrace?.end_time === nextTrace?.end_time && prevTrace?.status === nextTrace?.status && prevTrace?.output_data === nextTrace?.output_data && prevTrace?.error === nextTrace?.error
	//       if (unchanged) return n

	//       return {
	//         ...n,
	//         data: {
	//           ...n.data,
	//           execution_trace: nextTrace,
	//         },
	//       }
	//     })
	//   )
	// }, [setNodes, steps])

	// toggle edges to 'ant line' only when running state changes
	const prevRunningRef = useRef<boolean | null>(null);
	useEffect(() => {
		if (prevRunningRef.current === (running ?? null)) return;
		prevRunningRef.current = running ?? null;
		setEdges((eds) =>
			eds.map((e) => ({
				...e,
				animated: !!running,
				style: running
					? { ...e.style, strokeDasharray: "6 3" }
					: { ...e.style, strokeDasharray: undefined },
			})),
		);
	}, [setEdges, running]);

	const onConnect = useCallback(
		(params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
		[setEdges],
	);
	const { currentTheme } = useTheme();
	return (
		<ReactFlow
			nodes={nodes}
			edges={edges}
			onNodesChange={onNodesChange}
			onEdgesChange={onEdgesChange}
			onConnect={onConnect}
			nodeTypes={nodeTypes}
			proOptions={{
				hideAttribution: true,
			}}
			colorMode={currentTheme === "dark" ? "dark" : "light"}
			fitView
		>
			<Controls position="top-right" orientation="horizontal">
				<ControlButton
					onClick={() => {
						setIsFullscreen(!isFullscreen);
					}}
					title="Toggle fullscreen"
				>
					{isFullscreen ? <ScreenFullview2Off /> : <ScreenFullview2On />}
				</ControlButton>
			</Controls>
			<MiniMap />
		</ReactFlow>
	);
}
