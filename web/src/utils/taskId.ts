/**
 * TaskIdManager - Manages task IDs in sessionStorage with a specific prefix
 */
class TaskIdManager {
	private prefix: string;

	constructor(prefix: string) {
		this.prefix = prefix;
	}

	/**
	 * Generate the storage key with prefix
	 * @param key - The identifier key
	 * @returns The full storage key
	 */
	private getStorageKey(key: string): string {
		return `for_${this.prefix}_task___${key}`;
	}

	/**
	 * Store a task ID in sessionStorage
	 * @param key - The identifier key
	 * @param taskId - The task ID to store
	 */
	set(key: string, taskId: string): void {
		sessionStorage.setItem(this.getStorageKey(key), taskId);
	}

	/**
	 * Retrieve a task ID from sessionStorage
	 * @param key - The identifier key
	 * @returns The stored task ID or null if not found
	 */
	get(key: string): string | null {
		return sessionStorage.getItem(this.getStorageKey(key));
	}

	/**
	 * Remove a task ID from sessionStorage
	 * @param key - The identifier key
	 */
	remove(key: string): void {
		sessionStorage.removeItem(this.getStorageKey(key));
	}
}

// Create singleton instances for specific use cases
export const webCreatorTaskId = new TaskIdManager("webcreator");
export const workflowTaskId = new TaskIdManager("workflow");
