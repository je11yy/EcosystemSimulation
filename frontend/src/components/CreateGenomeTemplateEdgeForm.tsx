import { useState } from "react";
import type { GenomeTemplateGene } from "../api/types";

type Props = {
  genes: GenomeTemplateGene[];
  onSubmit: (payload: {
    source_gene_id: number;
    target_gene_id: number;
    weight: number;
  }) => void;
  isBusy?: boolean;
};

export function CreateGenomeTemplateEdgeForm({
  genes,
  onSubmit,
  isBusy = false,
}: Props) {
  const [source, setSource] = useState<number | "">("");
  const [target, setTarget] = useState<number | "">("");
  const [weight, setWeight] = useState(0.5);

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Добавить ребро</h3>

      <div style={{ display: "grid", gap: 8 }}>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value === "" ? "" : Number(e.target.value))}
        >
          <option value="">Выбери source gene</option>
          {genes.map((gene) => (
            <option key={gene.id} value={gene.id}>
              {gene.name} ({gene.effect_type})
            </option>
          ))}
        </select>

        <select
          value={target}
          onChange={(e) => setTarget(e.target.value === "" ? "" : Number(e.target.value))}
        >
          <option value="">Выбери target gene</option>
          {genes.map((gene) => (
            <option key={gene.id} value={gene.id}>
              {gene.name} ({gene.effect_type})
            </option>
          ))}
        </select>

        <input
          type="number"
          value={weight}
          onChange={(e) => setWeight(Number(e.target.value))}
          placeholder="Weight"
        />

        <button
          disabled={isBusy || source === "" || target === ""}
          onClick={() =>
            onSubmit({
              source_gene_id: Number(source),
              target_gene_id: Number(target),
              weight,
            })
          }
        >
          Добавить ребро
        </button>
      </div>
    </div>
  );
}