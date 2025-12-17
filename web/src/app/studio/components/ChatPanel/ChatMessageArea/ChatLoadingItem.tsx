import { Loading } from "@hatchify/icons";

function ChatLoadingItem() {
	return (
		<div className="group flex w-full flex-col items-start gap-3 px-4">
			<div
				className="w-fit rounded-[12px] bg-grey-fill2-normal px-4 py-[10px] text-sm leading-[24px] text-text-primary-2"
				style={{
					wordBreak: "break-word",
					whiteSpace: "pre-wrap",
				}}
			>
				<Loading className="animate-spin" size={16} />
			</div>
		</div>
	);
}

export default ChatLoadingItem;
