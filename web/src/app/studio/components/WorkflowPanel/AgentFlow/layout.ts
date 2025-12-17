export const LAYOUT = {
	NODE_WIDTH: 260,
	NODE_HEIGHT: 120,
	H_GAP: 120,
	V_GAP: 24,
	TOP_PADDING: 120,
};

export type GraphEdge = { from_node: string; to_node: string };

export function computeDAGPositions(nodeIds: string[], edges: GraphEdge[]) {
	const adjacency = new Map<string, string[]>();
	const indegree = new Map<string, number>();

	nodeIds.forEach((id) => {
		adjacency.set(id, []);
		indegree.set(id, 0);
	});

	for (const e of edges) {
		if (adjacency.has(e.from_node) && indegree.has(e.to_node)) {
			adjacency.get(e.from_node)!.push(e.to_node);
			indegree.set(e.to_node, (indegree.get(e.to_node) || 0) + 1);
		}
	}

	const queue: string[] = [];
	const layer = new Map<string, number>();
	for (const id of nodeIds) {
		if ((indegree.get(id) || 0) === 0) {
			queue.push(id);
			layer.set(id, 0);
		}
	}

	while (queue.length) {
		const current = queue.shift() as string;
		const currentLayer = layer.get(current) || 0;
		for (const next of adjacency.get(current) || []) {
			layer.set(next, Math.max(layer.get(next) || 0, currentLayer + 1));
			indegree.set(next, (indegree.get(next) || 0) - 1);
			if ((indegree.get(next) || 0) === 0) queue.push(next);
		}
	}

	for (const id of nodeIds) if (!layer.has(id)) layer.set(id, 0);

	const layers = new Map<number, string[]>();
	for (const id of nodeIds) {
		const l = layer.get(id) || 0;
		if (!layers.has(l)) layers.set(l, []);
		layers.get(l)!.push(id);
	}

	const idToPosition = new Map<string, { x: number; y: number }>();
	const layerIndexes = Array.from(layers.keys()).sort((a, b) => a - b);
	for (const l of layerIndexes) {
		const nodesInLayer = layers.get(l)!;
		nodesInLayer.forEach((id, index) => {
			const x = l * (LAYOUT.NODE_WIDTH + LAYOUT.H_GAP);
			const y =
				LAYOUT.TOP_PADDING + index * (LAYOUT.NODE_HEIGHT + LAYOUT.V_GAP);
			idToPosition.set(id, { x, y });
		});
	}

	return idToPosition;
}
