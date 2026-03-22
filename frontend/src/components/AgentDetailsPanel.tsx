import type { AgentState } from "../api/types";

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