import React from 'react';
import type {Props} from './types';

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
}: Props) => {
    const nodeById = new Map(graph.nodes.map(node => [node.id, node]));
    const [draggingNodeId, setDraggingNodeId] = React.useState<number | null>(null);

    const handleMouseDown = (nodeId: number) => {
        setDraggingNodeId(nodeId);
    };

    const handleMouseMove = (event: React.MouseEvent) => {
        if (draggingNodeId !== null) {
            const svg = event.currentTarget as SVGSVGElement;
            const point = svg.createSVGPoint();
            point.x = event.clientX;
            point.y = event.clientY;
            const cursorPoint = point.matrixTransform(svg.getScreenCTM()?.inverse());
            onNodePositionChange(draggingNodeId, {x: cursorPoint.x, y: cursorPoint.y});
        }
    };

    const handleMouseUp = () => {
        setDraggingNodeId(null);
    };

    return (
        <svg
            width={width}
            height={height}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            style={{border: '1px solid black'}}
        >
            {graph.edges.map(edge => {
                const sourceNode = nodeById.get(edge.source);
                const targetNode = nodeById.get(edge.target);
                if (!sourceNode || !targetNode) return null;
                return (
                    <line
                        key={edge.id}
                        x1={sourceNode.position.x}
                        y1={sourceNode.position.y}
                        x2={targetNode.position.x}
                        y2={targetNode.position.y}
                        stroke={edge.id === selectedEdgeId ? 'lightblue' : 'black'}
                        strokeWidth={2}
                        onClick={() => onEdgeClick(edge.id)}
                    />
                );
            })}
            {graph.nodes.map(node => (
                <circle
                    key={node.id}
                    cx={node.position.x}
                    cy={node.position.y}
                    r={20}
                    fill={getNodeColor ? getNodeColor(node) : 'white'}
                    stroke={node.id === selectedNodeId ? 'lightblue' : 'black'}
                    strokeWidth={1}
                    onMouseDown={() => handleMouseDown(node.id)}
                    onClick={() => onNodeClick(node.id)}
                />
            ))}
        </svg>
    );
};
