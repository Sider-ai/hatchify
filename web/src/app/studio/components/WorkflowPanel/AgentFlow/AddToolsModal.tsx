import NiceModal, { useModal } from "@ebay/nice-modal-react";
import { Loading } from "@hatchify/icons";
import { Modal, Typography } from "antd";
import { debounce } from "lodash";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { ToolsApi } from "@/api";
import { ToolSvgIconBox } from "@/components/common/SvgIconBox";

type Props = {
	toolIds?: string[];
	isSelectToolModal?: boolean;
};

export default NiceModal.create(
	({ toolIds, isSelectToolModal = true }: Props) => {
		const modal = useModal();
		const { t } = useTranslation();
		const [loading] = useState(false);
		const [search, setSearch] = useState("");
		const [debouncedSearch, setDebouncedSearch] = useState("");
		const setDebouncedSearchSafely = useMemo(
			() => debounce((value: string) => setDebouncedSearch(value), 300),
			[],
		);

		const [selectedToolIds, setSelectedToolIds] = useState<string[]>(
			toolIds || [],
		);

		const handleOk = async () => {
			modal.resolve(selectedToolIds.filter((id) => !toolIds?.includes(id)));
			modal.hide();
		};

		const [activeTagId, setActiveTagId] = useState<string | undefined>(
			undefined,
		);
		const { data: tools, isLoading } = ToolsApi.useAgentToolsList();
		const filteredTools = useMemo(() => {
			if (!tools || !Array.isArray(tools)) return [];
			const keyword = debouncedSearch.trim().toLowerCase();
			if (!keyword) return tools;
			return tools.filter((tool: any) => {
				const name = String(tool.tool_name || "").toLowerCase();
				const desc = String(tool.description || "").toLowerCase();
				return name.includes(keyword) || desc.includes(keyword);
			});
		}, [tools, debouncedSearch]);

		const handleAddTool = (toolId: string) => {
			// if already added, remove it
			if (selectedToolIds.includes(toolId)) {
				setSelectedToolIds((prev) => prev.filter((id) => id !== toolId));
			} else {
				setSelectedToolIds((prev) => [...prev, toolId]);
			}
		};

		return (
			<Modal
				title={t("agentToolsModal.title")}
				onOk={handleOk}
				open={modal.visible}
				onCancel={() => modal.hide()}
				afterClose={() => modal.remove()}
				width="55%"
				confirmLoading={loading}
				okText={t("common.confirm")}
				cancelText={t("common.cancel")}
				footer={isSelectToolModal ? undefined : null}
			>
				<div className="flex gap-4 h-[70vh]">
					{/* Left categories */}
					<aside className="w-[240px] shrink-0 bg-grey-layer2-normal rounded-xl shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal)] p-2.5 overflow-auto">
						<div className="text-text-primary-1 text-sm font-[600] px-2 py-1.5">
							{t("agentToolsModal.categories")}
						</div>
						<ul className="flex flex-col gap-1">
							<li
								key="all"
								className={`px-3 py-2 rounded-lg cursor-pointer hover:bg-grey-fill1-hover ${!activeTagId ? "bg-grey-fill1-hover2" : ""} text-text-primary-1`}
								onClick={() => setActiveTagId(undefined)}
							>
								{t("agentToolsModal.all")}
							</li>
						</ul>
					</aside>

					{/* Right content */}
					<section className="flex-1 min-w-0 bg-grey-layer2-normal rounded-xl shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal)] p-4 flex flex-col">
						{/* Search */}
						<div className="mb-3">
							<input
								placeholder={t("agentToolsModal.searchPlaceholder")}
								value={search}
								onChange={(e) => {
									const value = e.target.value;
									setSearch(value);
									setDebouncedSearchSafely(value);
								}}
								className="w-full rounded-lg px-3 py-2 bg-grey-fill2-normal text-text-primary-2 outline-none focus:shadow-[0_0_0_2px_var(--color-focus-primary-1)]"
							/>
						</div>

						{/* Tools list */}
						<div className="flex-1 overflow-auto custom-scrollbar">
							{isLoading ? (
								<div className="flex items-center justify-center h-full">
									<Loading className="animate-spin w-6 h-6" />
								</div>
							) : (
								<div className="flex flex-col divide-y-[1px] divide-grey-line1-normal">
									{filteredTools?.map((tool) => (
										<div
											className="flex items-center gap-3 py-3"
											key={tool.name}
										>
											<ToolSvgIconBox className="!size-10" svgString={null} />
											<div className="flex-1 min-w-0 flex flex-col justify-between gap-1">
												<Typography.Text
													className="!text-text-primary-1 !font-[600] !text-sm"
													ellipsis={{
														tooltip: {
															title: tool.name || tool.name,
														},
													}}
												>
													{tool.name || tool.name}
												</Typography.Text>
												<Typography.Text
													className="!text-text-primary-3 !text-xs"
													ellipsis={{
														tooltip: { title: tool.description },
													}}
												>
													{tool.description}
												</Typography.Text>
											</div>
											{isSelectToolModal && (
												<button
													className={`px-3 py-1.5 rounded-full text-sm text-text-primary-1 hover:bg-grey-fill1-hover shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal)] ${
														selectedToolIds.includes(tool.name)
															? "bg-grey-fill1-hover2 hover:bg-grey-fill1-hover2"
															: ""
													}`}
													onClick={() => handleAddTool(tool.name)}
												>
													<span>
														{selectedToolIds.includes(tool.name)
															? t("agentToolsModal.added")
															: t("agentToolsModal.add")}
													</span>
												</button>
											)}
										</div>
									))}
								</div>
							)}
						</div>
					</section>
				</div>
			</Modal>
		);
	},
);
