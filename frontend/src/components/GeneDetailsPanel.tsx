import type { GenomeTemplateGene, GenomeTemplateGeneState } from "../api/types";

type Props = {
  gene: GenomeTemplateGene | null;
  geneState: GenomeTemplateGeneState | null;
  onDelete: (geneId: number) => void;
  isBusy?: boolean;
};

export function GeneDetailsPanel({
  gene,
  geneState,
  onDelete,
  isBusy = false,
}: Props) {
  if (!gene) {
    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "#fff",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Ген</h3>
        <p style={{ marginBottom: 0 }}>Выбери ген на графе.</p>
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
      <h3 style={{ marginTop: 0 }}>Ген #{gene.id}</h3>

      <div style={{ display: "grid", gap: 6 }}>
        <div>name: <b>{gene.name}</b></div>
        <div>effect type: <b>{gene.effect_type}</b></div>
        <div>chromosome: <b>{gene.chromosome_id}</b></div>
        <div>position: <b>{gene.position}</b></div>
        <div>threshold: <b>{gene.threshold}</b></div>
        <div>default active: <b>{String(gene.default_active)}</b></div>
        <div>current active: <b>{String(geneState?.is_active ?? gene.default_active)}</b></div>
        <div>x: <b>{gene.x ?? "—"}</b></div>
        <div>y: <b>{gene.y ?? "—"}</b></div>
      </div>

      <div style={{ marginTop: 16 }}>
        <button
          disabled={isBusy}
          onClick={() => onDelete(gene.id)}
          style={{ color: "#b91c1c" }}
        >
          Удалить ген
        </button>
      </div>
    </div>
  );
}