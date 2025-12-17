import type { AgentDetail } from "./agent";

export type WorkflowListItem = WorkflowDetail;

export type WorkflowDetail = {
	id: string;
	name: string;
	description: string;
	current_spec: {
		agents: AgentDetail[];
		nodes: string[];
		edges: {
			from_node: string;
			to_node: string;
		}[];
		entry_point: string;
		input_schema: Record<string, any>;
		output_schema: Record<string, any>;
	};
	current_version_id: number;
	created_at: string;
	updated_at: string;
};

export type WorkflowProcessor = {
	instance_name: string;
	processor_type: string;
	input_mapping: Record<string, any>;
};
