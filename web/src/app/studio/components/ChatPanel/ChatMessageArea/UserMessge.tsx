import { memo } from "react";
import { type ChatHistory, type MessageItem, MessageItemType } from "@/types/chat";

function UserMessge({ message }: { message: ChatHistory }) {
	return (
		<div className="group flex w-full flex-col items-end gap-2 pe-4 ps-[42px]">
			<div
				className="w-fit rounded-[12px] bg-grey-fill2-normal px-4 py-[10px] text-sm leading-[24px] text-text-primary-2"
				style={{
					wordBreak: "break-word",
				}}
			>
				{message.content.map((item: MessageItem) => {
					if (item.type === MessageItemType.TEXT) {
						return <div key={item.id}>{item.text}</div>;
					}
					return null;
				})}
			</div>
		</div>
	);
}

export default memo(UserMessge);
