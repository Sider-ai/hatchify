import request, { HyperRequest } from "@/lib/request";
import type { ApiResponse } from "@/types/api";
import type { ChatHistory } from "@/types/chat";

const requestWebCreator = HyperRequest.prefixExtend("/web-builder", request);

// create or update web creator stream
export const createOrUpdateWebCreatorStream = ({
	text,
	workflowId,
}: {
	text: string;
	workflowId: string;
}) => {
	return requestWebCreator.post<
		ApiResponse<{
			session_id: string;
			execution_id: string;
			graph_id: string;
		}>
	>(`/stream`, {
		graph_id: workflowId,
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

// get web creator progress stream by execution_id
export const getWebCreatorProgressStream = (execution_id: string) => {
	return requestWebCreator.get<ReadableStream<Uint8Array>>(
		`/stream/${execution_id}`,
		{
			headers: {
				Accept: "text/event-stream",
			},
		},
	);
};

export const getWebCreatorMessageHistory = (workflowId: string) => {
	return requestWebCreator.get<ApiResponse<ChatHistory[]>>(
		`/history/${workflowId}`,
	);
};
