import type { AgentState } from "../api/types";
import { GenomeGraph } from "./GenomeGraph";

type Props = {
  agent: AgentState | null;
  onDelete: (agentId: string) => void;
  isBusy?: boolean;
};

export function AgentDetailsPanel({ agent, onDelete, isBusy = false }: Props) {
  if (!agent) {
    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "#fff",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Агент</h3>
        <p style={{ marginBottom: 0 }}>Выбери агента в списке.</p>
      </div>
    );
  }

  const activeGenes = agent.gene_states.filter((gene) => gene.is_active);

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Агент #{agent.id}</h3>

      <div style={{ display: "grid", gap: 6 }}>
        <div>territory: <b>{agent.location}</b></div>
        <div>sex: <b>{agent.sex}</b></div>
        <div>hunger: <b>{agent.hunger}</b></div>
        <div>hp: <b>{agent.hp}</b></div>
        <div>base strength: <b>{agent.base_strength}</b></div>
        <div>base defense: <b>{agent.base_defense}</b></div>
        <div>pregnant: <b>{String(agent.pregnant)}</b></div>
        <div>ticks to birth: <b>{agent.ticks_to_birth}</b></div>
        <div>father id: <b>{agent.father_id ?? "—"}</b></div>
        <div>base temp pref: <b>{agent.base_temp_pref}</b></div>
        <div>satisfaction: <b>{agent.satisfaction}</b></div>
        <div>alive: <b>{String(agent.alive)}</b></div>
      </div>

      <div style={{ marginTop: 16 }}>
        <h4 style={{ marginBottom: 8 }}>Genes</h4>
        {agent.genes.length === 0 ? (
          <p>Нет генов.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {agent.genes.map((gene) => (
              <li key={gene.id}>
                {gene.id} | chr: {gene.chromosome_id} | pos: {gene.position} | threshold: {gene.threshold}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <h4 style={{ marginBottom: 8 }}>Active genes</h4>
        {activeGenes.length === 0 ? (
          <p>Нет активных генов.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {activeGenes.map((gene) => (
              <li key={gene.gene_id}>{gene.gene_id}</li>
            ))}
          </ul>
        )}
      </div>

            <div style={{ marginTop: 16 }}>
        <GenomeGraph
          genes={agent.genes.map((gene) => ({
            id: gene.id,
            genome_template_id: 0,
            name: gene.name,
            effect_type: gene.effect_type,
            chromosome_id: gene.chromosome_id,
            position: gene.position,
            default_active: gene.default_active,
            threshold: gene.threshold,
          }))}
          edges={agent.gene_edges.map((edge, index) => ({
            id: index + 1,
            genome_template_id: 0,
            source_gene_id: edge.source_gene_id,
            target_gene_id: edge.target_gene_id,
            weight: edge.weight,
          }))}
          geneStates={agent.gene_states.map((state, index) => ({
            id: index + 1,
            genome_template_id: 0,
            gene_id: state.gene_id,
            effect_type: agent.genes.find((gene) => gene.id === state.gene_id)?.effect_type || "unknown",
            is_active: state.is_active,
          }))}
          width={700}
          height={320}
        />
      </div>

      <div style={{ marginTop: 16 }}>
        <button
          disabled={isBusy}
          onClick={() => onDelete(agent.id)}
          style={{ color: "#b91c1c" }}
        >
          Удалить агента
        </button>
      </div>
    </div>
  );
}