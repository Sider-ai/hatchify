import { useQuery } from "@tanstack/react-query";
import _request, { HyperRequest } from "@/lib/request";
import type { ApiResponse } from "@/types/api";

const request = HyperRequest.prefixExtend("/models", _request);

export function getModelList() {
	return request.get<
		ApiResponse<{ id: string; name: string; description: string }[]>
	>("/all");
}

export const useModelList = () => {
	const { data, isLoading, ...rest } = useQuery({
		queryKey: ["modelList"],
		queryFn: () => getModelList(),
		select(data) {
			if (data.data) return data.data;
			return [];
		},
	});

	return {
		modelList: data ?? [],
		isLoading,
		...rest,
	};
};
