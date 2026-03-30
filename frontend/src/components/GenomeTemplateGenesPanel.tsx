import type { GenomeTemplateGene } from "../api/types";

type Props = {
  genes: GenomeTemplateGene[];
};

export function GenomeTemplateGenesPanel({ genes }: Props) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Гены</h3>

      {genes.length === 0 ? (
        <p>Гены пока не добавлены.</p>
      ) : (
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          {genes.map((gene) => (
            <li key={gene.id}>
              <b>{gene.name}</b> | {gene.effect_type} | chr: {gene.chromosome_id} | pos:{" "}
              {gene.position} | threshold: {gene.threshold} | default_active:{" "}
              {String(gene.default_active)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}