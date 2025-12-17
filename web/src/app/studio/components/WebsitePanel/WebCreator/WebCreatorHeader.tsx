import {
	BackArrowLeft as Back,
	DevicePhoneOutline as DevicePhone,
	ArrowRight as Forward,
	Retry,
	StarDefault as StarIcon,
	Webpage as WebPageIcon,
} from "@hatchify/icons";
import { Modal, Tooltip } from "antd";
import { motion } from "motion/react";
import React, { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useShallow } from "zustand/react/shallow";
import useWebCreatorStore from "@/stores/webcreator";
import { useWebsiteHistory } from "@/stores/webcreator/history";
import useWebPreviewStore from "@/stores/webcreator/preview";
import { cn } from "@/utils";
import { WebCreatorTab } from "./types";

function WebCreatorHeader() {
	const { t } = useTranslation();
	const [iframeError, setIframeError] = useState<string>("");
	const { back, forward } = useWebsiteHistory();

	const { title, reload, goBack, goForward } = useWebPreviewStore(
		useShallow((state) => ({
			title: state.title,
			reload: state.reload,
			goBack: state.goBack,
			goForward: state.goForward,
		})),
	);
	const { currentTab, setCurrentTab } = useWebCreatorStore(
		useShallow((state) => ({
			currentTab: state.currentTab,
			setCurrentTab: state.setCurrentTab,
		})),
	);

	useEffect(() => {
		const controller = new AbortController();
		window.addEventListener(
			"message",
			(event) => {
				if (event.data.type === "iframeError") {
					setIframeError(event.data.error.stack ?? event.data.error.message);
				}
			},
			{ signal: controller.signal },
		);
		return () => {
			controller.abort();
		};
	}, []);

	useEffect(() => {
		if (iframeError) {
		}
	}, [iframeError]);

	const [errorDetailsModal, setErrorDetailsModal] = useState<boolean>(false);

	return (
		<header className="h-14 flex items-center px-5 bg-grey-layer3-normal">
			<Tab currentTab={currentTab} setCurrentTab={setCurrentTab} />
			<div className="flex-1 flex">
				<div className="flex px-2 items-center text-text-primary-3">
					<Tooltip title={t("webcreator.header.actions.back")}>
						<button
							disabled={!back}
							className="disabled:text-text-primary-3 size-8 active:scale-95 flex-center hover:bg-grey-fill1-hover rounded-sm text-text-primary-1"
							onClick={goBack}
						>
							<Back />
						</button>
					</Tooltip>
					<Tooltip title={t("webcreator.header.actions.forward")}>
						<button
							disabled={!forward}
							className="disabled:text-text-primary-3 size-8 active:scale-95 flex-center hover:bg-grey-fill1-hover rounded-sm text-text-primary-1"
							onClick={goForward}
						>
							<Forward />
						</button>
					</Tooltip>
					<Tooltip title={t("webcreator.header.actions.reload")}>
						<button
							className="size-8 active:scale-95 flex-center hover:bg-grey-fill1-hover rounded-sm text-text-primary-1"
							onClick={reload}
						>
							<Retry />
						</button>
					</Tooltip>
				</div>
				<div className="flex-1 rounded-lg bg-grey-fill2-normal h-8 flex items-center px-2">
					<span className="text-text-primary-5 text-sm">{title}</span>
				</div>

				<div className="flex items-center gap-2 ml-4">
					{false && (
						<button
							className="flex py-1.5 px-3.5 gap-2 justify-center items-center rounded-full bg-assistive-blue-bg text-assistive-blue-normal"
							onClick={() => {
								// NiceModal.show(DiagnosisModal, {
								//   onShowDetails: () => {
								//     setErrorDetailsModal(true)
								//   },
								//   onAutoFix: () => {
								//     webcreatorChat(`${t('webcreator.pleaseFix')}: ${buildError.message}`)
								//     NiceModal.hide(DiagnosisModal)
								//   },
								// })
							}}
						>
							<StarIcon />
							<span>{t("webcreator.header.actions.fixIssues")}</span>
						</button>
					)}
				</div>
				<Modal
					open={errorDetailsModal}
					onCancel={() => setErrorDetailsModal(false)}
					footer={null}
					centered
					title={t("webcreator.header.details")}
					zIndex={9999}
					className="w-[752px]"
				>
					123
					{/* <div>{buildError?.message ?? iframeError}</div> */}
				</Modal>
			</div>
		</header>
	);
}

function Tab({
	currentTab,
	setCurrentTab,
}: {
	currentTab: WebCreatorTab;
	setCurrentTab: (tab: WebCreatorTab) => void;
}) {
	const { t } = useTranslation();
	const tabs = [
		// {
		//   label: <CodeEditIcon />,
		//   value: WebCreatorTab.Code,
		//   title: t('webcreator.header.tabs.code'),
		// },
		{
			label: <WebPageIcon />,
			value: WebCreatorTab.Preview,
			title: t("webcreator.header.tabs.desktop"),
		},
		{
			label: <DevicePhone />,
			value: WebCreatorTab.Phone,
			title: t("webcreator.header.tabs.mobile"),
		},
	];

	// 计算当前选中tab的位置
	const currentTabIndex = useMemo(() => {
		return tabs.findIndex((tab) => tab.value === currentTab);
	}, [currentTab]);

	const handleTabClick = (tab: WebCreatorTab) => {
		setCurrentTab(tab);
	};

	return (
		<div className="h-8 flex p-[3px] gap-[3px] rounded-md bg-grey-layer1-semitrans items-center relative">
			{/* 移动的背景选中块 */}
			<motion.div
				className="absolute h-[26px] w-[26px] bg-grey-layer3-normal rounded-md"
				animate={{
					x: currentTabIndex * 29, // 26px宽度 + 3px间距
				}}
				transition={{
					type: "spring",
					stiffness: 400,
					damping: 30,
					duration: 0.3,
				}}
			/>
			{tabs.map((tab) => (
				<Tooltip title={tab.title} key={tab.value}>
					<div
						className={cn(
							"h-full w-[26px] flex items-center justify-center z-10 cursor-pointer hover:scale-110 transition-transform duration-200",
							{
								"text-text-primary-1": tab.value === currentTab,
								"text-text-primary-3": tab.value !== currentTab,
							},
						)}
						onClick={() => handleTabClick(tab.value)}
					>
						{tab.label}
					</div>
				</Tooltip>
			))}
		</div>
	);
}

export default React.memo(WebCreatorHeader);
