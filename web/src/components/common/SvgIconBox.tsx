import { cn } from "@/utils";

export type SvgIconBoxProps = {
	className?: string;
	svgString?: string | null | undefined;
};

const defaultToolSvgString = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 28 28" fill="none">
<path d="M12.2147 2.36751C13.189 1.87899 14.3329 1.87743 15.3085 2.36326L22.6536 6.02102C23.777 6.58046 23.7935 8.19377 22.6818 8.7766L15.3732 12.6083C14.3625 13.1382 13.1596 13.1365 12.1503 12.6037L4.89618 8.77456C3.78951 8.19039 3.80603 6.58361 4.92448 6.02282L12.2147 2.36751Z" fill="black" fill-opacity="0.96"/>
<path d="M11.022 13.9054C12.1912 14.508 12.9273 15.7226 12.9273 17.0494L12.9273 24.454C12.9273 25.6174 11.7026 26.3628 10.6855 25.8185L3.6576 22.0572C2.5148 21.4456 1.80005 20.2455 1.80005 18.9384L1.80005 11.6728C1.80005 10.5198 3.00486 9.77366 4.02099 10.2973L11.022 13.9054Z" fill="black" fill-opacity="0.96"/>
<path d="M16.5782 13.9054C15.4089 14.508 14.6728 15.7227 14.6728 17.0494V24.4539C14.6728 25.6174 15.8975 26.3628 16.9147 25.8185L23.9425 22.0572C25.0853 21.4456 25.8 20.2455 25.8 18.9384V11.6729C25.8 10.5199 24.5952 9.77369 23.5791 10.2974L16.5782 13.9054Z" fill="black" fill-opacity="0.96"/>
</svg>`;

export function ToolSvgIconBox({ className, svgString }: SvgIconBoxProps) {
	return (
		<div
			className={cn(
				"size-7 overflow-hidden bg-grey-layer2-normal flex items-center justify-center rounded-lg border border-grey-line2-normal",
				className,
			)}
			// biome-ignore lint/security/noDangerouslySetInnerHtml: <explanation>
			dangerouslySetInnerHTML={{
				__html: defaultToolSvgString,
			}}
		/>
	);
}
