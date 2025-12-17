import { Loading, SendFilled, StarDefault } from "@hatchify/icons";
import { Switch } from "antd";
import { memo, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/utils";

type Props = {
	onSend?: (value: {
		prompt: string;
		isPromptOptimization: boolean;
	}) => Promise<void>;
	isLoading?: boolean;
	value?: string;
	setValue?: (value: string) => void;
};

function InputArea({
	onSend = async () => {},
	isLoading: externalLoading = false,
	value,
	setValue,
}: Props) {
	const [_, setIsFocused] = useState(false);

	const [isPromptOptimization, setIsPromptOptimization] = useState(true);

	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const { t } = useTranslation();

	const [innerValue, setInnerValue] = useState(value ?? "");
	const currentValue = value ?? innerValue;

	useEffect(() => {
		const el = textareaRef.current;
		if (!el) return;
		// Recalculate height when value changes programmatically
		el.style.height = "auto";
		const lineHeight = 24;
		const maxHeight = lineHeight * 6;
		const scrollHeight = el.scrollHeight;
		el.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
		el.style.overflowY = scrollHeight > maxHeight ? "auto" : "hidden";
	}, [currentValue]);

	const handleSend = async () => {
		if (!currentValue.trim() || externalLoading) return;
		try {
			await onSend({
				prompt: currentValue,
				isPromptOptimization,
			});
			if (setValue) {
				setValue("");
			} else {
				setInnerValue("");
			}
		} catch (_) {
			// keep value on error
		}
	};

	return (
		<div
			className={`
              rounded-[24px] 
              border border-grey-line2-normal
              bg-grey-layer2-normal shadow-[0px_2px_8px_0px_var(--color-shadow-overflow-2),0px_8px_24px_0px_var(--color-shadow-overflow-2),0px_16px_48px_0px_var(--color-shadow-overflow-2)]
              transition-all duration-200
              hover:border-grey-line2-hover
      `}
		>
			<div
				className="mb-2 px-4 pt-3"
				onClick={() => textareaRef.current?.focus()}
			>
				<textarea
					ref={textareaRef}
					value={currentValue}
					onChange={(e) => {
						if (setValue) {
							setValue(e.target.value);
						} else {
							setInnerValue(e.target.value);
						}
						e.target.style.height = "auto";
						const scrollHeight = e.target.scrollHeight;

						const lineHeight = 24;
						const maxHeight = lineHeight * 6;

						e.target.style.height = `${Math.min(scrollHeight, maxHeight)}px`;

						e.target.style.overflowY =
							scrollHeight > maxHeight ? "auto" : "hidden";
					}}
					onFocus={() => setIsFocused(true)}
					onBlur={() => setIsFocused(false)}
					onKeyDown={(e) => {
						// Avoid sending when using IME (e.g., Chinese input) where Enter confirms composition
						const isComposing =
							// nativeEvent.isComposing is the standard way
							// keyCode 229 is a fallback for some environments
							((e.nativeEvent as any)?.isComposing ?? false) ||
							e.keyCode === 229;
						if (
							e.key === "Enter" &&
							!e.shiftKey &&
							!externalLoading &&
							!isComposing
						) {
							e.preventDefault();
							handleSend();
						}
					}}
					placeholder={t("home.input.placeholder")}
					className="custom-scrollbar w-full resize-none bg-transparent text-base outline-none placeholder:text-text-primary-4 text-text-primary-1"
					rows={2}
					style={{
						lineHeight: "24px",
						maxHeight: "144px",
						overflowY: "hidden",
					}}
				/>
			</div>
			{/* Toolbar */}
			<div
				className="flex h-[40px] items-center justify-between px-2 pb-2 "
				// onClick={() => textareaRef.current?.focus()}
			>
				<div className="flex items-center gap-x-2">
					<div
						onClick={() => setIsPromptOptimization(!isPromptOptimization)}
						className={cn(
							"!hidden hover:bg-grey-fill2-hover select-none cursor-pointer flex items-center gap-x-1 text-text-primary-3 bg-grey-fill2-normal rounded-full px-3.5 py-1.5",
						)}
					>
						<StarDefault size={16} />
						<span className="text-sm mr-1">
							{t("home.input.promptOptimization")}
						</span>
						<Switch size="small" checked={isPromptOptimization} />
					</div>
				</div>
				<button
					onClick={(e) => {
						e.stopPropagation();
						handleSend();
					}}
					className={`flex h-8 w-8 
            items-center justify-center rounded-full
            text-text-secondary-1 transition-all
            duration-200
						${
							externalLoading || !currentValue.trim()
								? "bg-glass-fill1-normal text-grey-layer2-normal disabled:cursor-not-allowed disabled:opacity-50"
								: "bg-advanced-fill-normal text-text-secondary-1 hover:bg-advanced-fil-hover"
						}`}
				>
					{externalLoading ? (
						<Loading size={16} className="animate-spin" />
					) : (
						<SendFilled size={16} />
					)}
				</button>
			</div>
		</div>
	);
}
export default memo(InputArea);
