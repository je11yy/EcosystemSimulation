import type { Gene } from "./types";
import type { Props } from "../graph/types";
import { GraphComponent } from "../graph/Graph";

export const GenomeGraphComponent = ({
    graph,
    width = 900,
    height = 600,
    selectedNodeId = null,
    onNodeClick,
    selectedEdgeId = null,
    onEdgeClick,
    onNodePositionChange,
    canDragNodes,
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
        canDragNodes={canDragNodes}
        getNodeColor={(node) => {
            const gene = node as Gene;
            return gene.default_active ? 'lightgreen' : 'lightgray';
        }} />
}  
