import { useState } from "react";
import { GENE_EFFECT_TYPES } from "../constants/geneEffectTypes";

type Props = {
    onSubmit: (payload: {
        effect_type: string;
        name: string;
        chromosome_id: string;
        position: number;
        default_active: boolean;
        threshold: number;
    }) => void;
    isBusy?: boolean;
};

export function CreateGenomeTemplateGeneForm({ onSubmit, isBusy = false }: Props) {
    const [name, setName] = useState("");
    const [chromosomeId, setChromosomeId] = useState("chr1");
    const [effectType, setEffectType] = useState("");
    const [position, setPosition] = useState(1);
    const [defaultActive, setDefaultActive] = useState(false);
    const [threshold, setThreshold] = useState(0);

    return (
        <div
            style={{
                border: "1px solid #ddd",
                borderRadius: 12,
                padding: 16,
                background: "#fff",
            }}
        >
            <h3 style={{ marginTop: 0 }}>Добавить ген</h3>

            <div style={{ display: "grid", gap: 8 }}>
                <select
                    value={effectType}
                    onChange={(e) => setEffectType(e.target.value)}
                >
                    <option value="">Тип гена</option>
                    {GENE_EFFECT_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                            {type.label}
                        </option>
                    ))}
                </select>
                <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Gene name"
                />
                <input
                    value={chromosomeId}
                    onChange={(e) => setChromosomeId(e.target.value)}
                    placeholder="Chromosome id"
                />
                <input
                    type="number"
                    value={position}
                    onChange={(e) => setPosition(Number(e.target.value))}
                    placeholder="Position"
                />
                <input
                    type="number"
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                    placeholder="Threshold"
                />

                <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <input
                        type="checkbox"
                        checked={defaultActive}
                        onChange={(e) => setDefaultActive(e.target.checked)}
                    />
                    default active
                </label>

                <button
                    disabled={isBusy || !effectType || !name.trim() || !chromosomeId.trim()}
                    onClick={() =>
                        onSubmit({
                            effect_type: effectType,
                            name: name.trim(),
                            chromosome_id: chromosomeId.trim(),
                            position,
                            default_active: defaultActive,
                            threshold,
                        })
                    }
                >
                    Добавить ген
                </button>
            </div>
        </div>
    );
}