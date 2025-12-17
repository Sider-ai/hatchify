import { useQuery } from "@tanstack/react-query";
import request, { HyperRequest } from "@/lib/request";
import type { AgentToolDetail } from "@/types/agent";
import type { ApiResponse } from "@/types/api";

const requestAgent = HyperRequest.prefixExtend("/tools", request);

export const getAgentToolsList = () => {
	return requestAgent.get<ApiResponse<AgentToolDetail[]>>("/all");
};

export const useAgentToolsList = () => {
	return useQuery({
		queryKey: ["all-agent-tools"],
		queryFn: () => getAgentToolsList(),
		select(data) {
			if (data?.data) {
				return data.data;
			}
			return [];
		},
	});
};
