import NiceModal, { useModal } from "@ebay/nice-modal-react";
import { Button, Input, message } from "antd";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import CustomModal, { CloseIcon } from "@/components/common/CustomModal";

function RenameWorkflowModal({
	workflowName,
	onRename,
}: {
	workflowName: string;
	onRename: (newName: string) => Promise<void>;
}) {
	const modal = useModal();
	const { t } = useTranslation();

	const [value, setValue] = useState(workflowName);
	const [inputIsError, setInputError] = useState(false);
	const [isLoading, setIsLoading] = useState(false);

	useEffect(() => {
		setValue(workflowName);
	}, [workflowName]);

	// Ensure input resets to latest name whenever modal opens
	useEffect(() => {
		if (modal.visible) {
			setInputError(false);
			setValue(workflowName);
		}
	}, [modal.visible, workflowName]);

	const handleRename = async () => {
		if (!value.trim()) {
			message.warning(t("home.renameModal.nameRequired"));
			return;
		}
		setIsLoading(true);
		try {
			await onRename(value);
			modal.hide();
		} catch (error) {
			message.error(
				error instanceof Error
					? error.message
					: t("home.renameModal.unknownError"),
			);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<CustomModal
			open={modal.visible}
			width={480}
			onClose={modal.hide}
			maskClosable={false}
			hideCloseIcon
		>
			<div className="flex h-[56px] items-center gap-6 pe-4 ps-6">
				<div className="text-[18px] font-semibold text-color-text-primary-1">
					{t("home.renameModal.title")}
				</div>
				<CloseIcon
					className="ms-auto size-[26px]"
					size={14}
					onClick={modal.hide}
				/>
			</div>
			<div className="px-6 py-1">
				<Input
					maxLength={50}
					placeholder={t("home.renameModal.placeholder")}
					className="rounded-[8px]"
					allowClear={{ clearIcon: <CloseIcon size={14} /> }}
					value={value}
					onChange={(e) => {
						setInputError(false);
						setValue(e.target.value);
					}}
					status={inputIsError ? "error" : undefined}
					onPressEnter={() => handleRename()}
				/>
			</div>

			<div className="flex justify-end gap-3 px-6 py-4 pb-6 items-center">
				<button
					className="cursor-pointer hover:bg-grey-fill2-hover  bg-grey-fill2-normal text-text-primary-1 px-4.5 py-1.5 rounded-lg"
					onClick={() => modal.hide()}
				>
					{t("common.cancel")}
				</button>

				<Button type="primary" onClick={handleRename} loading={isLoading}>
					{t("common.confirm")}
				</Button>
			</div>
		</CustomModal>
	);
}

export default NiceModal.create(RenameWorkflowModal);
