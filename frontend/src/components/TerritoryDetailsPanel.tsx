import { useMemo, useState } from "react";
import type { AgentState, TerritoryState } from "../api/types";

type Props = {
    territory: TerritoryState | null;
    agents: AgentState[];
    selectedAgentId: string | null;
    edgeTargetMode: boolean;
    edgeSourceTerritoryId: string | null;
    onStartEdgeMode: () => void;
    onCancelEdgeMode: () => void;
    onDelete: (territoryId: string) => void;
    onSave: (
        territoryId: string,
        payload: {
            food: number;
            temperature: number;
            food_regen_per_tick: number;
            food_capacity: number;
            x?: number | null;
            y?: number | null;
        }
    ) => void;
    onAgentClick: (agentId: string) => void;
    isBusy?: boolean;
};

export function TerritoryDetailsPanel({
    territory,
    agents,
    selectedAgentId,
    edgeTargetMode,
    edgeSourceTerritoryId,
    onStartEdgeMode,
    onCancelEdgeMode,
    onDelete,
    onSave,
    onAgentClick,
    isBusy = false,
}: Props) {
    const [form, setForm] = useState({
        food: territory?.food ?? 0,
        temperature: territory?.temperature ?? 0,
        regen: territory?.food_regen_per_tick ?? 0,
        capacity: territory?.food_capacity ?? 0,
        x: territory?.x == null ? "" : String(territory.x),
        y: territory?.y == null ? "" : String(territory.y),
    });
    const [agentsOpen, setAgentsOpen] = useState(false);

    const territoryAgents = useMemo(() => {
        if (!territory) return [];
        return agents.filter((agent) => agent.location === territory.id);
    }, [agents, territory]);

    if (!territory) {
        return (
            <div
                style={{
                    border: "1px solid #ddd",
                    borderRadius: 12,
                    padding: 16,
                    background: "#fff",
                }}
            >
                <h3 style={{ marginTop: 0 }}>Территория</h3>
                <p style={{ marginBottom: 0 }}>Выбери территорию на графе.</p>
            </div>
        );
    }

    const isSourceForEdge = edgeSourceTerritoryId === territory.id;

    return (
        <div
            style={{
                border: "1px solid #ddd",
                borderRadius: 12,
                padding: 16,
                background: "#fff",
            }}
        >
            <h3 style={{ marginTop: 0 }}>Территория #{territory.id}</h3>

            {edgeTargetMode && isSourceForEdge && (
                <p style={{ color: "#1d4ed8" }}>
                    Режим создания ребра включён. Теперь нажми на другую территорию на графе.
                </p>
            )}

            <div style={{ display: "grid", gap: 8 }}>
                <label>
                    Food
                    <input
                        type="number"
                        value={form.food}
                        onChange={(e) => setForm({ ...form, food: Number(e.target.value) })}
                    />
                </label>

                <label>
                    Temperature
                    <input
                        type="number"
                        value={form.temperature}
                        onChange={(e) => setForm({ ...form, temperature: Number(e.target.value) })}
                    />
                </label>

                <label>
                    Food regen
                    <input
                        type="number"
                        value={form.regen}
                        onChange={(e) => setForm({ ...form, regen: Number(e.target.value) })}
                    />
                </label>

                <label>
                    Food capacity
                    <input
                        type="number"
                        value={form.capacity}
                        onChange={(e) => setForm({ ...form, capacity: Number(e.target.value) })}
                    />
                </label>

                <label>
                    X
                    <input value={form.x} onChange={(e) => setForm({ ...form, x: e.target.value })} />
                </label>

                <label>
                    Y
                    <input value={form.y} onChange={(e) => setForm({ ...form, y: e.target.value })} />
                </label>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
                    <button
                        disabled={isBusy}
                        onClick={() =>
                            onSave(territory.id, {
                                food: form.food,
                                temperature: form.temperature,
                                food_regen_per_tick: form.regen,
                                food_capacity: form.capacity,
                                x: form.x.trim() === "" ? null : Number(form.x),
                                y: form.y.trim() === "" ? null : Number(form.y),
                            })
                        }
                    >
                        Сохранить
                    </button>

                    {!edgeTargetMode ? (
                        <button disabled={isBusy} onClick={onStartEdgeMode}>
                            Создать ребро от этой территории
                        </button>
                    ) : isSourceForEdge ? (
                        <button disabled={isBusy} onClick={onCancelEdgeMode}>
                            Отменить создание ребра
                        </button>
                    ) : null}

                    <button
                        disabled={isBusy}
                        onClick={() => onDelete(territory.id)}
                        style={{ color: "#b91c1c" }}
                    >
                        Удалить территорию
                    </button>
                </div>
            </div>

            <div style={{ marginTop: 20 }}>
                <button
                    type="button"
                    onClick={() => setAgentsOpen((prev) => !prev)}
                    style={{ marginBottom: 8 }}
                >
                    {agentsOpen ? "Скрыть агентов" : "Показать агентов"} ({territoryAgents.length})
                </button>

                {agentsOpen && (
                    <>
                        {territoryAgents.length === 0 ? (
                            <p style={{ marginBottom: 0 }}>На этой территории нет агентов.</p>
                        ) : (
                            <ul style={{ margin: 0, paddingLeft: 20 }}>
                                {territoryAgents.map((agent) => {
                                    const activeGenes = agent.gene_states.filter((gene) => gene.is_active).length;
                                    const isSelected = selectedAgentId === agent.id;

                                    return (
                                        <li
                                            key={agent.id}
                                            onClick={() => onAgentClick(agent.id)}
                                            style={{
                                                cursor: "pointer",
                                                background: isSelected ? "#dbeafe" : "transparent",
                                                borderRadius: 6,
                                                padding: "4px 6px",
                                                marginBottom: 4,
                                            }}
                                        >
                                            #{agent.id} | hunger: {agent.hunger} | hp: {agent.hp} | sex: {agent.sex} | active genes: {activeGenes}
                                        </li>
                                    );
                                })}
                            </ul>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}