// import { useChatHistoryQuery } from "@/lib/webcreator/useChatHistoryQuery";
import { useChatHistoryQuery } from "@/hooks/useChatHistory";
import ChatInput from "./ChatInput";
import ChatMessageArea from "./ChatMessageArea";

export default function ChatPanel() {
	useChatHistoryQuery();
	return (
		<div className="flex h-full flex-col">
			<ChatMessageArea />
			<ChatInput />
		</div>
	);
}
