export function listenDOMPositionChange(
	el: HTMLElement,
	onChange: (rect: DOMRect, el: HTMLElement) => void,
	win: Window = window,
) {
	if (!el) {
		return;
	}

	let lastRect = new DOMRect();

	function doCheck() {
		const rect = el.getBoundingClientRect();
		if (
			!(
				Math.floor(lastRect.left) === Math.floor(rect.left) &&
				Math.floor(lastRect.top) === Math.floor(rect.top) &&
				Math.floor(lastRect.width) === Math.floor(rect.width) &&
				Math.floor(lastRect.height) === Math.floor(rect.height)
			)
		) {
			onChange(rect, el);
		}
		lastRect = rect;
	}

	const resizeOb = new ResizeObserver(() => {
		doCheck();
	});
	resizeOb.observe(el);

	const intersectionOb = new IntersectionObserver(
		() => {
			doCheck();
		},
		{
			threshold: [0, 1],
		},
	);
	intersectionOb.observe(el);

	win.document.addEventListener("scroll", doCheck, {
		capture: true,
		passive: true,
	});
	win.addEventListener("resize", doCheck, { capture: true, passive: true });

	return () => {
		resizeOb.disconnect();
		intersectionOb.disconnect();
		win.document.removeEventListener("scroll", doCheck, { capture: true });
		win.removeEventListener("resize", doCheck, { capture: true });
	};
}
