import NiceModal, { useModal } from "@ebay/nice-modal-react";
import { Modal, message, Tooltip, Typography } from "antd";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { ToolsApi, WorkflowApi } from "@/api";
import { CloseIcon } from "@/components/common/CustomModal";
import ModelSelecter from "@/components/common/ModelSelecter";
import { ToolSvgIconBox } from "@/components/common/SvgIconBox";
import type { AgentDetail } from "@/types/agent";
import AddToolsModal from "./AddToolsModal";

export default NiceModal.create(
	({ data, workflowId }: { data: AgentDetail; workflowId: string }) => {
		const modal = useModal();
		const { t } = useTranslation();
		const [systemPrompt, setSystemPrompt] = useState(data.instruction || "");

		const [selectedModel, setSelectedModel] = useState(data.model || "");
		const [loading, setLoading] = useState(false);

		const [toolIds, setToolIds] = useState<string[]>(data.tools || []);

		const { data: _allToolsList, isLoading: _isLoadingAllTools } =
			ToolsApi.useAgentToolsList();

		const handleOk = async () => {
			if (!systemPrompt.trim()) {
				message.error(t("agentDetailModal.systemPromptRequired"));
				return;
			}

			setLoading(true);
			try {
				console.log("workflowId------: ", workflowId);
				// call update agent interface
				await WorkflowApi.updateWorkflowAgent(workflowId!, data.name, {
					instruction: systemPrompt,
					tools: toolIds,
					model: selectedModel,
				});
				message.success(t("agentDetailModal.updateSuccess"));
				modal.resolve(true);
			} catch (error) {
				message.error(t("agentDetailModal.updateFailed"));
				console.error("Update failed:", error);
			} finally {
				setLoading(false);
			}
		};

		const handleAddTools = async () => {
			const _toolIds = await NiceModal.show(AddToolsModal, {
				toolIds: toolIds || [],
			});
			if (Array.isArray(_toolIds) && _toolIds.length) {
				setToolIds((prev) => [...prev, ..._toolIds]);
			}
		};

		const handleDeleteTool = (toolId: string) => {
			setToolIds((prev) => prev.filter((id) => id !== toolId));
		};

		return (
			<Modal
				title={data.name}
				onOk={handleOk}
				open={modal.visible}
				onCancel={() => modal.hide()}
				afterClose={() => modal.remove()}
				width="95%"
				confirmLoading={loading}
				okText={t("common.confirm")}
				cancelText={t("common.cancel")}
			>
				<div className="flex gap-2 items-stretch h-[60vh]">
					<div className="flex p-4 flex-col flex-1 min-w-0 bg-grey-layer2-normal rounded-xl shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal)]">
						<div className="mt-3 font-[600] text-text-primary-1">
							{t("agentDetailModal.input")}
						</div>
						<div className="flex-1 p-2.5 overflow-auto custom-scrollbar">
							<pre className="whitespace-pre-wrap text-sm font-mono">
								{data.structured_output_schema &&
								typeof data.structured_output_schema === "object"
									? JSON.stringify(data.structured_output_schema, null, 2)
									: data.structured_output_schema}
							</pre>
						</div>
					</div>
					<div className="flex p-4 flex-col flex-1 min-w-0 bg-grey-layer2-normal rounded-xl shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal)]">
						<div className="mt-3 font-[600] text-text-primary-1">
							{t("agentDetailModal.settings")}
						</div>
						{/* TODO: model selection*/}
						<div className="p-2.5 flex flex-col gap-2 overflow-auto">
							<div className="text-text-primary-1 text-sm  leading-5">
								<span className="text-red-500">*</span>
								<span className="font-[600]">
									{t("agentDetailModal.selectModel")}
								</span>
							</div>
							<div>
								<ModelSelecter
									value={selectedModel}
									onChange={setSelectedModel}
								/>
							</div>
						</div>
						{/* TODO: add toolset */}
						<div className="flex-1 p-2.5 flex flex-col gap-2 overflow-auto">
							<div className="text-text-primary-1 text-sm  leading-5 flex items-center">
								<span className="text-red-500">*</span>
								<span className="font-[600]">
									{t("agentDetailModal.toolsets")}
								</span>
								<Tooltip title={t("agentToolsModal.title")}>
									<button
										className="text-text-primary-2 ml-auto text-xl font-dmSans hover:bg-grey-fill1-hover px-2 rounded-lg"
										onClick={() => handleAddTools()}
									>
										+
									</button>
								</Tooltip>
							</div>
							<div className="flex flex-col gap-3 overflow-auto custom-scrollbar max-h-40  ">
								{toolIds.length ? (
									toolIds.map((toolId: string) => (
										<div
											key={toolId}
											className="flex items-center gap-2 text-text-primary-2"
										>
											<div className="flex items-center gap-2.5 flex-1 min-w-0">
												{/* tool image */}
												<div className="w-9">
													<ToolSvgIconBox
														className="!size-9"
														svgString={null}
													/>
												</div>
												<div className="flex flex-col justify-between min-w-0 w-full">
													<Typography.Text
														className="block w-full truncate font-[600] !text-sm"
														ellipsis={{
															tooltip: {
																title:
																	_allToolsList?.find(
																		(tool) => tool.name === toolId,
																	)?.name || toolId,
															},
														}}
													>
														{_allToolsList?.find((tool) => tool.name === toolId)
															?.name || toolId}
													</Typography.Text>
													<Typography.Text
														className="!block !text-text-primary-3 !text-xs"
														ellipsis={{
															tooltip: {
																title: _allToolsList?.find(
																	(tool) => tool.name === toolId,
																)?.description,
															},
														}}
													>
														{
															_allToolsList?.find(
																(tool) => tool.name === toolId,
															)?.description
														}
													</Typography.Text>
												</div>
												{/* Location services, directions, and place details */}
											</div>
											<Tooltip title="Delete">
												<button
													className="text-text-primary-2 ml-auto text-xl font-dmSans hover:bg-grey-fill1-hover p-1 rounded"
													onClick={() => handleDeleteTool(toolId)}
												>
													<CloseIcon className="w-4 h-4" />
												</button>
											</Tooltip>
										</div>
									))
								) : (
									<div>{t("agentDetailModal.noTools")}</div>
								)}
							</div>

							<div className="text-text-primary-1 text-sm  leading-5">
								<span className="text-red-500">*</span>
								<span className="font-[600]">
									{t("agentDetailModal.systemPrompt")}
								</span>
							</div>
							<textarea
								value={systemPrompt}
								onChange={(e) => setSystemPrompt(e.target.value)}
								placeholder={t("agentDetailModal.systemPromptPlaceholder")}
								className="w-full flex-1 overflow-auto rounded-xl bg-grey-fill2-normal p-2.5 resize-none text-text-primary-2 custom-scrollbar"
							></textarea>
						</div>
					</div>
					<div className="flex p-4 flex-col flex-1 min-w-0 bg-grey-layer2-normal rounded-xl shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal)]">
						<div className="mt-3 font-[600] text-text-primary-1">
							{t("agentDetailModal.output")}
						</div>
						<div className="flex-1 p-2.5 overflow-auto custom-scrollbar">
							<pre className="whitespace-pre-wrap text-sm font-mono ">
								{data.structured_output_schema &&
								typeof data.structured_output_schema === "object"
									? JSON.stringify(data.structured_output_schema, null, 2)
									: data.structured_output_schema}
							</pre>
						</div>
					</div>
				</div>
			</Modal>
		);
	},
);
