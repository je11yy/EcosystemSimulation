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
            const gene = node as Gene;
            return gene.is_active ? 'lightgreen' : 'lightgray';
        }} />
}  
