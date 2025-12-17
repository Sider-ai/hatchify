import request, { HyperRequest } from "@/lib/request";
import type { ApiResponse, WithPagination } from "@/types/api";
import type { WorkflowDetail, WorkflowListItem } from "@/types/workflow";

const requestWorkflow = HyperRequest.prefixExtend("/graphs", request);

// get workflow detail by graph_id
export const fetchWorkflowDetailById = (id: string) => {
	return requestWorkflow.get<ApiResponse<WorkflowDetail>>(`/get_by_id/${id}`);
};

// get workflow list
export const fetchWorkflowList = ({
	page = 1,
	size = 100,
}: {
	page?: number;
	size?: number;
}) => {
	return requestWorkflow.get<ApiResponse<WithPagination<WorkflowListItem>>>(
		`/page?page=${page}&size=${size}&sort=updated_at:desc`,
	);
};

// delete workflow
export const deleteWorkflow = (workflowId: string) => {
	return requestWorkflow.delete(`/delete_by_id/${workflowId}`);
};

// update workflow (name)
export const updateWorkflowByID = (
	workflowId: string,
	params: { name: string },
) => {
	return requestWorkflow.put(`/update_by_id/${workflowId}`, params);
};

// create workflow stream
export const createOrUpdateWorkflowStream = ({ text }: { text: string }) => {
	return requestWorkflow.post<
		ApiResponse<{
			session_id: "string";
			execution_id: "string";
			graph_id: string;
		}>
	>(`/stream`, {
		messages: [
			{
				content: [
					{
						text,
					},
				],
				role: "user",
			},
		],
	});
};

// get workflow progress stream by execution_id
export const getWorkflowProgressStream = (execution_id: string) => {
	return requestWorkflow.get<ReadableStream<Uint8Array>>(
		`/stream/${execution_id}`,
		{
			headers: {
				Accept: "text/event-stream",
			},
		},
	);
};

export const updateWorkflowAgent = (
	workflowId: string,
	agentName: string,
	params: { model?: string; instruction?: string; tools?: string[] },
) => {
	return requestWorkflow.patch(`/${workflowId}/spec`, {
		agents: {
			update: {
				[agentName]: params,
			},
		},
	});
};
