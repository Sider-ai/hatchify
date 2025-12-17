import type { StateCreator } from "zustand";
import type { ChatHistory } from "@/types/chat";

export type Updater<T> = T | ((prev: T) => T);

export interface ChatSliceState {
	chatHistoryForWorkflow: ChatHistory[];
	chatHistoryForWebCreator: ChatHistory[];
}

export interface ChatSliceActions {
	setChatHistoryForWorkflow: (v: Updater<ChatHistory[]>) => void;
	setChatHistoryForWebCreator: (v: Updater<ChatHistory[]>) => void;
	resetChatSlice: () => void; // 只重置本 slice，避免和 UiSlice 强耦合
}

export type ChatSlice = ChatSliceState & ChatSliceActions;

export const CHAT_INITIAL_STATE: ChatSliceState = {
	chatHistoryForWorkflow: [],
	chatHistoryForWebCreator: [],
};

export const createChatSlice: StateCreator<ChatSlice, [], [], ChatSlice> = (
	set /*, get */,
) => ({
	...CHAT_INITIAL_STATE,

	setChatHistoryForWorkflow: (v) =>
		set((s) => ({
			chatHistoryForWorkflow:
				typeof v === "function" ? (v as any)(s.chatHistoryForWorkflow) : v,
		})),

	setChatHistoryForWebCreator: (v) =>
		set((s) => ({
			chatHistoryForWebCreator:
				typeof v === "function" ? (v as any)(s.chatHistoryForWebCreator) : v,
		})),

	resetChatSlice: () => set(CHAT_INITIAL_STATE, false),
});
