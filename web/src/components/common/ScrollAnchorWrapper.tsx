import mergeRefs from "merge-refs";
import {
	type ComponentProps,
	type ForwardedRef,
	forwardRef,
	useEffect,
	useRef,
} from "react";
import { cn } from "@/utils";

function ScrollAnchorWrapper(
	props: ComponentProps<"div"> & {
		children: React.ReactNode;
		content: any;
	},
	forwardedRef: ForwardedRef<HTMLDivElement>,
) {
	const { className, children, content, ...restProps } = props;
	const ref = useRef<HTMLDivElement>(null);

	useEffect(() => {
		const el = ref.current;
		if (el && content) {
			const { scrollHeight, clientHeight, scrollTop } = el;
			const overflowY = scrollHeight - clientHeight;
			if (scrollTop === 0 && overflowY > 0 && overflowY <= 50) {
				el.scrollTop = overflowY + 99;
			}
		}
	}, [content]);

	return (
		<div
			ref={mergeRefs(ref, forwardedRef)}
			className={cn("ScrollAnchorWrapper overflow-auto", className)}
			{...restProps}
		>
			{children}
			<div
				style={{ flexShrink: 0, height: "1px", overflowAnchor: "auto" }}
			></div>
		</div>
	);
}

export default /* #__PURE__ */ forwardRef(ScrollAnchorWrapper);
