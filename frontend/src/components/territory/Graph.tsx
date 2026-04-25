import type { Territory } from "./types";
import type { Edge, Node, Position, Props } from "../graph/types";
import { GraphComponent } from "../graph/Graph";

export const TerritoryGraphComponent = ({
    graph,
    selectedNodeId = null,
    onNodeClick,
    selectedEdgeId = null,
    onEdgeClick,
    onNodePositionChange,
    canDragNodes,
}: Props) => {
    return <GraphComponent
        graph={graph}
        selectedNodeId={selectedNodeId}
        onNodeClick={onNodeClick}
        selectedEdgeId={selectedEdgeId}
        onEdgeClick={onEdgeClick}
        onNodePositionChange={onNodePositionChange}
        canDragNodes={canDragNodes}
        getEdgeLabel={(edge) => edge.weight.toFixed(1)}
        constrainNodePosition={constrainTerritoryPosition}
        resolveDragPositions={resolveTerritoryDragPositions}
        renderNodeContent={(node, position) => {
            const territory = node as Territory;
            return (
                <>
                    <text
                        x={position.x}
                        y={position.y + 6}
                        textAnchor="middle"
                        className="graph-node-label"
                    >
                        {territory.id}
                    </text>
                    <g transform={`translate(${position.x + 22}, ${position.y - 22})`}>
                        <circle r={13} className="territory-agent-badge" />
                        <text
                            y={4.5}
                            textAnchor="middle"
                            className="territory-agent-badge__label"
                        >
                            {territory.occupant_count ?? 0}
                        </text>
                    </g>
                </>
            );
        }}
        getNodeColor={(node) => {
            const territory = node as Territory;
            const foodRatio = territory.food_capacity > 0
                ? Math.max(0, Math.min(1, territory.food / territory.food_capacity))
                : 0;
            const red = Math.round(214 - 116 * foodRatio);
            const green = Math.round(76 + 104 * foodRatio);
            const blue = Math.round(75 - 35 * foodRatio);
            return `rgb(${red}, ${green}, ${blue})`;
        }} />
}

const EDGE_DISTANCE_SCALE = 140;
const NODE_PADDING = 28;

function constrainTerritoryPosition(
    _nodeId: number,
    position: Position,
    _graph: { nodes: Node[]; edges: Edge[] },
    _positions: Record<number, Position>,
) {
    return clampToCanvas(position);
}

function clampToCanvas(position: Position): Position {
    return {
        x: Math.max(NODE_PADDING, Math.min(800 - NODE_PADDING, position.x)),
        y: Math.max(NODE_PADDING, Math.min(600 - NODE_PADDING, position.y)),
    };
}

function resolveTerritoryDragPositions(
    nodeId: number,
    position: Position,
    graph: { nodes: Node[]; edges: Edge[] },
    positions: Record<number, Position>,
): Record<number, Position> {
    const basePosition = positions[nodeId];
    if (!basePosition) {
        return { ...positions, [nodeId]: position };
    }

    const nextPositions: Record<number, Position> = {
        ...positions,
        [nodeId]: position,
    };
    const distanceEdges = collapseDistanceEdges(graph.edges);
    const delta = {
        x: position.x - basePosition.x,
        y: position.y - basePosition.y,
    };

    if (delta.x === 0 && delta.y === 0) {
        return nextPositions;
    }

    const adjacency = new Map<number, Edge[]>();
    for (const edge of distanceEdges) {
        adjacency.set(edge.source, [...(adjacency.get(edge.source) ?? []), edge]);
        adjacency.set(edge.target, [...(adjacency.get(edge.target) ?? []), edge]);
    }

    const visited = new Set<number>([nodeId]);
    const queue: Array<{ territoryId: number; depth: number }> = [{ territoryId: nodeId, depth: 0 }];

    while (queue.length > 0) {
        const current = queue.shift();
        if (!current) {
            continue;
        }
        if (current.depth >= 2) {
            continue;
        }

        for (const edge of adjacency.get(current.territoryId) ?? []) {
            const neighborId = edge.source === current.territoryId ? edge.target : edge.source;
            if (visited.has(neighborId)) {
                continue;
            }
            visited.add(neighborId);
            queue.push({ territoryId: neighborId, depth: current.depth + 1 });

            const currentNeighborPosition = nextPositions[neighborId] ?? positions[neighborId];
            if (!currentNeighborPosition) {
                continue;
            }

            const depthFalloff = current.depth === 0 ? 0.28 : 0.14;
            const weightFalloff = 1 / Math.max(1, edge.weight);
            const springFactor = Math.max(0.08, Math.min(0.32, depthFalloff * weightFalloff));

            nextPositions[neighborId] = clampToCanvas({
                x: currentNeighborPosition.x + delta.x * springFactor,
                y: currentNeighborPosition.y + delta.y * springFactor,
            });
        }
    }

    for (let iteration = 0; iteration < 4; iteration += 1) {
        for (const edge of distanceEdges) {
            const source = nextPositions[edge.source];
            const target = nextPositions[edge.target];
            if (!source || !target) {
                continue;
            }

            const desiredDistance = edge.weight * EDGE_DISTANCE_SCALE;
            const aligned = alignPairDistance(
                source,
                target,
                desiredDistance,
                edge.source === nodeId,
                edge.target === nodeId,
            );

            nextPositions[edge.source] = clampToCanvas(aligned.source);
            nextPositions[edge.target] = clampToCanvas(aligned.target);
        }
    }

    for (let iteration = 0; iteration < 3; iteration += 1) {
        for (const edge of distanceEdges) {
            const source = nextPositions[edge.source];
            const target = nextPositions[edge.target];
            if (!source || !target) {
                continue;
            }

            const dx = target.x - source.x;
            const dy = target.y - source.y;
            const distance = Math.hypot(dx, dy);
            const desiredDistance = edge.weight * EDGE_DISTANCE_SCALE;
            if (distance === 0) {
                continue;
            }

            const differenceRatio = (distance - desiredDistance) / distance;
            if (Math.abs(differenceRatio) < 0.0025) {
                continue;
            }

            const correctionX = dx * differenceRatio;
            const correctionY = dy * differenceRatio;

            if (edge.source === nodeId) {
                nextPositions[edge.target] = clampToCanvas({
                    x: target.x - correctionX,
                    y: target.y - correctionY,
                });
                continue;
            }

            if (edge.target === nodeId) {
                nextPositions[edge.source] = clampToCanvas({
                    x: source.x + correctionX,
                    y: source.y + correctionY,
                });
                continue;
            }

            nextPositions[edge.source] = clampToCanvas({
                x: source.x + correctionX * 0.5,
                y: source.y + correctionY * 0.5,
            });
            nextPositions[edge.target] = clampToCanvas({
                x: target.x - correctionX * 0.5,
                y: target.y - correctionY * 0.5,
            });
        }
    }

    return nextPositions;
}

function collapseDistanceEdges(edges: Edge[]): Edge[] {
    const collapsed = new Map<string, { edge: Edge; totalWeight: number; count: number }>();
    for (const edge of edges) {
        const source = Math.min(edge.source, edge.target);
        const target = Math.max(edge.source, edge.target);
        const key = `${source}:${target}`;
        const existing = collapsed.get(key);
        collapsed.set(key, {
            edge: {
                ...edge,
                source,
                target,
                directed: false,
            },
            totalWeight: (existing?.totalWeight ?? 0) + edge.weight,
            count: (existing?.count ?? 0) + 1,
        });
    }
    return [...collapsed.values()].map(({ edge, totalWeight, count }) => ({
        ...edge,
        weight: totalWeight / count,
    }));
}

function alignPairDistance(
    source: Position,
    target: Position,
    desiredDistance: number,
    lockSource: boolean,
    lockTarget: boolean,
) {
    let dx = target.x - source.x;
    let dy = target.y - source.y;
    let currentDistance = Math.hypot(dx, dy);

    if (currentDistance < 0.0001) {
        dx = desiredDistance;
        dy = 0;
        currentDistance = desiredDistance || 1;
    }

    const unitX = dx / currentDistance;
    const unitY = dy / currentDistance;
    const difference = currentDistance - desiredDistance;

    if (Math.abs(difference) < 0.001) {
        return { source, target };
    }

    if (lockSource && !lockTarget) {
        return {
            source,
            target: {
                x: source.x + unitX * desiredDistance,
                y: source.y + unitY * desiredDistance,
            },
        };
    }

    if (lockTarget && !lockSource) {
        return {
            source: {
                x: target.x - unitX * desiredDistance,
                y: target.y - unitY * desiredDistance,
            },
            target,
        };
    }

    const halfShift = difference / 2;
    return {
        source: {
            x: source.x + unitX * halfShift,
            y: source.y + unitY * halfShift,
        },
        target: {
            x: target.x - unitX * halfShift,
            y: target.y - unitY * halfShift,
        },
    };
}
