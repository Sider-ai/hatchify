import { memo } from "react";
import "./style.css";

import { NoteOutline } from "@hatchify/icons";
import type { WorkflowProcessor } from "@/types/workflow";

function ProcessorNode({ data }: { data: WorkflowProcessor }) {
	return (
		<section
			style={{
				boxShadow:
					"0px 0px 3px 1px rgba(255, 255, 255, 0.10), 0px 3px 7px 0px rgba(53, 54, 74, 0.04), 0px 0px 3px 0px rgba(12, 13, 25, 0.14), 0px 8px 40px 0px rgba(12, 13, 25, 0.06)",
				background:
					"linear-gradient(0deg, var(--color-grey-fill2-normal) 0%, var(--color-grey-fill2-normal) 100%), var(--color-grey-layer2-normal)",
			}}
			className="rounded-xl relative flex w-[260px] flex-col items-start "
		>
			<div className="flex items-center gap-2 py-1.5 px-3">
				<div className="text-grey-text-normal text-sm">
					<NoteOutline className="text-[#F4BF00]" />
				</div>
				<div className="w-[200px] truncate text-text-primary-3 text-sm">
					{data.processor_type}
				</div>
			</div>
			<div
				onClick={() => {}}
				className="shadow-[0px_-1px_0px_0px_var(--color-grey-fill2-normal)] w-full flex p-3 flex-col gap-2 rounded-xl bg-grey-layer2-normal"
			>
				<div className="text-text-primary-2 text-sm break-words node-instructions-clamp">
					{data.instance_name}
				</div>
			</div>
		</section>
	);
}

export default memo(ProcessorNode);
