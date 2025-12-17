import { useEffect, useId, useState } from "react";

export default function IconRender({
	svgStr,
	size,
	width,
	height,
	className,
}: {
	svgStr: string;
	size?: number | string;
	width?: number | string;
	height?: number | string;
	className?: string;
}) {
	const [processedSvg, setProcessedSvg] = useState<string>("");
	const uniqueId = useId();

	useEffect(() => {
		if (svgStr) {
			let processed = svgStr.replace(
				/id="([^"]+)"/g,
				(match: string, p1: string) => `id="${p1}_${uniqueId}"`,
			);

			processed = processed.replace(
				/url\(#([^)]+)\)/g,
				(match: string, p1: string) => `url(#${p1}_${uniqueId})`,
			);

			setProcessedSvg(processed);
		}
	}, [svgStr, uniqueId]);

	if (!processedSvg) {
		return null;
	}

	return (
		<span
			className={"inline-flex shrink-0 [&>svg]:size-[inherit]"}
			// biome-ignore lint/security/noDangerouslySetInnerHtml: <explanation>
			dangerouslySetInnerHTML={{ __html: processedSvg }}
			style={{ width: width || size, height: height || size }}
		/>
	);
}
