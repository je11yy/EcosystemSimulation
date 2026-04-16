export type Position = {
	x: number;
	y: number;
};

export interface Node {
	id: number;
	position: Position;
}

export type Edge = {
	id: number;
	source: number;
	target: number;
	weight: number;
};

type Graph = {
	nodes: Node[];
	edges: Edge[];
};

export type Props = {
	graph: Graph;
	width: number;
	height: number;
	selectedNodeId: number | null;
	onNodeClick: (nodeId: number) => void;
	selectedEdgeId: number | null;
	onEdgeClick: (edgeId: number) => void;
	onNodePositionChange: (nodeId: number, position: Position) => void;
	getNodeColor?: (node: Node) => string;
};
