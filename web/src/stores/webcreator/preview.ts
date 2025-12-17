import { createRef } from "react";
import { create } from "zustand";

interface WebPreviewState {
	iframeRef: React.RefObject<HTMLIFrameElement | null>;
	title: string;
	goBack: () => void;
	goForward: () => void;
	reload: () => void;
	reloadIndex: number;
	setIframeRef: (dom: HTMLIFrameElement) => void;
	setTitle: (title: string) => void;
}

const useWebPreviewStore = create<WebPreviewState>((set, get) => ({
	iframeRef: createRef<HTMLIFrameElement>(),
	title: "",
	reloadIndex: 0,
	setIframeRef: (dom: HTMLIFrameElement) => {
		get().iframeRef.current = dom;
	},
	setTitle: (title: string) => {
		set({ title });
	},
	goBack: () => {
		get().iframeRef.current?.contentWindow?.postMessage("goBack");
		// get().iframeRef.current?.contentWindow?.history.back();
	},
	goForward: () => {
		get().iframeRef.current?.contentWindow?.postMessage("goForward");
		// get().iframeRef.current?.contentWindow?.history.forward();
	},
	reload: () => {
		set({ reloadIndex: get().reloadIndex + 1 });
	},
}));

export default useWebPreviewStore;
