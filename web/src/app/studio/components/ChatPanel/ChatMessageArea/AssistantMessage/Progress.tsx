import { CheckMark, Loading } from "@hatchify/icons";
import { memo } from "react";
import type { MessageItem, MessageItemType } from "@/types/chat";

function Progress({
	item,
	isLoading: _,
}: {
	item: Extract<MessageItem, { type: typeof MessageItemType.PROGRESS }>;
	isLoading: boolean;
}) {
	return (
		<div className="text-text-primary-2 flex items-center gap-2">
			{item.progress === 100 ? (
				<CheckMark className="size-4 text-green-500" />
			) : (
				<Loading className="size-4 animate-spin" />
			)}
			<span>{item.progress}%</span>
		</div>
	);
}

export default memo(Progress);
