import { useState } from "react";
import { useTranslation } from "react-i18next";
import { match } from "ts-pattern";
import Tabs from "@/components/common/Tabs";
import { cn } from "@/utils";
import HistoryList from "./HistoryList";

export default function HistorySection() {
	const { t } = useTranslation();

	const tabs = [
		{
			label: t("home.history.tabs.myAiApp"),
			value: "history",
		},
		// {
		// 	label: t("home.history.tabs.tools"),
		// 	value: "tools",
		// },
	];

	const [activeTab, setActiveTab] = useState("history");

	return (
		<div>
			<div
				className={cn(
					"sticky end-0 start-0 top-0 flex items-center justify-between  transition-all py-4",
					"z-1 bg-grey-layer1-semitrans2 backdrop-blur-[50px]",
				)}
			>
				<Tabs
					type="underline"
					tabs={tabs}
					value={activeTab}
					onChange={(tab) => {
						setActiveTab(tab);
					}}
				/>
			</div>
			<div className="mt-3">
				{match(activeTab)
					.with("history", () => <HistoryList />)
					.otherwise(() => (
						<HistoryList />
					))}
			</div>
		</div>
	);
}
