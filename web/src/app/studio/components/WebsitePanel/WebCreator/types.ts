export const WebCreatorTab = {
	// Code: "code",
	Preview: "preview",
	Phone: "phone",
} as const;

export type WebCreatorTab = (typeof WebCreatorTab)[keyof typeof WebCreatorTab];
