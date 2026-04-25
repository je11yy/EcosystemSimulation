import React from 'react';
import type { Node, Position, Props } from './types';

export const GraphComponent = ({
    graph,
    selectedNodeId = null,
    onNodeClick,
    selectedEdgeId = null,
    onEdgeClick,
    onNodePositionChange,
    getNodeColor,
    getEdgeLabel,
    renderNodeContent,
    constrainNodePosition,
    resolveDragPositions,
    canDragNodes = true,
}: Props) => {
    const nodeById = new Map(graph.nodes.map(node => [node.id, node]));
    const pairedEdgeIds = React.useMemo(() => {
        const pairs = new Set<number>();
        const edgeByKey = new Map(graph.edges.map((edge) => [`${edge.source}:${edge.target}`, edge.id]));
        for (const edge of graph.edges) {
            if (edgeByKey.has(`${edge.target}:${edge.source}`)) {
                pairs.add(edge.id);
            }
        }
        return pairs;
    }, [graph.edges]);
    const [draftPositions, setDraftPositions] = React.useState<Record<number, Position>>({});
    const dragRef = React.useRef<{
        nodeId: number;
        start: Position;
        current: Position;
        moved: boolean;
    } | null>(null);
    const suppressClickRef = React.useRef(false);

    React.useEffect(() => {
        const nodeIds = new Set(graph.nodes.map(node => node.id));
        setDraftPositions((current) => {
            const next = Object.fromEntries(
                Object.entries(current).filter(([nodeId]) => nodeIds.has(Number(nodeId))),
            );
            return next;
        });
    }, [graph.nodes]);

    const getNodePosition = (node: Node) => draftPositions[node.id] ?? node.position;
    const getResolvedPositions = React.useCallback(
        () => Object.fromEntries(graph.nodes.map(node => [node.id, getNodePosition(node)])),
        [graph.nodes, draftPositions],
    );
    const resolvedPositions = getResolvedPositions();
    const portOffsetsByEdgeId = React.useMemo(
        () => buildPortOffsetsByEdgeId(graph.edges, graph.nodes, resolvedPositions),
        [graph.edges, graph.nodes, resolvedPositions],
    );

    const handleMouseDown = (event: React.MouseEvent, nodeId: number) => {
        if (!canDragNodes) {
            return;
        }

        const point = getSvgPoint(event);
        if (point === null) {
            return;
        }

        dragRef.current = {
            nodeId,
            start: point,
            current: point,
            moved: false,
        };
    };

    const handleMouseMove = (event: React.MouseEvent) => {
        if (dragRef.current !== null) {
            const cursorPoint = getSvgPoint(event);
            if (cursorPoint === null) {
                return;
            }

            const movedDistance = Math.hypot(
                cursorPoint.x - dragRef.current.start.x,
                cursorPoint.y - dragRef.current.start.y,
            );
            const nodeId = dragRef.current.nodeId;
            const constrainedPoint = constrainNodePosition
                ? constrainNodePosition(nodeId, cursorPoint, graph, getResolvedPositions())
                : cursorPoint;
            const nextPositions = resolveDragPositions
                ? resolveDragPositions(nodeId, constrainedPoint, graph, getResolvedPositions())
                : { ...getResolvedPositions(), [nodeId]: constrainedPoint };

            dragRef.current = {
                ...dragRef.current,
                current: nextPositions[nodeId] ?? constrainedPoint,
                moved: dragRef.current.moved || movedDistance > 3,
            };

            setDraftPositions(nextPositions);
        }
    };

    const handleMouseUp = () => {
        if (dragRef.current === null) {
            return;
        }

        const dragState = dragRef.current;
        dragRef.current = null;

        if (dragState.moved) {
            suppressClickRef.current = true;
            onNodePositionChange(dragState.nodeId, dragState.current);
        }
    };

    const handleNodeClick = (nodeId: number) => {
        if (suppressClickRef.current) {
            suppressClickRef.current = false;
            return;
        }

        onNodeClick(nodeId);
    };

    return (
        <svg
            className="graph-canvas"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
        >
            <defs>
                <marker
                    id="graph-arrowhead"
                    viewBox="0 0 10 10"
                    refX="9"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
                </marker>
            </defs>
            {graph.edges.map(edge => {
                const sourceNode = nodeById.get(edge.source);
                const targetNode = nodeById.get(edge.target);
                if (!sourceNode || !targetNode) return null;
                const sourcePosition = getNodePosition(sourceNode);
                const targetPosition = getNodePosition(targetNode);
                const portOffsets = portOffsetsByEdgeId.get(edge.id);
                const edgeGeometry = getEdgeGeometry(
                    sourcePosition,
                    targetPosition,
                    pairedEdgeIds.has(edge.id),
                    edge.source < edge.target ? 1 : -1,
                    portOffsets?.source ?? 0,
                    portOffsets?.target ?? 0,
                );
                const stroke = edge.id === selectedEdgeId ? "lightblue" : "black";
                return (
                    <g key={edge.id}>
                        <path
                            d={edgeGeometry.path}
                            stroke={stroke}
                            strokeWidth={1.4}
                            fill="none"
                            color={stroke}
                            markerStart={edge.bidirectionalArrows ? "url(#graph-arrowhead)" : undefined}
                            markerEnd={
                                edge.directed === false && !edge.bidirectionalArrows
                                    ? undefined
                                    : "url(#graph-arrowhead)"
                            }
                            onClick={() => onEdgeClick(edge.id)}
                        />
                        {getEdgeLabel?.(edge) && (
                            <text
                                x={edgeGeometry.label.x}
                                y={edgeGeometry.label.y}
                                textAnchor="middle"
                                className="graph-edge-label"
                                onClick={() => onEdgeClick(edge.id)}
                            >
                                {getEdgeLabel(edge)}
                            </text>
                        )}
                    </g>
                );
            })}
            {graph.nodes.map(node => {
                const position = getNodePosition(node);
                return (
                    <g
                        key={node.id}
                        onMouseDown={(event) => handleMouseDown(event, node.id)}
                        onClick={() => handleNodeClick(node.id)}
                        style={{ cursor: canDragNodes ? "grab" : "pointer" }}
                    >
                        <circle
                            cx={position.x}
                            cy={position.y}
                            r={NODE_RADIUS}
                            fill={getNodeColor ? getNodeColor(node) : 'white'}
                            stroke={node.id === selectedNodeId ? 'lightblue' : 'black'}
                            strokeWidth={1}
                        />
                        {renderNodeContent?.(node, position, node.id === selectedNodeId)}
                    </g>
                );
            })}
        </svg>
    );
};

const NODE_RADIUS = 28;
const ARROW_OFFSET = 1.5;
const PARALLEL_EDGE_OFFSET = 18;
const PARALLEL_CURVE_OFFSET = 42;
const PORT_SPACING = 8;

function getEdgeGeometry(
    source: Position,
    target: Position,
    isBidirectional: boolean,
    directionSign: number,
    sourcePortOffset: number,
    targetPortOffset: number,
) {
    const adjusted = adjustEdgeEndpoints(
        source,
        target,
        isBidirectional,
        directionSign,
        sourcePortOffset,
        targetPortOffset,
    );
    const midX = (adjusted.source.x + adjusted.target.x) / 2;
    const midY = (adjusted.source.y + adjusted.target.y) / 2;
    if (!isBidirectional) {
        return {
            path: `M ${adjusted.source.x} ${adjusted.source.y} L ${adjusted.target.x} ${adjusted.target.y}`,
            label: { x: midX, y: midY - 8 },
        };
    }

    const dx = adjusted.target.x - adjusted.source.x;
    const dy = adjusted.target.y - adjusted.source.y;
    const distance = Math.hypot(dx, dy) || 1;
    const normalX = -dy / distance;
    const normalY = dx / distance;
    const curveOffset = PARALLEL_CURVE_OFFSET * directionSign;
    const control = {
        x: midX + normalX * curveOffset,
        y: midY + normalY * curveOffset,
    };
    return {
        path: `M ${adjusted.source.x} ${adjusted.source.y} Q ${control.x} ${control.y} ${adjusted.target.x} ${adjusted.target.y}`,
        label: {
            x: (adjusted.source.x + 2 * control.x + adjusted.target.x) / 4,
            y: (adjusted.source.y + 2 * control.y + adjusted.target.y) / 4 - 8,
        },
    };
}

function adjustEdgeEndpoints(
    source: Position,
    target: Position,
    isBidirectional: boolean,
    directionSign: number,
    sourcePortOffset: number,
    targetPortOffset: number,
) {
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const distance = Math.hypot(dx, dy) || 1;
    const unitX = dx / distance;
    const unitY = dy / distance;
    const normalX = -unitY;
    const normalY = unitX;
    const parallelOffset = isBidirectional ? PARALLEL_EDGE_OFFSET * directionSign : 0;
    const sourceLateralOffset = parallelOffset + sourcePortOffset;
    const targetLateralOffset = parallelOffset + targetPortOffset;
    const startOffset = Math.sqrt(Math.max(0, NODE_RADIUS ** 2 - sourceLateralOffset ** 2));
    const endOffset = Math.sqrt(Math.max(0, NODE_RADIUS ** 2 - targetLateralOffset ** 2)) + ARROW_OFFSET;

    return {
        source: {
            x: source.x + unitX * startOffset + normalX * sourceLateralOffset,
            y: source.y + unitY * startOffset + normalY * sourceLateralOffset,
        },
        target: {
            x: target.x - unitX * endOffset + normalX * targetLateralOffset,
            y: target.y - unitY * endOffset + normalY * targetLateralOffset,
        },
    };
}

function buildPortOffsetsByEdgeId(
    edges: Props["graph"]["edges"],
    nodes: Node[],
    positions: Record<number, Position>,
) {
    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    const incidents = new Map<
        number,
        Array<{ edgeId: number; angle: number; endpoint: "source" | "target"; manualOffset: number }>
    >();

    for (const edge of edges) {
        const sourceNode = nodeById.get(edge.source);
        const targetNode = nodeById.get(edge.target);
        if (!sourceNode || !targetNode) {
            continue;
        }

        const source = positions[edge.source] ?? sourceNode.position;
        const target = positions[edge.target] ?? targetNode.position;
        const sourceAngle = Math.atan2(target.y - source.y, target.x - source.x);
        const targetAngle = Math.atan2(source.y - target.y, source.x - target.x);

        incidents.set(edge.source, [
            ...(incidents.get(edge.source) ?? []),
            {
                edgeId: edge.id,
                angle: sourceAngle,
                endpoint: "source",
                manualOffset: edge.sourcePortOffset ?? 0,
            },
        ]);
        incidents.set(edge.target, [
            ...(incidents.get(edge.target) ?? []),
            {
                edgeId: edge.id,
                angle: targetAngle,
                endpoint: "target",
                manualOffset: edge.targetPortOffset ?? 0,
            },
        ]);
    }

    const offsets = new Map<number, { source: number; target: number }>();
    for (const incidentEntries of incidents.values()) {
        const sorted = [...incidentEntries].sort((left, right) => left.angle - right.angle);
        const centerIndex = (sorted.length - 1) / 2;

        sorted.forEach((entry, index) => {
            const offset = (index - centerIndex) * PORT_SPACING + entry.manualOffset;
            const current = offsets.get(entry.edgeId) ?? { source: 0, target: 0 };
            current[entry.endpoint] = offset;
            offsets.set(entry.edgeId, current);
        });
    }

    return offsets;
}

function getSvgPoint(event: React.MouseEvent): Position | null {
    const target = event.currentTarget as SVGElement;
    const svg = target instanceof SVGSVGElement ? target : target.ownerSVGElement;
    if (svg === null) {
        return null;
    }

    const matrix = svg.getScreenCTM();
    if (matrix === null) {
        return null;
    }

    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const cursorPoint = point.matrixTransform(matrix.inverse());
    return { x: cursorPoint.x, y: cursorPoint.y };
}
