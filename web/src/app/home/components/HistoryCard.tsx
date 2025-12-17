import { DeleteOutline, Edit1, MoreH } from "@hatchify/icons";
import { Popover } from "antd";
import { type FC, useState } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/utils";

interface HistoryCardProps {
	image_url: string;
	title: string;
	workflowId: string;
	onClick: (workflowId: string) => void;
	onDelete: (workflowId: string) => void;
	updated_at: string;
	created_at: string;
	onRename: (workflowName: string, workflowId: string) => void;
}

const PopoverContent: FC<{
	onDelete: () => void;
	onRename: () => void;
}> = ({ onDelete, onRename }) => {
	const { t } = useTranslation();
	return (
		<div className="flex flex-col gap-0.5 p-0.5">
			<div
				className="flex h-8 min-w-[144px] cursor-pointer items-center gap-1.5 rounded-[10px]  px-[9px] text-text-primary-1 transition-colors hover:bg-grey-fill1-hover"
				onClick={onRename}
			>
				<Edit1 size={14} />
				<span> {t("home.renameModal.title")}</span>
			</div>

			<div
				className="flex h-8 min-w-[144px] cursor-pointer items-center gap-1.5 rounded-[10px]  px-[9px] text-text-primary-1 transition-colors hover:bg-error-bg hover:text-error-normal"
				onClick={(e) => {
					e.stopPropagation();
					onDelete();
				}}
			>
				<DeleteOutline size={14} />
				<span>{t("common.delete")}</span>
			</div>
		</div>
	);
};

export default function HistoryCard({
	image_url,
	title,
	workflowId,
	onClick,
	onDelete,
	updated_at,
	onRename,
}: HistoryCardProps) {
	const [popOpen, setPopOpen] = useState(false);
	return (
		<div
			style={{
				boxShadow: "0 0 0 1px var(--color-grey-line2-normal)",
			}}
			className="flex flex-col items-start w-full group rounded-xl bg-grey-layer2-normal"
		>
			<div
				onClick={() => onClick(workflowId)}
				className="relative overflow-hidden flex h-[170px] text-text-secondary-3 flex-center size-full object-cover border border-grey-line1-normal w-full bg-clip-content rounded-t-xl text-center items-center justify-center"
			>
				<img
					src={image_url || "/default-cover.png"}
					alt="sider"
					className="size-full  object-cover group:hover:hidden group-hover:scale-110 duration-200"
				/>
				{/* <div
					style={{
						background:
							"linear-gradient(180deg, var(--color-text-white-5) 0%, var(--color-text-black-5) 100%)",
					}}
					className="absolute inset-0  rounded-lg group-hover:block hidden"
				/> */}
			</div>
			<div className="px-4 py-3 flex flex-col gap-2 w-full">
				<div
					title={title}
					style={{
						fontFeatureSettings: "'liga' off",
					}}
					className="text-text-primary-1 leading-5 font-[500] text-sm truncate max-w-full"
				>
					{title}
				</div>
				<div className="flex items-center font-[DM_Sans] justify-between w-full">
					<div className="text-text-primary-4 leading-5  mr-auto">
						{new Date(updated_at).toLocaleDateString()}
					</div>
					<Popover
						trigger={["click"]}
						placement="topRight"
						content={
							<PopoverContent
								onDelete={() => onDelete(workflowId)}
								onRename={() => {
									onRename(title, workflowId);
								}}
							/>
						}
						overlayInnerStyle={{
							padding: "8px",
						}}
						arrow={false}
						onOpenChange={(open) => {
							setPopOpen(open);
						}}
					>
						<button
							className={cn(
								" p-1.5 transition-colors hover:bg-grey-fill1-hover",
								popOpen && "bg-grey-fill1-hover",
							)}
						>
							<MoreH size={14} className="text-text-primary-3" />
						</button>
					</Popover>
				</div>
			</div>
		</div>
	);
}
