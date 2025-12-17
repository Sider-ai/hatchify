import { CloseOutlineM } from "@hatchify/icons";
import { Modal, type ModalProps } from "antd";
import { cn } from "@/utils";

export default function CustomModal({
	onClose,
	children,
	hideCloseIcon,
	...rest
}: ModalProps & {
	onClose?: () => void;
	hideCloseIcon?: boolean;
}) {
	return (
		<Modal
			title={null}
			footer={null}
			closable={false}
			centered
			maskClosable
			width={480}
			zIndex={2000}
			destroyOnHidden
			styles={{
				mask: {
					backgroundColor: "rgba(12, 13, 25, 0.2)",
				},
				container: {
					padding: 0,
				},
			}}
			onCancel={() => onClose?.()}
			{...rest}
		>
			<div className="relative">
				{!hideCloseIcon && onClose && (
					<CloseIcon
						className="absolute end-1 top-1 size-[26px]"
						size={14}
						onClick={onClose}
					/>
				)}
				{children}
			</div>
		</Modal>
	);
}

export function CloseIcon({
	type = "default",
	className,
	size = 12,
	onClick,
}: {
	type?: "default" | "glass";
	className?: string;
	size?: number;
	onClick?: () => void;
}) {
	return (
		<span
			className={cn(
				"backdrop-filter-[8px] z-1 size-5 shrink-0 cursor-pointer rounded-full border-none outline-none transition-colors flex-center",
				type === "default"
					? "bg-transparent text-text-primary-4 hover:bg-grey-fill1-hover hover:text-text-primary-2"
					: "bg-glass-fill1-normal text-text-white-1 hover:bg-glass-fill1-hover",
				className,
			)}
			onClick={onClick}
		>
			<CloseOutlineM className="shrink-0" size={size} />
		</span>
	);
}
