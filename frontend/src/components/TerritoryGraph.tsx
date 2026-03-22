import { useMemo, useRef, useState } from "react";
import type { AgentState, TerritoryEdgeState, TerritoryState } from "../api/types";

type PositionedTerritory = TerritoryState & {
  px: number;
  py: number;
};

type TerritoryPosition = {
  id: string;
  px: number;
  py: number;
};

type Props = {
  territories: TerritoryState[];
  edges: TerritoryEdgeState[];
  agents: AgentState[];
  width?: number;
  height?: number;
  selectedTerritoryId?: string | null;
  selectedEdgeId?: number | null;
  edgeCreationMode?: boolean;
  onTerritoryClick?: (territoryId: string) => void;
  onEdgeClick?: (edgeId: number) => void;
  onTerritoryMoveEnd?: (territoryId: string, x: number, y: number) => void;
};

function buildPositions(
  territories: TerritoryState[],
  width: number,
  height: number
): PositionedTerritory[] {
  const hasCoordinates = territories.every(
    (territory) =>
      territory.x !== undefined &&
      territory.x !== null &&
      territory.y !== undefined &&
      territory.y !== null
  );

  if (hasCoordinates) {
    return territories.map((territory) => ({
      ...territory,
      px: territory.x as number,
      py: territory.y as number,
    }));
  }

  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) * 0.35;

  return territories.map((territory, index) => {
    const angle = (2 * Math.PI * index) / Math.max(1, territories.length);
    return {
      ...territory,
      px: cx + radius * Math.cos(angle),
      py: cy + radius * Math.sin(angle),
    };
  });
}

function getFoodFill(food: number, capacity: number): string {
  const ratio = capacity > 0 ? food / capacity : 0;

  if (ratio >= 0.75) return "#86efac";
  if (ratio >= 0.45) return "#fde68a";
  if (ratio >= 0.2) return "#fdba74";
  return "#fca5a5";
}

export function TerritoryGraph({
  territories,
  edges,
  agents,
  width = 900,
  height = 520,
  selectedTerritoryId = null,
  selectedEdgeId = null,
  edgeCreationMode = false,
  onTerritoryClick,
  onEdgeClick,
  onTerritoryMoveEnd,
}: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [localPositions, setLocalPositions] = useState<Record<string, TerritoryPosition>>({});
  const [dragMoved, setDragMoved] = useState(false);

  const basePositioned = useMemo(
    () => buildPositions(territories, width, height),
    [territories, width, height]
  );

  const positioned = useMemo(() => {
    return basePositioned.map((territory) => {
      const local = localPositions[territory.id];
      if (!local) return territory;
      return {
        ...territory,
        px: local.px,
        py: local.py,
      };
    });
  }, [basePositioned, localPositions]);

  const territoryById = new Map(positioned.map((territory) => [territory.id, territory]));

  const agentCountByTerritory = agents.reduce<Record<string, number>>((acc, agent) => {
    acc[agent.location] = (acc[agent.location] ?? 0) + 1;
    return acc;
  }, {});

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

  const clampToCanvas = (x: number, y: number) => {
    const padding = 40;

    return {
      x: Math.max(padding, Math.min(width - padding, x)),
      y: Math.max(padding, Math.min(height - padding, y)),
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
      <h3 style={{ marginTop: 0 }}>Граф территорий</h3>

      {edgeCreationMode && (
        <p style={{ marginTop: 0, color: "#1d4ed8" }}>
          Режим создания ребра: выбери вторую территорию.
        </p>
      )}

      <svg
        ref={svgRef}
        width="100%"
        viewBox={`0 0 ${width} ${height}`}
        style={{ display: "block", userSelect: "none" }}
        onMouseMove={(event) => {
          if (!draggingId) return;

          const pos = getMousePosition(event);
          if (!pos) return;

          const clamped = clampToCanvas(pos.x, pos.y);
          setDragMoved(true);

          setLocalPositions((prev) => ({
            ...prev,
            [draggingId]: {
              id: draggingId,
              px: clamped.x,
              py: clamped.y,
            },
          }));
        }}
        onMouseUp={() => {
          if (!draggingId) return;

          const finalPosition = localPositions[draggingId];
          const moved = dragMoved;
          const finishedId = draggingId;

          setDraggingId(null);
          setDragMoved(false);

          if (moved && finalPosition) {
            onTerritoryMoveEnd?.(
              finishedId,
              Math.round(finalPosition.px),
              Math.round(finalPosition.py)
            );
          }
        }}
        onMouseLeave={() => {
          if (!draggingId) return;

          const finalPosition = localPositions[draggingId];
          const moved = dragMoved;
          const finishedId = draggingId;

          setDraggingId(null);
          setDragMoved(false);

          if (moved && finalPosition) {
            onTerritoryMoveEnd?.(
              finishedId,
              Math.round(finalPosition.px),
              Math.round(finalPosition.py)
            );
          }
        }}
      >
        {edges.map((edge) => {
          const source = territoryById.get(edge.source_id);
          const target = territoryById.get(edge.target_id);

          if (!source || !target) return null;

          const midX = (source.px + target.px) / 2;
          const midY = (source.py + target.py) / 2;
          const isSelected = selectedEdgeId === edge.id;

          return (
            <g key={edge.id} onClick={(e) => {
              e.stopPropagation();
              onEdgeClick?.(edge.id);
            }} style={{ cursor: "pointer" }}>
              <line
                x1={source.px}
                y1={source.py}
                x2={target.px}
                y2={target.py}
                stroke={isSelected ? "#2563eb" : "#94a3b8"}
                strokeWidth={isSelected ? 4 : 2}
              />
              <text
                x={midX}
                y={midY - 6}
                textAnchor="middle"
                fontSize="11"
                fill="#475569"
              >
                {edge.movement_cost}
              </text>
            </g>
          );
        })}

        {positioned.map((territory) => {
          const agentsHere = agentCountByTerritory[territory.id] ?? 0;
          const fill = getFoodFill(territory.food, territory.food_capacity);
          const isSelected = selectedTerritoryId === territory.id;

          return (
            <g
              key={territory.id}
              onMouseDown={(event) => {
                event.stopPropagation();
                setDraggingId(territory.id);
                setDragMoved(false);
              }}
              onClick={(event) => {
                event.stopPropagation();
                if (dragMoved) return;
                onTerritoryClick?.(territory.id);
              }}
              style={{ cursor: "grab" }}
            >
              <circle
                cx={territory.px}
                cy={territory.py}
                r={34}
                fill={fill}
                stroke={isSelected ? "#2563eb" : "#334155"}
                strokeWidth={isSelected ? 4 : 2}
              />
              <text
                x={territory.px}
                y={territory.py + 4}
                textAnchor="middle"
                fontSize="12"
                fontWeight="bold"
                fill="#0f172a"
              >
                #{territory.id}
              </text>

              {agentsHere > 0 && (
                <>
                  <circle
                    cx={territory.px + 24}
                    cy={territory.py - 24}
                    r={13}
                    fill="#2563eb"
                    stroke="#1e3a8a"
                    strokeWidth={1.5}
                  />
                  <text
                    x={territory.px + 24}
                    y={territory.py - 20}
                    textAnchor="middle"
                    fontSize="11"
                    fontWeight="bold"
                    fill="#ffffff"
                  >
                    {agentsHere}
                  </text>
                </>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}