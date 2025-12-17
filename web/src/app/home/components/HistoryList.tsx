import NiceModal from "@ebay/nice-modal-react";
import { Loading } from "@hatchify/icons";
import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import { App, Empty } from "antd";
import { useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { WorkflowApi } from "@/api";
import DeleteConfirmModal from "@/components/common/DeleteConfirmModal";
import type { WorkflowListItem } from "@/types/workflow";
import HistoryCard from "./HistoryCard";
import RenameWorkflowModal from "./RenameModel";

const PAGE_SIZE = 20;

export default function WorkflowList() {
	const { t } = useTranslation();
	const navigate = useNavigate();

	const queryClient = useQueryClient();

	const { message } = App.useApp();

	const {
		data,
		isLoading,
		isFetchingNextPage,
		fetchNextPage,
		hasNextPage,
		isSuccess,
	} = useInfiniteQuery({
		queryKey: ["workflows", { pageSize: PAGE_SIZE }],
		queryFn: async ({ pageParam = 1 }) => {
			return WorkflowApi.fetchWorkflowList({
				page: pageParam,
				size: PAGE_SIZE,
			});
		},
		initialPageParam: 1,
		getNextPageParam: (lastPage, allPages) => {
			try {
				const pages = Array.isArray(allPages) ? allPages : [];
				const total = lastPage?.data?.total ?? 0;
				const loaded = pages.reduce((acc, p) => {
					const items = Array.isArray(p?.data?.list) ? p.data.list : [];
					return acc + items.length;
				}, 0);
				return loaded < total ? pages.length + 1 : undefined;
			} catch {
				return undefined;
			}
		},
	});

	useEffect(() => {
		const handleScroll = () => {
			const scrollPosition = window.innerHeight + window.scrollY;
			const threshold = document.documentElement.scrollHeight - 300;
			if (
				scrollPosition >= threshold &&
				isSuccess &&
				hasNextPage &&
				!isFetchingNextPage
			) {
				fetchNextPage();
			}
		};
		window.addEventListener("scroll", handleScroll, { passive: true });
		handleScroll();
		return () => window.removeEventListener("scroll", handleScroll);
	}, [isSuccess, hasNextPage, isFetchingNextPage, fetchNextPage]);

	const handleDelete = useCallback(
		async (id: string) => {
			NiceModal.show(DeleteConfirmModal, {
				onConfirm: async () => {
					try {
						await WorkflowApi.deleteWorkflow(id);
						queryClient.setQueryData(
							["workflows", { pageSize: PAGE_SIZE }],
							(old: any) => {
								if (!old) return old;
								let removed = false;
								const pages = old.pages.map((p: any) => {
									const before = p?.data?.list || [];
									const after = before.filter(
										(item: WorkflowListItem) => item.id !== id,
									);
									if (after.length !== before.length) removed = true;
									return { ...p, data: { list: after } };
								});
								if (removed) {
									for (const p of pages) {
										if (
											p.pagination &&
											typeof p.pagination.total === "number"
										) {
											p.pagination = {
												...p.pagination,
												total: Math.max(0, p.pagination.total - 1),
											};
											break;
										}
									}
								}
								return { ...old, pages };
							},
						);
						message.success("Deleted successfully");
					} catch (error) {
						console.error("Failed to delete:", error);
					}
				},
			});
		},
		[queryClient],
	);

	const handleRename = useCallback(
		(workflowName: string, workflowId: string) => {
			NiceModal.show(RenameWorkflowModal, {
				workflowName,
				onRename: async (newName) => {
					await WorkflowApi.updateWorkflowByID(workflowId, {
						name: newName,
					});
					/// 使用react-query的invalidateQueries来更新数据
					queryClient.invalidateQueries({
						queryKey: ["workflows", { pageSize: PAGE_SIZE }],
					});
					message.success("Renamed successfully");
				},
			});
		},
		[],
	);

	const handleClick = useCallback(
		(workflowId: string) => {
			navigate(`/studio/${workflowId}`);
		},
		[navigate],
	);
	// Get all workflows from cached pages
	const allWorkflows = data?.pages?.flatMap((p) => p?.data?.list || []) || [];
	return (
		<div>
			{allWorkflows.length ? (
				<div className="grid w-full grid-cols-[repeat(auto-fill,_minmax(260px,_1fr))] gap-x-6 gap-y-8">
					{allWorkflows.map((item) => (
						<HistoryCard
							key={item.id}
							image_url={"/default-cover.png"}
							title={item.name}
							workflowId={item.id}
							onClick={handleClick}
							onDelete={handleDelete}
							onRename={handleRename}
							updated_at={item.updated_at}
							created_at={item.created_at}
						/>
					))}
				</div>
			) : (
				!isLoading && (
					<div className="text-text-primary-1 text-sm">
						<Empty />
					</div>
				)
			)}

			{(isLoading || isFetchingNextPage) && (
				<div className="flex items-center justify-center gap-2 px-[10px] py-4 text-text-primary-1">
					<Loading size={14} className="animate-spin" />
					{t("common.loading")}
				</div>
			)}
		</div>
	);
}
