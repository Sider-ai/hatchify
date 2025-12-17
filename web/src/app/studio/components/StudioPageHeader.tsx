import NiceModal from "@ebay/nice-modal-react";
import { Homepage as HomepageIcon, TextLogo } from "@hatchify/icons";
import { useQueryClient } from "@tanstack/react-query";
import { Typography } from "antd";
import { useCallback } from "react";
import { WorkflowApi } from "@/api";
import RenameWorkflowModal from "@/app/home/components/RenameModel";

interface StudioPageHeaderProps {
	projectName: string;
	workflowId?: string;
	middleComponent?: React.ReactNode;
	rightComponent: React.ReactNode[];
	redirectToLogin?: boolean;
	canEditName?: boolean;
}

const StudioPageHeader: React.FC<StudioPageHeaderProps> = ({
	projectName,
	workflowId,
	middleComponent,
	rightComponent,
	redirectToLogin = false,
	canEditName = false,
}) => {
	const queryClient = useQueryClient();

	const openRenameModal = useCallback(() => {
		if (!workflowId) return;
		NiceModal.show(RenameWorkflowModal, {
			workflowName: projectName,
			onRename: async (newName: string) => {
				await WorkflowApi.updateWorkflowByID(workflowId, { name: newName });
				await Promise.all([
					queryClient.invalidateQueries({
						queryKey: ["workflowDetail", workflowId],
					}),
					queryClient.invalidateQueries({ queryKey: ["workflows"] }),
				]);
			},
		});
	}, [projectName, queryClient, workflowId]);

	return (
		<header className="relative flex items-center h-14 px-2 gap-2 shrink-0 rounded-xl bg-grey-layer1-white">
			<a
				className="flex justify-center items-center p-1 rounded gap-2 !text-text-primary-1 hover:!text-text-primary-2"
				href="/"
			>
				<TextLogo className="size-24" />
				<HomepageIcon className="size-4" />
			</a>
			<Typography.Text
				className="text-text-primary-1 font-semibold px-2 text-sm !max-w-[300px] truncate cursor-pointer"
				onClick={canEditName ? openRenameModal : () => {}}
				ellipsis={{
					tooltip: { title: projectName },
				}}
			>
				{projectName}
			</Typography.Text>

			{middleComponent && (
				<div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
					{middleComponent}
				</div>
			)}

			<div className="ml-auto flex items-center gap-2">{rightComponent}</div>
		</header>
	);
};

export default StudioPageHeader;
