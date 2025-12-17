import { useAsyncEffect } from "ahooks";
import { Spin } from "antd";
import React, { useEffect, useMemo, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import { useStudioParams } from "@/hooks/useStudioParams";
import useWebCreatorStore from "@/stores/webcreator";
import { useWebsiteHistory } from "@/stores/webcreator/history";
import useWebPreviewStore from "@/stores/webcreator/preview";
import { getPreviewUrl } from "@/utils/getPreviewUrl";
import WaitLock from "@/utils/WaitLock";
import { WebCreatorTab } from "./types";

function WebCreatorPreview() {
	const iframeRef = useRef<HTMLIFrameElement>(null);
	const { pending, previewResult, currentTab } = useWebCreatorStore(
		useShallow((state) => ({
			pending: state.pending,
			previewResult: state.previewResult,
			currentTab: state.currentTab,
		})),
	);

	const { reloadIndex, setIframeRef, setTitle } = useWebPreviewStore(
		useShallow((state) => ({
			reloadIndex: state.reloadIndex,
			setIframeRef: state.setIframeRef,
			setTitle: state.setTitle,
		})),
	);
	const isMobileView = useMemo(
		() => currentTab === WebCreatorTab.Phone,
		[currentTab],
	);

	const iframeReadyLock = useMemo(() => new WaitLock(), []);

	const { addHistory, setHistoryIdx, reload } = useWebsiteHistory(true);

	useEffect(() => {
		if (iframeRef.current) {
			const controller = new AbortController();

			// 监听iframe的load事件
			iframeRef.current.addEventListener(
				"load",
				() => {
					iframeReadyLock.unlock();
					reload();
				},
				{ signal: controller.signal },
			);

			// 通过postMessage监听来自iframe的路由变化事件
			window.addEventListener(
				"message",
				(event) => {
					// 验证消息来源（可选，根据实际情况调整）
					// if (event.origin !== expectedOrigin) return

					const { type, data } = event.data;

					if (type === "popstate") {
						setHistoryIdx(data.idx);
					} else if (type === "custom-pushstate") {
						addHistory();
					}
				},
				{ signal: controller.signal },
			);

			setIframeRef(iframeRef.current);
			return () => {
				controller.abort();
			};
		}
	}, []);

	const handleReload = async () => {
		if (iframeRef.current) {
			iframeReadyLock.lock();

			// 通过重新设置src来实现reload，避免跨域安全问题
			const currentSrc = iframeRef.current.src;
			iframeRef.current.src = currentSrc;

			await iframeReadyLock.wait();
			setTitle("/");
			console.log("reload");
		}
	};

	useAsyncEffect(async () => {
		return await handleReload();
	}, [previewResult]);

	useEffect(() => {
		if (reloadIndex !== 0) {
			handleReload();
		}
	}, [reloadIndex]);

	const { workflowId } = useStudioParams();
	const iframeUrl = getPreviewUrl(workflowId || "");

	return (
		<div
			className="h-full max-h-full transition-[width] duration-300 relative"
			style={{
				width: isMobileView ? "440px" : "100%",
			}}
		>
			<iframe
				src={iframeUrl}
				className="size-full overflow-hidden border-none outline-none"
				ref={iframeRef}
				title="WebCreator Preview"
			></iframe>

			{pending && (
				<div className="absolute inset-0 bg-black/20 flex justify-center items-center">
					<Spin
						// tip="Loading"
						size="large"
					/>
				</div>
			)}
			{/* {!building && !pending && generateError !== null && (
				<div className="absolute inset-0 bg-black/20 flex justify-center items-center px-8">
					<Alert
						message={
							generateError instanceof WebCreatorBuildError
								? "WebCreator Build Error"
								: "WebCreator Generate Error"
						}
						description={generateError?.message}
						type="info"
					/>
				</div>
			)} */}
		</div>
	);
}

export default React.memo(WebCreatorPreview);
