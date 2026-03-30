import { useState } from "react";
import type { GenomeTemplateRead, TerritoryState } from "../api/types";

type Props = {
  territories: TerritoryState[];
  genomeTemplates: GenomeTemplateRead[];
  onSubmit: (payload: {
    territory_id: number;
    genome_template_id: number;
    hunger: number;
    hp: number;
    base_strength: number;
    base_defense: number;
    sex: string;
    pregnant: boolean;
    ticks_to_birth: number;
    father_id?: number | null;
    base_temp_pref: number;
    satisfaction: number;
    alive: boolean;
  }) => void;
  isBusy?: boolean;
};

export function CreateAgentForm({
  territories,
  genomeTemplates,
  onSubmit,
  isBusy = false,
}: Props) {
  const [territoryId, setTerritoryId] = useState<number | "">("");
  const [genomeTemplateId, setGenomeTemplateId] = useState<number | "">("");
  const [hunger, setHunger] = useState(0);
  const [hp, setHp] = useState(5);
  const [baseStrength, setBaseStrength] = useState(3);
  const [baseDefense, setBaseDefense] = useState(3);
  const [sex, setSex] = useState("female");
  const [baseTempPref, setBaseTempPref] = useState(20);
  const [satisfaction, setSatisfaction] = useState(1);

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Новый агент</h3>

      <div style={{ display: "grid", gap: 8 }}>
        <select
          value={territoryId}
          onChange={(e) => setTerritoryId(e.target.value === "" ? "" : Number(e.target.value))}
        >
          <option value="">Выбери территорию</option>
          {territories.map((territory) => (
            <option key={territory.id} value={territory.id}>
              #{territory.id}
            </option>
          ))}
        </select>

        <select
          value={genomeTemplateId}
          onChange={(e) =>
            setGenomeTemplateId(e.target.value === "" ? "" : Number(e.target.value))
          }
        >
          <option value="">Выбери шаблон генома</option>
          {genomeTemplates.map((template) => (
            <option key={template.id} value={template.id}>
              {template.name} ({template.species_group})
            </option>
          ))}
        </select>

        <input type="number" value={hunger} onChange={(e) => setHunger(Number(e.target.value))} placeholder="Hunger" />
        <input type="number" value={hp} onChange={(e) => setHp(Number(e.target.value))} placeholder="HP" />
        <input type="number" value={baseStrength} onChange={(e) => setBaseStrength(Number(e.target.value))} placeholder="Base strength" />
        <input type="number" value={baseDefense} onChange={(e) => setBaseDefense(Number(e.target.value))} placeholder="Base defense" />
        <select value={sex} onChange={(e) => setSex(e.target.value)}>
          <option value="female">female</option>
          <option value="male">male</option>
        </select>
        <input type="number" value={baseTempPref} onChange={(e) => setBaseTempPref(Number(e.target.value))} placeholder="Base temp pref" />
        <input type="number" step="0.1" value={satisfaction} onChange={(e) => setSatisfaction(Number(e.target.value))} placeholder="Satisfaction" />

        <button
          disabled={isBusy || territoryId === "" || genomeTemplateId === ""}
          onClick={() =>
            onSubmit({
              territory_id: Number(territoryId),
              genome_template_id: Number(genomeTemplateId),
              hunger,
              hp,
              base_strength: baseStrength,
              base_defense: baseDefense,
              sex,
              pregnant: false,
              ticks_to_birth: 0,
              father_id: null,
              base_temp_pref: baseTempPref,
              satisfaction,
              alive: true,
            })
          }
        >
          Создать агента
        </button>
      </div>
    </div>
  );
}