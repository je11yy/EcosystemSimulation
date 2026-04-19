import React from 'react';
import type { Node, Position, Props } from './types';

export const GraphComponent = ({
    graph,
    width = 900,
    height = 600,
    selectedNodeId = null,
    onNodeClick,
    selectedEdgeId = null,
    onEdgeClick,
    onNodePositionChange,
    getNodeColor,
    canDragNodes = true,
}: Props) => {
    const nodeById = new Map(graph.nodes.map(node => [node.id, node]));
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
            dragRef.current = {
                ...dragRef.current,
                current: cursorPoint,
                moved: dragRef.current.moved || movedDistance > 3,
            };

            const nodeId = dragRef.current.nodeId;
            setDraftPositions((current) => ({
                ...current,
                [nodeId]: cursorPoint,
            }));
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
            width={width}
            height={height}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
        >
            {graph.edges.map(edge => {
                const sourceNode = nodeById.get(edge.source);
                const targetNode = nodeById.get(edge.target);
                if (!sourceNode || !targetNode) return null;
                const sourcePosition = getNodePosition(sourceNode);
                const targetPosition = getNodePosition(targetNode);
                return (
                    <line
                        key={edge.id}
                        x1={sourcePosition.x}
                        y1={sourcePosition.y}
                        x2={targetPosition.x}
                        y2={targetPosition.y}
                        stroke={edge.id === selectedEdgeId ? 'lightblue' : 'black'}
                        strokeWidth={2}
                        onClick={() => onEdgeClick(edge.id)}
                    />
                );
            })}
            {graph.nodes.map(node => {
                const position = getNodePosition(node);
                return (
                    <circle
                        key={node.id}
                        cx={position.x}
                        cy={position.y}
                        r={20}
                        fill={getNodeColor ? getNodeColor(node) : 'white'}
                        stroke={node.id === selectedNodeId ? 'lightblue' : 'black'}
                        strokeWidth={1}
                        onMouseDown={(event) => handleMouseDown(event, node.id)}
                        onClick={() => handleNodeClick(node.id)}
                        style={{ cursor: canDragNodes ? "grab" : "pointer" }}
                    />
                );
            })}
        </svg>
    );
};

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
