export default class WaitLock {
	private p: Promise<any> | null = null;
	private resolve: (value?: any) => void = () => {};

	lock() {
		this.p = new Promise((resolve) => {
			this.resolve = resolve;
		});
	}

	unlock(value?: any) {
		this.resolve(value);
	}

	wait() {
		return this.p;
	}
}
