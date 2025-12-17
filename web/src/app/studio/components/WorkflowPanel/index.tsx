import { Agent as MutiAgentIcon } from "@hatchify/icons";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useShallow } from "zustand/react/shallow";
import AgentInput from "@/app/studio/components/AgentInput";
import { useWorkflowChatMessage } from "@/hooks/useWorkflow";
import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";
import { cn } from "@/utils";
import AgentFlow from "./AgentFlow";

export default function AgentPanel() {
	const [isFullscreen, setIsFullscreen] = useState(false);

	const { workflowChat } = useWorkflowChatMessage();

	const { isWorkflowCreating, studioPanelTab } = useWorkflowStore(
		useShallow((state) => ({
			isWorkflowRunning: state.isWorkflowRunning,
			isWorkflowCreating: state.isWorkflowCreating,
			studioPanelTab: state.studioPanelTab,
		})),
	);

	useEffect(() => {
		if (studioPanelTab === StudioPanelTab.WebCreator) {
			setIsFullscreen(false);
		}
	}, [studioPanelTab]);

	return (
		<div
			className={`bg-grey-layer2-normal rounded-xl flex flex-col  ${isFullscreen ? "fixed top-2 right-2 bottom-2 left-2 z-[99]" : "h-full w-full"}`}
		>
			<div className="bg-grey-layer1-normal rounded-xl flex-1 relative">
				<AgentFlow
					isFullscreen={isFullscreen}
					setIsFullscreen={setIsFullscreen}
				/>
				{/* {isShowMask && <div className="absolute top-0 left-0 w-full h-full bg-grey-layer1-semitrans2/80"></div>} */}

				{/* {shouldShowCreateWebsiteTip && (
          <div className="absolute bottom-20 left-[50%] translate-x-[-50%]">
            <CreateWebsiteTip disabled={isWorkflowCreating || createWebsitePending || updateWebsitePending || isBuildingWebSite} isCreate={isNotInit} onClick={() => handleCreateWebsite()} />
          </div>
        )} */}
				<div className="absolute bottom-3 left-[50%] translate-x-[-50%]">
					<AgentInput isLoading={isWorkflowCreating} onSend={workflowChat} />
				</div>
			</div>
		</div>
	);
}

function _CreateWebsiteTip({
	onClick,
	disabled,
	isCreate,
}: {
	onClick: () => void;
	disabled: boolean;
	isCreate: boolean;
}) {
	const { t } = useTranslation();
	return (
		<div
			className={cn(
				"flex w-[720px] h-[72px] items-center gap-4 rounded-[16px] px-5",
				"border-[1px] border-grey-layer2-normal bg-grey-layer2-normal",
				"shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal),0px_4px_16px_0px_var(--3,rgba(12,13,25,0.03)),0px_8px_32px_0px_var(--3,rgba(12,13,25,0.03)),0px_16px_64px_0px_var(--3,rgba(12,13,25,0.03))]",
			)}
		>
			<div className="">
				<div className="text-text-primary-1 font-[800]">
					{isCreate
						? t("agentAction.createWebsite")
						: t("agentAction.updateWebsite")}
				</div>
				<div className="text-text-primary-2 text-sm font-[400]">
					{isCreate
						? t("agentAction.tipCounter.message")
						: t("agentAction.tipCounter.messageUpdate")}
				</div>
			</div>
			<button
				onClick={onClick}
				disabled={disabled}
				className="ml-auto text-sm hover:bg-advanced-fil-hover bg-advanced-fill-normal rounded-full py-1.5 px-3.5 text-text-secondary-1 cursor-pointer"
			>
				{isCreate
					? t("agentAction.tipCounter.generateNow")
					: t("agentAction.tipCounter.updateNow")}
			</button>
		</div>
	);
}

function _CreateWorkflowLoading() {
	const { t } = useTranslation();
	return (
		<div className="flex flex-col items-center gap-2.5 text-text-primary-3">
			<MutiAgentIcon size={24} />
			<span className="text-sm">{t("agentAction.creatingWorkflow")}</span>
		</div>
	);
}
