export type AgentDetail = {
	name: string;
	model: string;
	instruction: string;
	category: string;
	tools: string[];
	structured_output_schema: {
		type: string;
		properties: {
			[key: string]: {
				type: string;
				description: string;
			}[];
		};
	};
};

export type AgentToolDetail = {
	name: string;
	description: string;
	input_schema: Record<string, any>;
	output_schema: Record<string, any>;
};
