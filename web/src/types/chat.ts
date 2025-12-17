export const mainTags = ["code-write", "code-replace", "code-delete"] as const;

export const subTags = ["code-path", "code-match", "code-content"] as const;

export const MessageItemType = {
	TEXT: "text",
	CODE: "code",
	REASONING: "reasoning",
	PROGRESS: "progress",
	TOOL_USE: "toolUse",
} as const;

export type MessageItemType =
	(typeof MessageItemType)[keyof typeof MessageItemType];

export type MessageItem =
	| {
			id: string;
			type: typeof MessageItemType.TEXT;
			text: string;
	  }
	| {
			id: string;
			type: typeof MessageItemType.CODE;
			code: {
				type: (typeof mainTags)[number];
				path: string;
				content: string;
			};
	  }
	| {
			id: string;
			type: typeof MessageItemType.REASONING;
			reasoning: string;
	  }
	| {
			id: string;
			type: typeof MessageItemType.PROGRESS;
			progress: number;
	  }
	| {
			id: string;
			type: typeof MessageItemType.TOOL_USE;
			toolUse: {
				toolUseId: string;
				name: string;
				input: Record<string, any>;
			};
	  };

export const StudioPanelTab = {
	Workflow: "workflow",
	WebCreator: "webCreator",
} as const;

export type StudioPanelTabType =
	(typeof StudioPanelTab)[keyof typeof StudioPanelTab];

export type ChatHistory = {
	id: string;
	type?: "loading" | "message" | "progress";
	role: "user" | "assistant";
	content: MessageItem[];
	mode: StudioPanelTabType;
	parentId?: string;
};
