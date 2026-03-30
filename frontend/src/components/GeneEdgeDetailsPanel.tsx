import type { GenomeTemplateEdge, GenomeTemplateGene } from "../api/types";

type Props = {
  edge: GenomeTemplateEdge | null;
  genes: GenomeTemplateGene[];
  onDelete: (edgeId: number) => void;
  isBusy?: boolean;
};

export function GeneEdgeDetailsPanel({
  edge,
  genes,
  onDelete,
  isBusy = false,
}: Props) {
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

  const source = genes.find((gene) => gene.id === edge.source_gene_id);
  const target = genes.find((gene) => gene.id === edge.target_gene_id);

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

      <div style={{ display: "grid", gap: 6 }}>
        <div>source: <b>{source?.name ?? edge.source_gene_id}</b></div>
        <div>target: <b>{target?.name ?? edge.target_gene_id}</b></div>
        <div>weight: <b>{edge.weight}</b></div>
      </div>

      <div style={{ marginTop: 16 }}>
        <button
          disabled={isBusy}
          onClick={() => onDelete(edge.id)}
          style={{ color: "#b91c1c" }}
        >
          Удалить ребро
        </button>
      </div>
    </div>
  );
}