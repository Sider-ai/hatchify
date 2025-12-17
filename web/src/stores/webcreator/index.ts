import { create } from "zustand";
import { combine } from "zustand/middleware";
import { WebCreatorTab } from "@/app/studio/components/WebsitePanel/WebCreator/types";

type WebCreatorState = {
	currentTab: WebCreatorTab;
	pending: boolean;
	previewResult: {
		url: string;
	};
};

const initialState: WebCreatorState = {
	currentTab: WebCreatorTab.Preview,
	pending: false,
	previewResult: {
		url: "",
	},
};

const useWebCreatorStore = create(
	combine(initialState, (set, _get, store) => ({
		setCurrentTab: (tab: WebCreatorTab) => set({ currentTab: tab }),
		setPreviewResult: (result: { url: string }) =>
			set({ previewResult: result }),

		setPending: (pending: boolean) => set({ pending }),
		reset: () => {
			set(() => store.getInitialState(), true);
		},
	})),
);

export default useWebCreatorStore;
