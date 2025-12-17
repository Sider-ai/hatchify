import {
	Agent as MultiAgentIcon,
	Webpage as WebpageIcon,
} from "@hatchify/icons";
import { useTranslation } from "react-i18next";
import { useShallow } from "zustand/react/shallow";
import Tabs from "@/components/common/Tabs";

import useWorkflowStore from "@/stores/workflow";
import { StudioPanelTab } from "@/types/chat";

export default function WorkflowWebsiteSwitchTab() {
	const { t } = useTranslation();
	const { currentMode, setCurrentMode } = useWorkflowStore(
		useShallow((state) => ({
			currentMode: state.studioPanelTab,
			setCurrentMode: state.setStudioPanelTab,
		})),
	);
	return (
		<Tabs
			tabs={[
				{
					label: (
						<div className="flex items-center gap-2">
							<MultiAgentIcon className="size-4.5" />
							<span> {t("agentAction.workflow")}</span>
						</div>
					),
					value: StudioPanelTab.Workflow,
				},
				{
					label: (
						<div className="flex items-center gap-2">
							<WebpageIcon className="size-4.5 translate-y-[1px]" />
							<span> {t("agentAction.webpage")}</span>
						</div>
					),
					value: StudioPanelTab.WebCreator,
				},
			]}
			value={currentMode}
			onChange={(value) => {
				setCurrentMode(value as any);
			}}
		/>
	);
}
