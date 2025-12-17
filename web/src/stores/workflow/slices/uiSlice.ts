import type { StateCreator } from "zustand";
import type { StudioPanelTabType } from "@/types/chat";
import { StudioPanelTab } from "@/types/chat";

export type Updater<T> = T | ((prev: T) => T);

export interface UiSliceState {
	studioPanelTab: StudioPanelTabType;
	isWorkflowRunning: boolean; // 是否从 webcreator 触发了 workflow 执行
	isWorkflowCreating: boolean; // 是否正在创建 workflow
}

export interface UiSliceActions {
	setStudioPanelTab: (v: StudioPanelTabType) => void;
	setIsWorkflowRunning: (v: boolean) => void;
	setIsWorkflowCreating: (v: boolean) => void;
	resetUiSlice: () => void;
}

export type UiSlice = UiSliceState & UiSliceActions;

export const UI_INITIAL_STATE: UiSliceState = {
	studioPanelTab: StudioPanelTab.Workflow,
	isWorkflowRunning: false,
	isWorkflowCreating: false,
};

export const createUiSlice: StateCreator<UiSlice, [], [], UiSlice> = (set) => ({
	...UI_INITIAL_STATE,

	setStudioPanelTab: (v) => set({ studioPanelTab: v }),
	setIsWorkflowRunning: (v) => set({ isWorkflowRunning: v }),
	setIsWorkflowCreating: (v) => set({ isWorkflowCreating: v }),

	resetUiSlice: () => set(UI_INITIAL_STATE),
});
