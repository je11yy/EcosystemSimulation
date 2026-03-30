import { useMemo, useRef, useState } from "react";
import type {
  GenomeTemplateEdge,
  GenomeTemplateGene,
  GenomeTemplateGeneState,
} from "../api/types";

type PositionedGene = GenomeTemplateGene & {
  px: number;
  py: number;
  isActive: boolean;
};

type Props = {
  genes: GenomeTemplateGene[];
  edges: GenomeTemplateEdge[];
  geneStates?: GenomeTemplateGeneState[];
  width?: number;
  height?: number;
  selectedGeneId?: number | null;
  selectedEdgeId?: number | null;
  onGeneClick?: (geneId: number) => void;
  onEdgeClick?: (edgeId: number) => void;
  onGeneMoveEnd?: (geneId: number, x: number, y: number) => void;
  draggable?: boolean;
};

function buildGenePositions(
  genes: GenomeTemplateGene[],
  width: number,
  height: number
): PositionedGene[] {
  if (genes.length === 0) return [];

  const chromosomeGroups = new Map<string, GenomeTemplateGene[]>();

  for (const gene of genes) {
    if (!chromosomeGroups.has(gene.chromosome_id)) {
      chromosomeGroups.set(gene.chromosome_id, []);
    }
    chromosomeGroups.get(gene.chromosome_id)!.push(gene);
  }

  const chromosomes = Array.from(chromosomeGroups.entries()).sort((a, b) =>
    a[0].localeCompare(b[0])
  );

  const columnCount = Math.max(1, chromosomes.length);
  const columnWidth = width / columnCount;

  const positioned: PositionedGene[] = [];

  chromosomes.forEach(([, chromosomeGenes], chromosomeIndex) => {
    const sortedGenes = [...chromosomeGenes].sort((a, b) => a.position - b.position);

    const defaultX = columnWidth * chromosomeIndex + columnWidth / 2;
    const verticalSpacing =
      sortedGenes.length > 1 ? (height - 120) / (sortedGenes.length - 1) : 0;

    sortedGenes.forEach((gene, index) => {
      const defaultY =
        sortedGenes.length === 1 ? height / 2 : 60 + index * verticalSpacing;

      positioned.push({
        ...gene,
        px: gene.x ?? Math.round(defaultX),
        py: gene.y ?? Math.round(defaultY),
        isActive: false,
      });
    });
  });

  return positioned;
}

function getEdgeColor(weight: number): string {
  if (weight > 0) return "#16a34a";
  if (weight < 0) return "#dc2626";
  return "#64748b";
}

export function GenomeGraph({
  genes,
  edges,
  geneStates = [],
  width = 900,
  height = 420,
  selectedGeneId = null,
  selectedEdgeId = null,
  onGeneClick,
  onEdgeClick,
  onGeneMoveEnd,
  draggable = false,
}: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [localPositions, setLocalPositions] = useState<Record<number, { x: number; y: number }>>(
    {}
  );
  const [dragMoved, setDragMoved] = useState(false);

  const baseGenes = useMemo(() => {
    const base = buildGenePositions(genes, width, height);
    const activeMap = new Map(geneStates.map((state) => [state.id, state.is_active]));

    return base.map((gene) => ({
      ...gene,
      isActive: activeMap.get(gene.id) ?? gene.default_active,
    }));
  }, [genes, geneStates, width, height]);

  const positionedGenes = useMemo(() => {
    return baseGenes.map((gene) => ({
      ...gene,
      px: localPositions[gene.id]?.x ?? gene.px,
      py: localPositions[gene.id]?.y ?? gene.py,
    }));
  }, [baseGenes, localPositions]);

  const geneById = new Map(positionedGenes.map((gene) => [gene.id, gene]));

  const chromosomeOrder = Array.from(
    new Set(positionedGenes.map((gene) => gene.chromosome_id))
  ).sort();

  const columnWidth = width / Math.max(1, chromosomeOrder.length);

  const getMousePosition = (event: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
    const svg = svgRef.current;
    if (!svg) return null;

    const rect = svg.getBoundingClientRect();
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;

    return {
      x: (event.clientX - rect.left) * scaleX,
      y: (event.clientY - rect.top) * scaleY,
    };
  };

  const clampGenePosition = (geneId: number, x: number, y: number) => {
    const gene = geneById.get(geneId);
    if (!gene) return { x, y };

    const chromosomeIndex = chromosomeOrder.indexOf(gene.chromosome_id);
    const columnLeft = chromosomeIndex * columnWidth;
    const columnRight = columnLeft + columnWidth;

    const paddingX = 40;
    const paddingY = 40;

    return {
      x: Math.max(columnLeft + paddingX, Math.min(columnRight - paddingX, x)),
      y: Math.max(paddingY, Math.min(height - paddingY, y)),
    };
  };

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 12,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Граф генома</h3>

      {genes.length === 0 ? (
        <p style={{ marginBottom: 0 }}>Гены пока не добавлены.</p>
      ) : (
        <svg
          ref={svgRef}
          width="100%"
          viewBox={`0 0 ${width} ${height}`}
          style={{ display: "block", userSelect: "none" }}
          onMouseMove={(event) => {
            if (!draggingId || !draggable) return;

            const pos = getMousePosition(event);
            if (!pos) return;

            const clamped = clampGenePosition(draggingId, pos.x, pos.y);
            setDragMoved(true);

            setLocalPositions((prev) => ({
              ...prev,
              [draggingId]: {
                x: Math.round(clamped.x),
                y: Math.round(clamped.y),
              },
            }));
          }}
          onMouseUp={() => {
            if (!draggingId) return;

            const finalPos = localPositions[draggingId];
            const moved = dragMoved;
            const id = draggingId;

            setDraggingId(null);
            setDragMoved(false);

            if (moved && finalPos) {
              onGeneMoveEnd?.(id, finalPos.x, finalPos.y);
            }
          }}
          onMouseLeave={() => {
            if (!draggingId) return;

            const finalPos = localPositions[draggingId];
            const moved = dragMoved;
            const id = draggingId;

            setDraggingId(null);
            setDragMoved(false);

            if (moved && finalPos) {
              onGeneMoveEnd?.(id, finalPos.x, finalPos.y);
            }
          }}
        >
          {chromosomeOrder.map((chromosomeId, index) => {
            const x = index * columnWidth + columnWidth / 2;
            const left = index * columnWidth;

            return (
              <g key={chromosomeId}>
                <rect
                  x={left + 8}
                  y={36}
                  width={columnWidth - 16}
                  height={height - 52}
                  fill="#f8fafc"
                  stroke="#e2e8f0"
                  strokeDasharray="4 4"
                  rx={8}
                />
                <text
                  x={x}
                  y={24}
                  textAnchor="middle"
                  fontSize="14"
                  fontWeight="bold"
                  fill="#334155"
                >
                  {chromosomeId}
                </text>
              </g>
            );
          })}

          {edges.map((edge) => {
            const source = geneById.get(edge.source_gene_id);
            const target = geneById.get(edge.target_gene_id);

            if (!source || !target) return null;

            const midX = (source.px + target.px) / 2;
            const midY = (source.py + target.py) / 2;
            const color = getEdgeColor(edge.weight);
            const isSelected = selectedEdgeId === edge.id;

            return (
              <g
                key={edge.id}
                onClick={(event) => {
                  event.stopPropagation();
                  onEdgeClick?.(edge.id);
                }}
                style={{ cursor: "pointer" }}
              >
                <line
                  x1={source.px}
                  y1={source.py}
                  x2={target.px}
                  y2={target.py}
                  stroke={isSelected ? "#2563eb" : color}
                  strokeWidth={isSelected ? 4 : 2}
                />
                <text
                  x={midX}
                  y={midY - 6}
                  textAnchor="middle"
                  fontSize="11"
                  fill={isSelected ? "#2563eb" : color}
                >
                  {edge.weight.toFixed(2)}
                </text>
              </g>
            );
          })}

          {positionedGenes.map((gene) => {
            const isSelected = selectedGeneId === gene.id;

            return (
              <g
                key={gene.id}
                onMouseDown={(event) => {
                  if (!draggable) return;
                  event.stopPropagation();
                  setDraggingId(gene.id);
                  setDragMoved(false);
                }}
                onClick={(event) => {
                  event.stopPropagation();
                  if (dragMoved) return;
                  onGeneClick?.(gene.id);
                }}
                style={{ cursor: draggable ? "grab" : "default" }}
              >
                <circle
                  cx={gene.px}
                  cy={gene.py}
                  r={28}
                  fill={gene.isActive ? "#bfdbfe" : "#f8fafc"}
                  stroke={isSelected ? "#2563eb" : gene.isActive ? "#1d4ed8" : "#334155"}
                  strokeWidth={isSelected ? 4 : 2}
                />
                <text
                  x={gene.px}
                  y={gene.py - 4}
                  textAnchor="middle"
                  fontSize="11"
                  fontWeight="bold"
                  fill="#0f172a"
                >
                  {gene.name}
                </text>
                <text
                  x={gene.px}
                  y={gene.py + 12}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#475569"
                >
                  θ={gene.threshold}
                </text>
              </g>
            );
          })}
        </svg>
      )}

      <div style={{ marginTop: 12, fontSize: 14, color: "#334155" }}>
        <div>Синий узел — активный ген.</div>
        <div>Зелёное ребро — положительное влияние, красное — отрицательное.</div>
        {draggable && <div>Гены можно перетаскивать внутри своей хромосомы.</div>}
      </div>
    </div>
  );
}