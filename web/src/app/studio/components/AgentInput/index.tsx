import { Loading, SendFilled } from "@hatchify/icons";
import { Input } from "antd";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/utils";

export interface AgentInputProps {
	/** Placeholder text for the input */
	placeholder?: string;
	/** Whether the input is in loading/disabled state */
	isLoading?: boolean;
	/** Callback when user sends a message */
	onSend: (message: string) => void | Promise<void>;
	/** Optional className for the container */
	className?: string;
	/** Optional value for controlled input */
	value?: string;
	/** Optional onChange for controlled input */
	onChange?: (value: string) => void;
}

export default function AgentInput({
	placeholder,
	isLoading = false,
	onSend,
	className,
	value: controlledValue,
	onChange: controlledOnChange,
}: AgentInputProps) {
	const { t } = useTranslation();
	const [internalValue, setInternalValue] = useState("");

	// Use controlled or uncontrolled mode
	const value = controlledValue !== undefined ? controlledValue : internalValue;
	const setValue =
		controlledOnChange !== undefined ? controlledOnChange : setInternalValue;

	async function sendMessage() {
		if (!value.trim() || isLoading) return;
		const messageContent = value;
		setValue("");
		await onSend(messageContent);
	}

	return (
		<div
			className={cn(
				"flex w-[720px] h-[60px] items-center gap-4 rounded-full ",
				"border-[1px] border-grey-layer2-normal bg-grey-layer2-normal",
				"shadow-[0px_0px_0px_1px_var(--color-grey-line1-normal),0px_4px_16px_0px_var(--3,rgba(12,13,25,0.03)),0px_8px_32px_0px_var(--3,rgba(12,13,25,0.03)),0px_16px_64px_0px_var(--3,rgba(12,13,25,0.03))]",
				className,
			)}
		>
			<Input
				value={value}
				onChange={(e) => setValue(e.target.value)}
				placeholder={placeholder || t("agentAction.askAnything")}
				onPressEnter={(e) => {
					// Avoid sending when using IME (e.g., Chinese) and Enter is used to confirm composition
					// Some browsers set nativeEvent.isComposing, and some report keyCode 229 during composition
					const nativeEvent: any = (e as any).nativeEvent;
					if (
						nativeEvent?.isComposing ||
						(e as any).isComposing ||
						(nativeEvent && nativeEvent.keyCode === 229)
					) {
						return;
					}
					sendMessage();
				}}
				className="!flex-1 !py-5 !pr-0 !px-6 h-full !ring-0 !border-0 !w-full"
			/>
			<div className="pr-3">
				<button
					onClick={(e) => {
						e.stopPropagation();
						sendMessage();
					}}
					disabled={!value.trim()}
					className={`flex h-8 w-8
            items-center justify-center rounded-full
            text-text-secondary-1 transition-all
            duration-200
						${isLoading ? "bg-glass-fill1-normal text-grey-layer2-normal disabled:cursor-not-allowed disabled:opacity-50" : "bg-advanced-fill-normal text-text-secondary-1 hover:bg-advanced-fil-hover"}`}
				>
					{isLoading ? (
						<Loading size={16} className="animate-spin" />
					) : (
						<SendFilled size={16} />
					)}
				</button>
			</div>
		</div>
	);
}
