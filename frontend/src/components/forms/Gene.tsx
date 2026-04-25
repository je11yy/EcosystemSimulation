import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { GeneCreate } from "src/api/types";
import { getGeneEffectMeta } from "src/constants/geneEffectMeta";
import { getGeneEffectLabel } from "src/i18n/meta";
import type { Option } from "./types";

interface NewGeneProps {
    availableEffectTypes: Option[];
    onCreate: (gene: GeneCreate) => void;
    initialValue?: GeneCreate;
    submitLabel?: string;
}

export function NewGene({ availableEffectTypes, onCreate, initialValue, submitLabel }: NewGeneProps) {
    const { t } = useTranslation();

    const [selectedEffectType, setSelectedEffectType] = useState<string>(
        initialValue?.effect_type ?? availableEffectTypes[0]?.name ?? "",
    );

    const [threshold, setThreshold] = useState<string>(
        initialValue?.threshold !== undefined ? String(initialValue.threshold) : "",
    );

    const [weight, setWeight] = useState<string>(
        initialValue?.weight !== undefined ? String(initialValue.weight) : "",
    );

    const [defaultActive, setDefaultActive] = useState(initialValue?.default_active ?? false);

    const effectMeta = getGeneEffectMeta(selectedEffectType);

    const effectsWithoutThreshold = [
        "MAX_HP",
        "STRENGTH",
        "DEFENSE",
        "METABOLISM",
        "MUTATION_RATE",
    ];

    const shouldShowThreshold = !effectsWithoutThreshold.includes(selectedEffectType);

    const handleSubmit = () => {
        onCreate({
            effect_type: selectedEffectType,
            weight: weight === "" ? 1 : Number(weight),
            threshold: threshold === "" ? 0 : Number(threshold),
            position: { x: 100, y: 100 },
            default_active: defaultActive,
        });
    };

    return (
        <div>
            <div>
                <label htmlFor="effectTypeSelect">{t("effectType")}</label>
                <div className="select-container">
                    <select
                        id="effectTypeSelect"
                        value={selectedEffectType}
                        onChange={(e) => setSelectedEffectType(e.target.value)}
                    >
                        {availableEffectTypes.map((effectType) => (
                            <option key={effectType.id} value={effectType.name}>
                                {getGeneEffectLabel(effectType.name, t)}
                            </option>
                        ))}
                    </select>
                </div>
                <p className="form-hint">{t(effectMeta.descriptionKey)}</p>
            </div>

            {shouldShowThreshold && (
                <div>
                    <label htmlFor="threshold">{t("threshold")}</label>
                    <input
                        className="modal-input"
                        type="number"
                        id="threshold"
                        value={threshold}
                        onChange={(e) => setThreshold(e.target.value)}
                    />
                    <p className="form-hint">{t(effectMeta.thresholdKey)}</p>
                </div>
            )}

            <div>
                <label htmlFor="geneWeight">{t("gene_weight")}</label>
                <input
                    className="modal-input"
                    type="number"
                    id="geneWeight"
                    min={0}
                    step={0.1}
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                />
                <p className="form-hint">{t(effectMeta.weightKey)}</p>
            </div>

            <div>
                <div className="checkbox-container">
                    <input
                        className="modal-input_checkbox"
                        id="geneDefaultActive"
                        type="checkbox"
                        checked={defaultActive}
                        onChange={(e) => setDefaultActive(e.target.checked)}
                    />
                    <label className="light-label" htmlFor="geneDefaultActive">
                        {t("default_active")}
                    </label>
                </div>
                <p className="form-hint">{t("default_active_hint")}</p>
            </div>

            <button className="modal-button" onClick={handleSubmit}>{submitLabel ?? t("create")}</button>
        </div>
    );
}