export const getPreviewUrl = (workflowId: string) => {
	return `${import.meta.env.VITE_API_TARGET}/preview/${workflowId}`;
};
