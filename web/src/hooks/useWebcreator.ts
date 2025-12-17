import { useMutation, useQuery } from "@tanstack/react-query";
import { App } from "antd";
import { nanoid } from "nanoid";
import { useEffect, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import { WebCreatorApi } from "@/api";
import type { HyperAbortController } from "@/lib/request/base";
import { handleWebCreatorStream } from "@/lib/stream";
import useWebCreatorStore from "@/stores/webcreator";
import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";
import { webCreatorTaskId } from "@/utils/taskId";
import { useStudioParams } from "./useStudioParams";
import { useTaskStatus } from "./useWorkflow";

export function useWebCreatorInitialization() {
	const controller = useRef<HyperAbortController | null>(null);
	const { workflowId, taskIdForWebCreator } = useStudioParams();
	const isInit = useRef(false);

	const { taskStatus: webCreatorTaskStatus } = useTaskStatus({
		taskId: taskIdForWebCreator!,
	});

	const { pending, setPending } = useWebCreatorStore(
		useShallow((state) => ({
			pending: state.pending,
			setPending: state.setPending,
		})),
	);

	useEffect(() => {
		if (
			!pending &&
			workflowId &&
			!isInit.current &&
			taskIdForWebCreator &&
			webCreatorTaskStatus?.status === "running"
		) {
			setPending(true);
			handleWebCreatorStream(taskIdForWebCreator!, controller);
		}

		if (webCreatorTaskStatus) {
			isInit.current = true;
		}
	}, [webCreatorTaskStatus?.status, workflowId]);

	useEffect(() => {
		return () => {
			controller.current?.abort();
		};
	}, []);

	return {};
}

/**
 * Hook for sending chat messages to workflow and handling streaming responses
 */
export function useWebCreatorChatMessage() {
	const { message } = App.useApp();
	const controller = useRef<HyperAbortController | null>(null);
	const { setChatHistoryForWebCreator } = useWorkflowStore(
		useShallow((state) => ({
			setChatHistoryForWebCreator: state.setChatHistoryForWebCreator,
		})),
	);

	const { workflowId } = useStudioParams();

	const webCreatorChat = useMutation({
		mutationFn: async (content: string) => {
			useWebCreatorStore.setState({ pending: true });
			const response = await WebCreatorApi.createOrUpdateWebCreatorStream({
				text: content,
				workflowId: workflowId!,
			});
			webCreatorTaskId.set(response.data.graph_id, response.data.execution_id);
			return handleWebCreatorStream(response.data.execution_id, controller);
		},
		onMutate: async (content: string) => {
			// Only add user message, streamHandler will add loading message
			setChatHistoryForWebCreator((prev) => {
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
						mode: StudioPanelTab.WebCreator,
					},
				];
			});
		},
		onSuccess: async (_data) => {
			console.log("web creator success");
		},
		onError: (error: any) => {
			message.error(error?.message || "Web creator refine failed");
			useWebCreatorStore.setState({ pending: false });
		},
	});

	useEffect(() => {
		return () => {
			controller.current?.abort();
		};
	}, []);

	return {
		webCreatorChat: async (content: string) => {
			return await webCreatorChat.mutateAsync(content);
		},
	};
}

const _usePreviewUrl = () => {
	const { workflowId } = useStudioParams();
	const { data } = useQuery({
		queryKey: ["previewUrl", workflowId],
		queryFn: () =>
			fetch(`${import.meta.env.VITE_API_URL}/preview/${workflowId}`),
	});
	return data;
};
