import { useQuery } from "@tanstack/react-query";
import { nanoid } from "nanoid";
import { useEffect } from "react";
import { WebCreatorApi } from "@/api";
import useWorkflowStore from "@/stores/workflow";
import { type ChatHistory, StudioPanelTab } from "@/types/chat";
import { useStudioParams } from "./useStudioParams";

export function useChatHistory(workflowId: string) {
	const { data } = useQuery({
		queryKey: ["chatHistory", workflowId],
		queryFn: () => WebCreatorApi.getWebCreatorMessageHistory(workflowId),
		retry: false,
		refetchOnMount: false,
		refetchOnWindowFocus: false,
		select(data) {
			return data.data;
		},
	});
	return {
		data,
	};
}

export function useChatHistoryQuery() {
	const { workflowId } = useStudioParams();
	const { data } = useChatHistory(workflowId!);
	const setChatHistoryForWebCreator = useWorkflowStore(
		(state) => state.setChatHistoryForWebCreator,
	);
	useEffect(() => {
		if (data) {
			const chatItems: ChatHistory[] = [];
			for (const item of data || []) {
				const chatItem: ChatHistory = {
					id: nanoid(),
					role: item.role,
					type: "message",
					mode: StudioPanelTab.WebCreator,
					content: [],
				};
				// console.log("item:", item);
				if (item.role === "assistant") {
					// Process assistant messages - handle both text and toolUse
					chatItem.content = item.content.map((content: any) => {
						// Handle text content
						if (content.text) {
							return {
								type: "text",
								text: content.text,
								id: nanoid(),
							};
						}
						// Handle toolUse content
						if (content.toolUse) {
							return {
								type: "toolUse",
								toolUse: content.toolUse,
								id: nanoid(),
							};
						}
						// Fallback for unknown content types
						return {
							type: "text",
							text: JSON.stringify(content),
							id: nanoid(),
						};
					});
				} else {
					// Process user messages - only keep text content, filter out toolResult
					chatItem.content = item.content
						.filter((content: any) => content.text) // Only keep items with text field
						.map((content: any) => ({
							type: "text",
							text: content.text,
							id: nanoid(),
						}));
				}

				// Only add the chat item if it has content
				if (chatItem.content.length > 0) {
					chatItems.push(chatItem);
				}
			}

			// Preserve existing loading messages when setting history
			// This is crucial when the page is refreshed while a stream is in progress
			setChatHistoryForWebCreator((prev) => {
				// Find any loading messages in the current state
				const loadingMessages = prev.filter(
					(msg) => msg.type === "loading" && msg.role === "assistant",
				);

				// If there are loading messages, append them to the history
				if (loadingMessages.length > 0) {
					return [...chatItems, ...loadingMessages];
				}

				return chatItems;
			});
		}
	}, [data]);
}
