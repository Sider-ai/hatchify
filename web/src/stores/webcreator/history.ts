import { useEffect } from "react";
import { create } from "zustand";

interface WebsiteHistoryState {
	historyIdx: number;
	historyCount: number;
	addHistory: () => void;
	setHistoryIdx: (idx: number) => void;
	reload: () => void;
}

const useWebsiteHistoryStore = create<WebsiteHistoryState>((set) => ({
	historyIdx: 0,
	historyCount: 0,
	addHistory: () =>
		set((state) => ({
			historyCount: state.historyIdx + 1,
			historyIdx: state.historyIdx + 1,
		})),
	setHistoryIdx: (idx: number) => set({ historyIdx: idx }),
	reload: () => set({ historyIdx: 0, historyCount: 0 }),
}));

export function useWebsiteHistory(init = false) {
	const { historyIdx, historyCount, addHistory, setHistoryIdx, reload } =
		useWebsiteHistoryStore();
	useEffect(() => {
		if (init) {
			reload();
		}
	}, []);

	return {
		reload,
		addHistory,
		setHistoryIdx,
		back: historyIdx > 0,
		forward: historyIdx < historyCount,
	};
}

export { useWebsiteHistoryStore };
