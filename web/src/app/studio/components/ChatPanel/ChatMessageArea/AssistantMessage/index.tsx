import { ArrowDown, CheckMark, Loading } from "@hatchify/icons";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import AnswerMakdown from "@/components/common/Markdown/AnswerMakdown";
import { type ChatHistory, type MessageItem, MessageItemType } from "@/types/chat";
import { cn } from "@/utils";
import ProgressComponent from "./Progress";

function AssistantMessage({ message }: { message: ChatHistory }) {
	const isLoading = message.type === "loading";
	return (
		<div
			className={cn(
				"group flex w-full flex-col items-start gap-3 px-4 message-item text-text-primary-1",
				// { [styles.blinkContainer]: isLoading },
			)}
		>
			{message.type === "loading" && message.content.length === 0 ? (
				<Loading className="animate-spin" size={16} />
			) : (
				message.content.map((item: MessageItem, index: number) => (
					<MessageItemNode
						key={index}
						item={item}
						isLast={isLoading && index === message.content.length - 1}
					/>
				))
			)}
		</div>
	);
}

export function MessageItemNode({
	item,
	isLast,
}: {
	item: MessageItem;
	isLast: boolean;
}) {
	switch (item.type) {
		case MessageItemType.TEXT:
			return <TextMarkdownNode item={item} isLoading={isLast} />;
		case MessageItemType.CODE:
			return <CodeNode item={item} isLoading={isLast} />;
		case MessageItemType.REASONING:
			return <ReasoningNode item={item} isLoading={isLast} />;
		case MessageItemType.PROGRESS:
			return <ProgressNode item={item} isLoading={isLast} />;
		case MessageItemType.TOOL_USE:
			return <ToolUseNode item={item} isLoading={isLast} />;
		default:
			return null;
	}
}

function TextMarkdownNode({
	item,
	isLoading,
}: {
	item: Extract<MessageItem, { type: typeof MessageItemType.TEXT }>;
	isLoading: boolean;
}) {
	return (
		<>
			<AnswerMakdown>{item.text}</AnswerMakdown>
			{isLoading && <Loading className="animate-spin" size={16} />}
		</>
	);
}

function ReasoningNode({
	item,
	isLoading,
}: {
	item: Extract<MessageItem, { type: typeof MessageItemType.REASONING }>;
	isLoading: boolean;
}) {
	const { t } = useTranslation();
	const [expanded, setExpanded] = useState(false);
	return (
		<div className="w-full rounded-xl px-[10px] border-grey-line2-normal border">
			<div
				className="h-9 flex justify-between items-center cursor-pointer"
				onClick={() => setExpanded(!expanded)}
			>
				<div className="flex items-center gap-3 text-text-primary-3 text-sm">
					{isLoading ? (
						<Loading className="animate-spin" size={16} />
					) : (
						<CheckMark className="size-4" />
					)}
					{isLoading ? (
						<span>{t("chat.reasoning")}...</span>
					) : (
						<span>{t("chat.ReasoningCompleted")}</span>
					)}
				</div>
				<ArrowDown className={cn("size-4", { "rotate-180": expanded })} />
			</div>
			<div hidden={!expanded} className="text-text-primary-3 text-sm pb-[10px]">
				<AnswerMakdown>{item.reasoning}</AnswerMakdown>
			</div>
		</div>
	);
}

function CodeNode({
	item,
	isLoading,
}: {
	item: Extract<MessageItem, { type: typeof MessageItemType.CODE }>;
	isLoading: boolean;
}) {
	const { t } = useTranslation();
	const codeType = {
		"code-write": t("chat.write"),
		"code-replace": t("chat.replace"),
		"code-delete": t("chat.delete"),
	}[item.code.type];
	return (
		<div
			onClick={() => {
				// switchViewFile(memAbsolutePath(item.code.path))
			}}
			className="w-full rounded-xl px-[10px] border-grey-line2-normal border cursor-pointer hover:bg-grey-fill2-normal transition-colors"
		>
			<div className="flex items-center gap-3 text-text-primary-3 text-sm h-9">
				{isLoading ? (
					<Loading className="animate-spin" size={16} />
				) : (
					<CheckMark className="size-4" />
				)}
				<span className="whitespace-nowrap overflow-hidden text-ellipsis">
					{codeType} {item.code.path}
				</span>
			</div>
		</div>
	);
}

function ProgressNode({
	item,
	isLoading,
}: {
	item: Extract<MessageItem, { type: typeof MessageItemType.PROGRESS }>;
	isLoading: boolean;
}) {
	return <ProgressComponent item={item} isLoading={isLoading} />;
}

function ToolUseNode({
	item,
	isLoading,
}: {
	item: Extract<MessageItem, { type: typeof MessageItemType.TOOL_USE }>;
	isLoading: boolean;
}) {
	const [expanded, setExpanded] = useState(false);

	return (
		<div className="w-full rounded-xl px-[10px] border-grey-line2-normal border">
			<div
				className="h-9 flex justify-between items-center cursor-pointer"
				onClick={() => setExpanded(!expanded)}
			>
				<div className="flex items-center gap-3 text-text-primary-3 text-sm">
					{isLoading ? (
						<Loading className="animate-spin" size={16} />
					) : (
						<CheckMark className="size-4" />
					)}
					<span>🔧 {item.toolUse.name}</span>
				</div>
				<ArrowDown className={cn("size-4", { "rotate-180": expanded })} />
			</div>
			<div hidden={!expanded} className="text-text-primary-3 text-sm pb-[10px]">
				<div className="space-y-2">
					<div>
						<span className="font-semibold">Tool ID:</span>{" "}
						{item.toolUse.toolUseId}
					</div>
					<div>
						<span className="font-semibold">Input:</span>
						<pre className="mt-1 p-2 bg-grey-fill1-normal rounded text-xs overflow-x-auto">
							{JSON.stringify(item.toolUse.input, null, 2)}
						</pre>
					</div>
				</div>
			</div>
		</div>
	);
}

export default AssistantMessage;
