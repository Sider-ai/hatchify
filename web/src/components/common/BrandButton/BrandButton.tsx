import type React from "react";
import { cn } from "@/utils";
import styles from "./brand-button.module.scss";

type BrandButtonProps = {
	children: React.ReactNode;
	onClick: () => void;
	className?: string;
	buttonClassName?: string;
};

function BrandButton({
	children,
	onClick,
	className,
	buttonClassName,
}: BrandButtonProps) {
	return (
		<div className={cn("relative group cursor-pointer shrink-0", className)}>
			<div
				className="absolute inset-0 opacity-0 blur-[10px] transition-opacity group-hover:opacity-100"
				style={{
					background:
						"linear-gradient(91deg, rgba(255, 193, 74, 0.6) 4%, rgba(107, 174, 255, 0.6) 27.46%, rgba(108, 137, 255, 0.6) 57.26%, rgba(146, 111, 255, 0.6) 96%)",
				}}
			/>
			<button
				className={cn(
					"rounded-lg z-10 relative w-full h-full",
					styles.brandButton,
					buttonClassName,
				)}
				onClick={onClick}
			>
				<span>{children}</span>
			</button>
		</div>
	);
}

export default BrandButton;
