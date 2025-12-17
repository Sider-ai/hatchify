import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App } from "antd";
import { nanoid } from "nanoid";
import { useEffect, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import { ExecutionApi, WorkflowApi } from "@/api";
import { useStudioParams } from "@/hooks/useStudioParams";
import type { HyperAbortController } from "@/lib/request/base";
import { handleWorkflowStream } from "@/lib/stream";
import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";
import { workflowTaskId } from "@/utils/taskId";
import { useWebCreatorInitialization } from "./useWebcreator";

export const useTaskStatus = ({ taskId }: { taskId: string }) => {
	const { data, isLoading, refetch, error } = useQuery({
		queryKey: ["workflowTaskStatus", taskId],
		queryFn: () => ExecutionApi.getTaskExectionDetailByID(taskId!),
		enabled: !!taskId,
		refetchOnWindowFocus: false,
		refetchOnMount: true,

		select(data) {
			if (!data?.data) return null;
			return data.data;
		},
	});

	return {
		taskStatus: data,
		isLoading,
		refetch,
		error,
	};
};

/**
 * Hook for creating and streaming workflow updates
 */
export function useCreateWorkflowStream() {
	const controller = useRef<HyperAbortController | null>(null);
	const { taskIdForWorkflow } = useStudioParams();
	const queryClient = useQueryClient();

	const { refetch: refetchWorkflowDetail } = useWorkflowDetail({});

	const handleWorkflowCreateStream = async () => {
		if (!taskIdForWorkflow) {
			return;
		}

		await handleWorkflowStream(taskIdForWorkflow, controller);
		queryClient.invalidateQueries({
			queryKey: ["workflowTaskStatus", taskIdForWorkflow],
		});
		await refetchWorkflowDetail();
	};

	return {
		handleWorkflowCreateStream,
	};
}

/**
 * Hook for fetching workflow detail by session ID
 */
export function useWorkflowDetail({ enabled = false }: { enabled?: boolean }) {
	const { workflowId } = useStudioParams();
	const { data, isLoading, refetch } = useQuery({
		queryKey: ["workflowDetail", workflowId],
		queryFn: () => WorkflowApi.fetchWorkflowDetailById(workflowId!),
		enabled,
		// always refetch on mount and avoid caching between navigations
		refetchOnMount: true,
		refetchOnWindowFocus: false,
		staleTime: 0,
		gcTime: 0,
		select(data) {
			if (!data?.data) return null;
			return data.data;
		},
	});

	return {
		workflow: data,
		isLoading,
		refetch,
	};
}

/**
 * Hook for sending chat messages to workflow and handling streaming responses
 */
export function useWorkflowChatMessage() {
	const { message } = App.useApp();
	const controller = useRef<HyperAbortController | null>(null);
	const { refetch: refetchWorkflowDetail } = useWorkflowDetail({});
	const { setChatHistoryForWorkflow } = useWorkflowStore(
		useShallow((state) => ({
			setChatHistoryForWorkflow: state.setChatHistoryForWorkflow,
		})),
	);

	const workflowChat = useMutation({
		mutationFn: async (content: string) => {
			useWorkflowStore.setState({ isWorkflowCreating: true });
			const response = await WorkflowApi.createOrUpdateWorkflowStream({
				text: content,
			});
			workflowTaskId.set(response.data.graph_id, response.data.execution_id);
			return handleWorkflowStream(response.data.execution_id, controller);
		},
		onMutate: async (content: string) => {
			setChatHistoryForWorkflow((prev) => {
				return [
					...prev,
					{
						id: nanoid(),
						role: "user",
						content: [
							{
								type: "text",
								text: content,
								id: nanoid(),
							},
						],
						mode: StudioPanelTab.Workflow,
					},
					{
						id: nanoid(),
						role: "assistant",
						content: [
							{
								type: "text",
								text: "",
								id: nanoid(),
							},
						],
						mode: StudioPanelTab.Workflow,
						type: "loading" as any,
					},
				];
			});
		},
		onSuccess: async (_data) => {
			await refetchWorkflowDetail();
		},
		onError: (error: any) => {
			message.error(error?.message || "Workflow refine failed");
			useWorkflowStore.setState({ isWorkflowCreating: false });
		},
	});

	useEffect(() => {
		return () => {
			controller.current?.abort();
		};
	}, []);

	return {
		workflowChat: async (content: string) => {
			return await workflowChat.mutateAsync(content);
		},
	};
}

/**
 * Hook for initializing workflow page and handling stream on mount
 */
export function useWorkflowPageInit() {
	const { taskIdForWorkflow } = useStudioParams();
	const { handleWorkflowCreateStream } = useCreateWorkflowStream();

	const _controller = useRef<HyperAbortController | null>(null);
	_controller;
	const {
		taskStatus: workflowTaskStatus,
		isLoading: isWorkflowTaskStatusLoading,
	} = useTaskStatus({
		taskId: taskIdForWorkflow!,
	});

	const { isLoading: _isWorkflowDetailLoading } = useWorkflowDetail({
		enabled: workflowTaskStatus?.status === "completed" && !!taskIdForWorkflow,
	});

	const isLoading = isWorkflowTaskStatusLoading;

	useEffect(() => {
		if (taskIdForWorkflow && workflowTaskStatus?.status === "running") {
			void handleWorkflowCreateStream();
		}
	}, [taskIdForWorkflow, workflowTaskStatus?.status]);

	useWebCreatorInitialization();

	return {
		isLoading: isLoading,
	};
}
