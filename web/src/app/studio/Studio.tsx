import { Loading } from "@hatchify/icons";
import { motion } from "motion/react";
import { useShallow } from "zustand/react/shallow";
import WorkflowWebsiteSwitchTab from "@/components/common/WorkflowWebsiteSwitchTab";
import { useSplitter2 } from "@/hooks/useSplitter";
import { useWorkflowDetail, useWorkflowPageInit } from "@/hooks/useWorkflow";
import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";
import ChatPanel from "./components/ChatPanel";
import StudioPageHeader from "./components/StudioPageHeader";
import WebCreator from "./components/WebsitePanel/WebCreator/WebCreator";
import WorkFlowPanel from "./components/WorkflowPanel";

export default function StudioPage() {
	const { isLoading } = useWorkflowPageInit();
	const { SplitterHandleNode, targetEl } = useSplitter2({});

	const { workflow } = useWorkflowDetail({});
	const { currentMode } = useWorkflowStore(
		useShallow((state) => ({
			currentMode: state.studioPanelTab,
		})),
	);

	return (
		<div className="p-4 pt-0  flex flex-1 flex-col  h-screen bg-grey-layer1-white">
			<StudioPageHeader
				canEditName={true}
				projectName={workflow?.name ?? ""}
				workflowId={workflow?.id}
				rightComponent={[]}
				redirectToLogin
				middleComponent={<WorkflowWebsiteSwitchTab />}
			/>

			<div className="flex-1 flex w-full min-h-0">
				<div
					onScroll={(event) => {
						event.currentTarget.scrollLeft = 0;
					}}
					className="flex-1 overflow-hidden scroll-m-0 scroll-p-0"
				>
					<motion.div
						animate={{
							x: currentMode === StudioPanelTab.Workflow ? 0 : "-50%",
						}}
						transition={{
							duration: 0.3,
						}}
						className="w-[200%] h-full flex"
					>
						<div className="flex-1 mr-1 min-w-0 flex-shrink-0 border border-grey-line2-normal rounded-xl overflow-hidden">
							<WorkFlowPanel></WorkFlowPanel>
						</div>
						<div className="flex flex-1 flex-shrink-0 overflow-hidden min-w-0 share-iframe-wrap">
							<div
								className="h-full w-[360px] min-w-[300px] max-w-[500px] rounded-[12px] bg-grey-layer1-white mr-1"
								ref={targetEl}
							>
								<ChatPanel />
							</div>
							<div>{SplitterHandleNode}</div>
							<div
								style={{
									boxShadow:
										"0 2px 8px 0 var(--color-shadow-overflow-2), 0 4px 16px 0 var(--color-shadow-overflow-2), 0 8px 32px 0 var(--color-shadow-overflow-2)",
								}}
								className="flex-1 border border-grey-line2-normal rounded-xl "
							>
								<WebCreator />
							</div>
						</div>
					</motion.div>
				</div>
			</div>

			<LoadingOverlay isLoading={isLoading} />
		</div>
	);
}

const LoadingOverlay: React.FC<{ isLoading: boolean }> = ({ isLoading }) => {
	if (!isLoading) return null;

	return (
		<>
			{isLoading && (
				<div className="fixed inset-0 flex justify-center items-center bg-grey-layer2-normal">
					<Loading className="animate-spin text-text-primary-1" size={24} />
				</div>
			)}
		</>
	);
};
