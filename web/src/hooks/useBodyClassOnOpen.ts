import { useEffect } from "react";

export function useBodyClassOnOpen(isOpen: boolean, className: string) {
	useEffect(() => {
		document.body.classList.toggle(className, isOpen);
		return () => {
			document.body.classList.remove(className);
		};
	}, [isOpen, className]);
}
