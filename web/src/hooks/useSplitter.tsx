import { useGetState } from "ahooks";
import { useEffect, useMemo, useRef, useState } from "react";
import { cn } from "@/utils";

export default function useSplitter(opts?: {
	resizeable?: boolean;
	className?: string;
}) {
	const { resizeable = true, className } = opts || {};
	const [targetEl, setTargetEl] = useState<HTMLDivElement | null>(null);
	const [handleEl, setHandleEl] = useState<HTMLDivElement | null>(null);

	const [dragging, setDragging, getDragging] = useGetState(false);

	useEffect(() => {
		if (!targetEl || !handleEl) return;
		const ac = new AbortController();
		let ac2 = new AbortController();
		let width = 0;

		const handlePointerMove = (e: PointerEvent) => {
			if (getDragging()) {
				width -= e.movementX;
				targetEl.style.width = `${width}px`;
			}
		};

		const handlePointerDown = (e: PointerEvent) => {
			setDragging(true);
			handleEl.setPointerCapture(e.pointerId);
			const rect = targetEl.getBoundingClientRect();
			width = rect.width;

			ac2 = new AbortController();
			window.addEventListener("pointermove", handlePointerMove, {
				signal: ac2.signal,
			});
		};

		const handlePointerUp = (e: PointerEvent) => {
			setDragging(false);
			handleEl.releasePointerCapture(e.pointerId);
			ac2.abort();
		};

		handleEl.addEventListener("pointerdown", handlePointerDown, {
			signal: ac.signal,
		});
		window.addEventListener("pointerup", handlePointerUp, {
			signal: ac.signal,
		});
		window.addEventListener("pointercancel", handlePointerUp, {
			signal: ac.signal,
		});
		return () => {
			ac.abort();
			ac2.abort();
		};
	}, [getDragging, handleEl, setDragging, targetEl]);

	const SplitterHandleNode = useMemo(() => {
		return resizeable ? (
			<div
				ref={setHandleEl}
				className={cn(
					"group relative w-[8px] shrink-0 cursor-ew-resize flex-center",
					className,
				)}
			>
				<div
					className={cn(
						"h-full w-[2px]",
						"group-hover:bg-brand-secondary-normal",
						dragging && "bg-brand-secondary-normal",
					)}
				/>
			</div>
		) : null;
	}, [className, dragging, resizeable]);

	return {
		setTargetEl,
		SplitterHandleNode,
	};
}

export function useSplitter2({
	resizeable = true,
	className,
	minWidth,
	maxWidth,
}: {
	resizeable?: boolean;
	className?: string;
	minWidth?: number;
	maxWidth?: number;
}) {
	const targetEl = useRef<HTMLDivElement>(null);

	const SplitterHandleNode = useMemo(() => {
		let width = 0;
		let x = 0;
		return resizeable ? (
			<SplitterNode
				className={className}
				onStart={(clientX) => {
					x = clientX;
					const rect = targetEl.current?.getBoundingClientRect();
					if (!rect) return;
					width = rect.width;
				}}
				onEnd={() => {
					width = 0;
					x = 0;
				}}
				onMove={(clientX) => {
					const _newWidth = width + clientX - x;

					const newWidth = Math.max(
						minWidth || 0,
						Math.min(maxWidth || Infinity, _newWidth),
					);
					targetEl.current!.style.width = `${newWidth}px`;
				}}
			/>
		) : null;
	}, [className, resizeable, targetEl, minWidth, maxWidth]);

	return {
		targetEl,
		SplitterHandleNode,
	};
}

type SplitterNodeProps = {
	className?: string;
	onMove?: (clientX: number) => void;
	onStart?: (clientX: number) => void;
	onEnd?: (clientX: number) => void;
};

function SplitterNode({
	className,
	onMove,
	onStart,
	onEnd,
}: SplitterNodeProps) {
	const [dragging, setDragging] = useState(false);
	const handleEl = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!handleEl.current) return;
		const ac = new AbortController();
		let dragging = false;

		handleEl.current.addEventListener(
			"pointerdown",
			(e) => {
				onStart?.(e.clientX);
				setDragging(true);
				handleEl.current?.setPointerCapture(e.pointerId);
				dragging = true;
			},
			{
				signal: ac.signal,
			},
		);

		handleEl.current.addEventListener(
			"pointermove",
			(e) => {
				if (dragging) {
					onMove?.(e.clientX);
				}
			},
			{
				signal: ac.signal,
			},
		);

		handleEl.current.addEventListener(
			"pointercancel",
			(e) => {
				setDragging(false);
				handleEl.current?.releasePointerCapture(e.pointerId);
				dragging = false;
			},
			{
				signal: ac.signal,
			},
		);

		window.addEventListener(
			"pointerup",
			(e) => {
				onEnd?.(e.clientX);
				setDragging(false);
				handleEl.current?.releasePointerCapture(e.pointerId);
				dragging = false;
			},
			{
				signal: ac.signal,
			},
		);

		return () => {
			ac.abort();
		};
	}, []);

	return (
		<div
			ref={handleEl}
			className={cn(
				"group relative w-[8px] shrink-0 cursor-ew-resize flex-center",
				className,
			)}
		>
			<div
				className={cn(
					"h-full w-[2px]",
					"group-hover:bg-brand-secondary-normal",
					dragging && "bg-brand-secondary-normal",
				)}
			/>
		</div>
	);
}
