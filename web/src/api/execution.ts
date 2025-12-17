import request, { HyperRequest } from "@/lib/request";
import type { ApiResponse } from "@/types/api";

const requestExecution = HyperRequest.prefixExtend("/executions", request);

export const getTaskExectionDetailByID = (id: string) => {
	return requestExecution.get<ApiResponse<TaskExecutionDetail>>(
		`/get_by_id/${id}`,
	);
};

type TaskExecutionDetail = {
	id: string;
	type: "graph_builder" | "webhook" | "web_builder" | "deploy";
	status: "completed" | "pending" | "running" | "failed" | "cancelled";
	error: string | null;
	graph_id: string;
	session_id: string;
	created_at: string;
	started_at: string;
	completed_at: string;
	updated_at: string;
};
