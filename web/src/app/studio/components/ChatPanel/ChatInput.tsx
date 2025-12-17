import {
	Agent as MultiAgentIcon,
	SendFilled,
	Webpage as WebpageIcon,
} from "@hatchify/icons";
import { useClickAway } from "ahooks";
import { memo, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useShallow } from "zustand/react/shallow";
import { useWebCreatorChatMessage } from "@/hooks/useWebcreator";
import { useWorkflowChatMessage } from "@/hooks/useWorkflow";
import useWebCreatorStore from "@/stores/webcreator";
import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";
import { cn } from "@/utils";

function ChatInput() {
	const { t } = useTranslation();
	const [value, setValue] = useState("");
	const [focused, setFocused] = useState(false);

	const { studioPanelTab, isWorkflowCreating } = useWorkflowStore(
		useShallow((state) => ({
			studioPanelTab: state.studioPanelTab,
			isWorkflowCreating: state.isWorkflowCreating,
		})),
	);

	const webCreating = useWebCreatorStore((s) => s.pending);

	const { webCreatorChat } = useWebCreatorChatMessage();

	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const inputNodeRef = useRef<HTMLDivElement>(null);

	useClickAway(() => {
		setFocused(false);
	}, inputNodeRef);

	// const { webcreatorChat } = useWebCreatorChatMessage();
	const { workflowChat } = useWorkflowChatMessage();

	// Reset textarea height when value is programmatically cleared
	useEffect(() => {
		if (value === "" && textareaRef.current) {
			const el = textareaRef.current;
			el.style.height = "auto";
			el.style.overflowY = "hidden";
		}
	}, [value]);

	async function sendMessage() {
		if (!value.trim()) return;
		const messageContent = value;
		setValue("");
		if (studioPanelTab === StudioPanelTab.WebCreator) {
			webCreatorChat(messageContent);
			return;
		}

		workflowChat(messageContent);
	}

	return (
		<div
			ref={inputNodeRef}
			className="relative mt-auto"
			onClick={() => {
				textareaRef.current?.focus();
			}}
		>
			<div className="relative">
				<div className="relative top-[24px] bg-grey-fill2-normal flex gap-2 pb-8 rounded-t-[20px] text-text-primary-3 px-4 py-2 items-center">
					{studioPanelTab === StudioPanelTab.WebCreator ? (
						<WebpageIcon className="translate-y-0.5 size-4" />
					) : (
						<MultiAgentIcon className="translate-y-0.5 size-4" />
					)}
					<span className="text-sm select-none">
						{studioPanelTab === StudioPanelTab.WebCreator
							? t("agentAction.websiteEditor")
							: t("agentAction.workflowEditor")}
					</span>
				</div>
				<div
					className={cn(
						"cursor-text rounded-[20px] border border-solid border-grey-line2-normal relative overflow-hidden",
						focused &&
							"!border-grey-line2-hover shadow-[0px_0px_0px_3px_rgba(114,118,139,0.06)]",
					)}
				>
					<div>
						{/* <FileScrollArea wisebaseId={wisebaseId} /> */}

						<div className="" style={{ fontSize: 0 }}>
							<textarea
								ref={textareaRef}
								className={cn(
									"min-h-28 pt-1 text-text-primary-1 px-2 cus-scrollbar h-full w-full bg-grey-layer1-white text-base outline-none placeholder:text-text-primary-4",
								)}
								style={{
									scrollbarGutter: "stable",
									resize: "none",
								}}
								placeholder={t("agentAction.askAnything")}
								value={value}
								disabled={
									(studioPanelTab === StudioPanelTab.WebCreator &&
										webCreating) ||
									(studioPanelTab === StudioPanelTab.Workflow &&
										isWorkflowCreating)
								}
								onKeyDown={(e) => {
									if (e.key === "Enter" && !e.shiftKey) {
										// 检查是否正在使用输入法
										if (
											e.nativeEvent.isComposing ||
											e.nativeEvent.keyCode === 229
										) {
											return; // 正在输入法编辑状态，不发送消息
										}
										e.preventDefault();
										sendMessage();
									}
								}}
								onChange={(e) => {
									setValue(e.target.value);
									e.target.style.height = "auto";
									const scrollHeight = e.target.scrollHeight;

									const lineHeight = 24;
									const maxHeight = lineHeight * 10;

									e.target.style.height = `${Math.min(scrollHeight, maxHeight)}px`;

									e.target.style.overflowY =
										scrollHeight > maxHeight ? "auto" : "hidden";
								}}
								onPaste={(e) => {
									const files = [...e.clipboardData.files];
									if (files.length) {
										e.preventDefault();
									}
								}}
								data-ext-inject="no"
								onFocus={() => {
									setFocused(true);
								}}
							/>
						</div>
					</div>
					<div className="flex gap-1.5 px-2 ps-3">
						<button
							disabled={!value}
							className={cn(
								"ms-auto size-9 rounded-[10px] transition-colors flex items-center justify-center	",
								value.trim()
									? "hover:bg-grey-fill1-hover"
									: "text-text-primary-5",
							)}
							onClick={() => sendMessage()}
						>
							<SendFilled size={18} />
						</button>
					</div>
				</div>
			</div>
		</div>
	);
}

export default memo(ChatInput);
