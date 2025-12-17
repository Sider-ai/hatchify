import { Handle, Position, useReactFlow } from "@xyflow/react";
import { memo } from "react";
import "./style.css";

import NiceModal from "@ebay/nice-modal-react";
import {
	ExclamationMarkTriangleFilledWarning,
	SuccessDot,
} from "@hatchify/icons";
import { Tooltip } from "antd";
import { ToolsApi } from "@/api";
import { ToolSvgIconBox } from "@/components/common/SvgIconBox";
import { useStudioParams } from "@/hooks/useStudioParams";
import { queryClient } from "@/lib/queryClient";
import type { AgentDetail, AgentToolDetail } from "@/types/agent";
import AgentDetailModal from "./AgentDetailModal"; // created by above code

function AgentNode({
	data,
	id,
}: {
	data: AgentDetail & { execution_trace: any | null };
	id: string;
}) {
	const { getEdges } = useReactFlow();
	const edges = getEdges();

	// Check if this node has any incoming connections
	const hasIncomingConnection = edges.some((edge) => edge.target === id);
	// Check if this node has any outgoing connections
	const hasOutgoingConnection = edges.some((edge) => edge.source === id);
	const { workflowId } = useStudioParams();

	const handleClick = async () => {
		await NiceModal.show(AgentDetailModal, {
			data: {
				...data,
				output_schema:
					data.execution_trace?.output_data ?? data.structured_output_schema,
				input_schema:
					data.execution_trace?.input_data ?? data.structured_output_schema,
			},
			workflowId,
		});
		queryClient.invalidateQueries({
			queryKey: ["workflowDetail"],
		});
		NiceModal.hide(AgentDetailModal);
	};

	const { data: _allToolsList, isLoading: _isLoadingAllTools } =
		ToolsApi.useAgentToolsList();

	const statusIcon = () => {
		if (data.execution_trace?.status === "running") {
			return <div className="size-1.5 rounded-full bg-text-primary-4/45"></div>;
		}
		if (data.execution_trace?.status === "completed") {
			return <SuccessDot size={6} />;
		}
		if (
			data.execution_trace?.status === "failed" ||
			data.execution_trace?.status === "error"
		) {
			return (
				<div title={data.execution_trace?.error ?? ""}>
					<ExclamationMarkTriangleFilledWarning size={6} />
				</div>
			);
		}
		return <div className="size-1.5 rounded-full bg-text-primary-4/45"></div>;
	};

	return (
		<section
			style={{
				boxShadow:
					"0px 0px 3px 1px rgba(255, 255, 255, 0.10), 0px 3px 7px 0px rgba(53, 54, 74, 0.04), 0px 0px 3px 0px rgba(12, 13, 25, 0.14), 0px 8px 40px 0px rgba(12, 13, 25, 0.06)",
				background:
					"linear-gradient(0deg, var(--color-grey-fill2-normal) 0%, var(--color-grey-fill2-normal) 100%), var(--color-grey-layer2-normal)",
			}}
			className="rounded-xl relative flex w-[260px] flex-col items-start "
		>
			{hasIncomingConnection && (
				<Handle
					type="target"
					position={Position.Left}
					className="hidden-target-handle"
					style={{ opacity: 0, pointerEvents: "none" }}
				/>
			)}
			<div className="flex items-center gap-2 py-1.5 px-3">
				<div className="text-grey-text-normal text-sm">{statusIcon()}</div>
				<div className="w-[200px] truncate text-text-primary-3 text-sm">
					{data?.name}
				</div>
			</div>
			<div
				onClick={() => {
					handleClick();
				}}
				className="shadow-[0px_-1px_0px_0px_var(--color-grey-fill2-normal)] w-full flex p-3 flex-col gap-2 rounded-xl bg-grey-layer2-normal"
			>
				<div className="text-text-primary-2 text-sm break-words node-instructions-clamp">
					{data.instruction}
				</div>
				<div className="flex gap-2 flex-wrap">
					{data?.tools?.map((tool: string, index: number) => (
						<Tooltip
							key={index}
							title={
								_allToolsList?.find((t: AgentToolDetail) => t?.name === tool)
									?.name ?? tool
							}
						>
							<div>
								<ToolSvgIconBox
									className="size-7 overflow-hidden bg-grey-layer2-normal flex items-center justify-center rounded-lg border border-grey-line2-normal"
									svgString={null}
								/>
							</div>
						</Tooltip>
					))}
				</div>
			</div>
			{hasOutgoingConnection && (
				<Handle type="source" position={Position.Right} />
			)}
		</section>
	);
}

export default memo(AgentNode);
