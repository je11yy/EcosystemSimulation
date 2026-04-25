import type { ReactNode } from "react";

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
	directed?: boolean;
	bidirectionalArrows?: boolean;
	edgeIds?: number[];
	displayKey?: string;
	sourcePortOffset?: number;
	targetPortOffset?: number;
};

type Graph = {
	nodes: Node[];
	edges: Edge[];
};

export type Props = {
	graph: Graph;
	selectedNodeId: number | null;
	onNodeClick: (nodeId: number) => void;
	selectedEdgeId: number | null;
	onEdgeClick: (edgeId: number) => void;
	onNodePositionChange: (nodeId: number, position: Position) => void;
	getNodeColor?: (node: Node) => string;
	getEdgeLabel?: (edge: Edge) => string | undefined;
	renderNodeContent?: (node: Node, position: Position, isSelected: boolean) => ReactNode;
	constrainNodePosition?: (
		nodeId: number,
		position: Position,
		graph: Graph,
		positions: Record<number, Position>,
	) => Position;
	resolveDragPositions?: (
		nodeId: number,
		position: Position,
		graph: Graph,
		positions: Record<number, Position>,
	) => Record<number, Position>;
	canDragNodes?: boolean;
};
