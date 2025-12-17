import NiceModal, { useModal } from "@ebay/nice-modal-react";
import { ExclamationMarkTriangleFilledWarning as IconWarning } from "@hatchify/icons";
import { Button as AntdButton } from "antd";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import CustomModal from "@/components/common/CustomModal";

interface DeleteConfirmModalProps {
	onConfirm: () => Promise<void>;
	title?: string;
	description?: string;
	confirmText?: string;
}

export default NiceModal.create(
	({ onConfirm, title, description, confirmText }: DeleteConfirmModalProps) => {
		const { t } = useTranslation();
		const modal = useModal();
		const [isLoading, setIsLoading] = useState(false);

		const handleDelete = async () => {
			setIsLoading(true);
			await onConfirm();
			modal.hide();
			setIsLoading(false);
		};

		return (
			<CustomModal
				width={480}
				open={modal.visible}
				onClose={() => modal.hide()}
			>
				<div className="p-6">
					<div className="flex items-start gap-3">
						<IconWarning size={20} />

						<div className="flex flex-col gap-2">
							<div className="!font-dm-sans !text-[16px] !font-extrabold !leading-5 text-color-text-primary-1">
								{title || t("common.deleteConfirm.title")}
							</div>

							<div className="text-[14px] leading-5 text-color-text-primary-2">
								{description || t("common.deleteConfirm.description")}
							</div>
						</div>
					</div>

					<div className="mt-6 flex justify-end gap-2">
						<button
							className="cursor-pointer hover:bg-grey-fill2-hover  bg-grey-fill2-normal text-text-primary-1 px-3 py-1 rounded-lg"
							onClick={() => modal.hide()}
						>
							{t("common.cancel")}
						</button>

						<AntdButton
							type="primary"
							danger
							onClick={handleDelete}
							loading={isLoading}
						>
							{confirmText || t("common.delete")}
						</AntdButton>
					</div>
				</div>
			</CustomModal>
		);
	},
);
