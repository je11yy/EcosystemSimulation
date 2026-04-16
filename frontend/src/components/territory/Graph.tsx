import type { Territory } from "./types";
import type { Props } from "../graph/types";
import { GraphComponent } from "../graph/Graph";

export const TerritoryGraphComponent = ({
    graph,
    width = 900,
    height = 600,
    selectedNodeId = null,
    onNodeClick,
    selectedEdgeId = null,
    onEdgeClick,
    onNodePositionChange,
}: Props) => {
    return <GraphComponent
        graph={graph}
        width={width}
        height={height}
        selectedNodeId={selectedNodeId}
        onNodeClick={onNodeClick}
        selectedEdgeId={selectedEdgeId}
        onEdgeClick={onEdgeClick}
        onNodePositionChange={onNodePositionChange}
        getNodeColor={(node) => {
            const foodRatio = (node as Territory).food / (node as Territory).food_capacity;
            const red = Math.min(255, Math.floor(255 * foodRatio));
            const green = Math.min(255, Math.floor(255 * (1 - foodRatio)));
            return `rgb(${red}, ${green}, 0)`;
        }} />
}