import { useParams } from "react-router";
import { webCreatorTaskId, workflowTaskId } from "@/utils/taskId";

export const useStudioParams = () => {
	const { id } = useParams<{ id: string }>();
	const taskIdForWorkflow = id ? workflowTaskId.get(id) : undefined;
	const taskIdForWebCreator = id ? webCreatorTaskId.get(id) : undefined;
	return { workflowId: id, taskIdForWorkflow, taskIdForWebCreator };
};
