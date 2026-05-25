import type { Gene } from "./types";
import type { Props } from "../graph/types";
import { GraphComponent } from "../graph/Graph";

export const GenomeGraphComponent = ({
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
        getEdgeLabel={(edge) => edge.weight.toFixed(2)}
        getNodeColor={(node) => {
            const gene = node as Gene;
            return gene.default_active ? 'lightgreen' : 'lightgray';
        }} />
}  
