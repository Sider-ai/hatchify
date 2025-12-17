import { useEffect, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";
import AssistantMessage from "./AssistantMessage";
import UserMessage from "./UserMessge";

export default function ChatMessageArea() {
	const { chatHistoryForWorkflow, chatHistoryForWebCreator, studioPanelTab } =
		useWorkflowStore(
			useShallow((state) => {
				return {
					chatHistoryForWorkflow: state.chatHistoryForWorkflow,
					chatHistoryForWebCreator: state.chatHistoryForWebCreator,
					studioPanelTab: state.studioPanelTab,
				};
			}),
		);

	const chatHistory =
		studioPanelTab === StudioPanelTab.WebCreator
			? chatHistoryForWebCreator
			: chatHistoryForWorkflow;

	const scrollRef = useRef<HTMLDivElement>(null);
	const messagesEndRef = useRef<HTMLDivElement>(null);

	// 仅在已接近底部（≤160px）时才自动滚动到底部，否则不滚动
	const scrollToBottom = () => {
		const container = scrollRef.current;
		if (!container) {
			messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
			return;
		}
		const distanceToBottom =
			container.scrollHeight - container.scrollTop - container.clientHeight;
		if (distanceToBottom <= 160) {
			messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
		}
	};

	// 当消息更新时滚动到底部
	useEffect(() => {
		scrollToBottom();
	}, [chatHistory]);

	useEffect(() => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [chatHistory.length]);

	return (
		<div ref={scrollRef} className="custom-scrollbar h-full overflow-auto pt-4">
			<div className="flex flex-col gap-6">
				{chatHistory.map((message) =>
					message.role === "user" ? (
						<UserMessage key={message.id} message={message} />
					) : (
						<AssistantMessage key={message.id} message={message} />
					),
				)}
				<div ref={messagesEndRef} />
			</div>
		</div>
	);
}
