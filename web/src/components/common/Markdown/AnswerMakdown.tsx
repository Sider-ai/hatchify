import "./AnswerMakdown.scss";
import "./markdown.scss";

import { memo, useRef } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

const PreComponent = ({ children }: { children?: React.ReactNode }) => {
	const containerRef = useRef<HTMLDivElement>(null);

	let language = "text";
	if (Array.isArray(children)) {
		const firstChild = children[0];
		if (
			typeof firstChild === "object" &&
			firstChild !== null &&
			"props" in firstChild &&
			typeof (firstChild as any).props?.className === "string"
		) {
			const match = (firstChild as any).props.className.match(/language-(\w+)/);
			if (match?.[1]) {
				language = match[1];
			}
		}
	}

	return (
		<pre className="flex flex-col rounded-xl border border-grey-line2-normal bg-[#262734]">
			<div className="me-2 ms-4 flex h-10 items-center gap-2 text-[#D6DAFF8F] font-normal-12">
				<span className="me-auto">{language}</span>

				<div
					className="flex cursor-pointer select-none items-center gap-1 rounded-md px-2 hover:text-[#DCDFF9EB]"
					onClick={() => {}}
				></div>
			</div>

			<div
				ref={containerRef}
				className="message-item custom-scrollbar overflow-x-auto text-text-primary-2"
			>
				{children}
			</div>
		</pre>
	);
};

function AnswerMakdown(props: Parameters<typeof ReactMarkdown>[0]) {
	return (
		<div className="markdown-body">
			<ReactMarkdown
				rehypePlugins={[
					[
						rehypeKatex,
						{
							errorColor: "",
						},
					],
					[rehypeHighlight, { detect: true, ignoreMissing: true }],
				]}
				remarkPlugins={[remarkGfm, remarkMath]}
				components={{
					pre: PreComponent,
				}}
			>
				{props.children?.trim().replace(/(\[ref:\d+(,\d+)*\])(\(\))?/g, "$1()")}
			</ReactMarkdown>
		</div>
	);
}

export default memo(AnswerMakdown);
