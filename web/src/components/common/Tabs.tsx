import { motion } from "motion/react";
import {
	type ComponentPropsWithRef,
	type ReactNode,
	useEffect,
	useState,
} from "react";
import { cn } from "@/utils";
import { listenDOMPositionChange } from "./listenDOMPositionChange";

export type TabItem<T> = { label: ReactNode; value: T; disabled?: boolean };

export type TabsProps<T> = {
	type?: "bubble" | "underline";
	tabs: TabItem<T>[];
	value: T;
	onChange: (tab: T) => void;
} & Omit<ComponentPropsWithRef<"div">, "onChange">;

export default function Tabs<T extends string>({
	type = "bubble",
	...restProps
}: TabsProps<T>) {
	if (type === "bubble") {
		return <BubbleTabs {...restProps} />;
	}
	return <UnderlineTabs {...restProps} />;
}

function BubbleTabs<T extends string>({
	tabs,
	value,
	onChange,
	className,
	...restProps
}: TabsProps<T>) {
	const [containerEl, setContainerEl] = useState<HTMLDivElement | null>(null);
	const [bubbleStyle, setBubbleStyle] = useState({
		left: "0px",
		top: "0px",
		width: "0px",
		height: "0px",
	});

	useEffect(() => {
		if (!containerEl) {
			return;
		}

		const setStyle = () => {
			const activeItem = containerEl.querySelector(".tab-item-active");
			if (!activeItem) {
				return;
			}

			const containerRect = containerEl.getBoundingClientRect();
			const rect = activeItem.getBoundingClientRect();
			setBubbleStyle({
				left: `${rect.left - containerRect.left}px`,
				top: `${rect.top - containerRect.top}px`,
				width: `${rect.width}px`,
				height: `${rect.height}px`,
			});
		};

		return listenDOMPositionChange(containerEl, () => {
			setStyle();
		});
	}, [containerEl, value]);

	return (
		<div
			ref={setContainerEl}
			className={cn(
				"relative flex w-fit items-center gap-[3px] whitespace-nowrap rounded-full bg-grey-layer1-semitrans p-[3px]",
				className,
			)}
			{...restProps}
		>
			{tabs.map((tab) => {
				return (
					<div
						className={cn(
							"relative z-1 cursor-pointer select-none rounded-full px-3 py-[3px] text-sm",
							tab.disabled
								? "cursor-not-allowed text-text-primary-5"
								: value === tab.value
									? "tab-item-active font-semibold text-text-primary-1 [letter-spacing:-0.018em]"
									: "text-text-primary-3 hover:bg-grey-fill1-hover",
						)}
						key={tab.value}
						onClick={() => {
							if (tab.disabled) {
								return;
							}
							onChange?.(tab.value);
						}}
					>
						{tab.label}
					</div>
				);
			})}
			<motion.div
				className="pointer-events-none absolute z-0 rounded-full bg-grey-layer3-normal"
				transition={{ type: "spring", stiffness: 400, damping: 30 }}
				animate={bubbleStyle}
			></motion.div>
		</div>
	);
}

function UnderlineTabs<T extends string>({
	tabs,
	value,
	onChange,
	className,
	...restProps
}: TabsProps<T>) {
	const [containerEl, setContainerEl] = useState<HTMLDivElement | null>(null);
	const [undelineStyle, setUndelineStyle] = useState({
		left: "0px",
		width: "0px",
	});

	useEffect(() => {
		if (!containerEl) {
			return;
		}

		const setStyle = () => {
			const activeItem = containerEl.querySelector(".tab-item-active");
			if (!activeItem) {
				return;
			}

			const containerRect = containerEl.getBoundingClientRect();
			const rect = activeItem.getBoundingClientRect();
			setUndelineStyle({
				left: `${rect.left - containerRect.left + rect.width / 4}px`,
				width: `${rect.width / 2}px`,
			});
		};

		return listenDOMPositionChange(containerEl, () => {
			setStyle();
		});
	}, [containerEl, value]);

	return (
		<div
			ref={setContainerEl}
			className={cn(
				"relative flex h-8 w-fit items-center gap-4 whitespace-nowrap",
				className,
			)}
			{...restProps}
		>
			{tabs.map((tab) => {
				return (
					<div
						className={cn(
							"relative z-1 cursor-pointer select-none pb-2 pt-0.5 text-lg font-semibold leading-5",
							tab.disabled
								? "cursor-not-allowed text-text-primary-5"
								: value === tab.value
									? "tab-item-active text-text-primary-1"
									: "text-text-primary-4 hover:text-text-primary-1",
						)}
						key={tab.value}
						onClick={() => {
							if (tab.disabled) {
								return;
							}
							onChange?.(tab.value);
						}}
					>
						{tab.label}
					</div>
				);
			})}
			<motion.div
				className="pointer-events-none absolute bottom-0 z-0 h-0.5 overflow-hidden rounded-full bg-text-primary-1"
				transition={{ type: "spring", stiffness: 400, damping: 30 }}
				animate={undelineStyle}
			></motion.div>
		</div>
	);
}
