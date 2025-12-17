/**
 * SSE Event Type Definitions
 *
 * Defines discriminated union types for workflow and webcreator SSE events.
 * Each event type has specific data payloads for type-safe event handling.
 */

// Base SSE event structure from the reader
export interface BaseSSEEvent {
	event: string;
	data: string;
	id?: string;
}

/**
 * Workflow SSE Events
 * Used for workflow execution progress streaming
 */
export type WorkflowEvent =
	| { type: "start"; data: Record<string, unknown> }
	| { type: "phase"; phase: string; message: string }
	| { type: "done"; data?: Record<string, unknown> }
	| { type: "error"; message: string; code?: string };

/**
 * WebCreator SSE Events
 * Used for web creator build and deployment progress streaming
 */
export type WebCreatorEvent =
	| { type: "start"; taskId: string; data?: Record<string, unknown> }
	| { type: "delta"; content: string }
	| {
			type: "tool_call";
			tool_calls: Array<{
				tool_call_id: string;
				tool_name: string;
				args: Record<string, unknown>;
			}>;
	  }
	| { type: "tool_output"; tool_call_id: string; status: "success" | "error" }
	| { type: "progress"; stage: string; message: string }
	| { type: "log"; content: string }
	| { type: "deploy_result"; preview_url: string; message: string }
	| { type: "ping"; timestamp: number }
	| { type: "done"; data?: Record<string, unknown> }
	| { type: "error"; reason?: string; message?: string };

/**
 * Union of all stream event types
 */
export type StreamEvent = WorkflowEvent | WebCreatorEvent;

/**
 * Event parser function type
 * Converts raw SSE event to typed event object
 */
export type EventParser<T extends StreamEvent> = (
	raw: BaseSSEEvent,
) => T | null;
