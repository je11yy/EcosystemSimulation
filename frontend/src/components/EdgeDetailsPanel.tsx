import type { TerritoryEdgeState } from "../api/types";

type Props = {
  edge: TerritoryEdgeState | null;
  onDelete: (edgeId: number) => void;
  isBusy?: boolean;
};

export function EdgeDetailsPanel({ edge, onDelete, isBusy = false }: Props) {
  if (!edge) {
    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "#fff",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Ребро</h3>
        <p style={{ marginBottom: 0 }}>Выбери ребро на графе.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Ребро #{edge.id}</h3>

      <p>
        <b>{edge.source_id}</b> → <b>{edge.target_id}</b>
      </p>

      <p>movement cost: {edge.movement_cost}</p>

      <button
        disabled={isBusy}
        onClick={() => onDelete(edge.id)}
        style={{ color: "#b91c1c" }}
      >
        Удалить ребро
      </button>
    </div>
  );
}