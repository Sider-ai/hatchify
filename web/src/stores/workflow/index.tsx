import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { ChatSlice } from "./slices/chatSlice";
import { createChatSlice } from "./slices/chatSlice";
import type { UiSlice } from "./slices/uiSlice";
import { createUiSlice } from "./slices/uiSlice";

type WorkflowStoreState = ChatSlice & UiSlice;

const useWorkflowStore = create<WorkflowStoreState>()(
	devtools((...a) => ({
		...createChatSlice(...a),
		...createUiSlice(...a),
	})),
);

export default useWorkflowStore;
