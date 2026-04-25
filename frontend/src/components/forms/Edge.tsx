import { useState } from "react";
import { useTranslation } from "react-i18next";
import { getGeneEffectLabel } from "src/i18n/meta";
import type { Option } from "./types";

interface NewEdgeProps {
    sourceOptions: Option[];
    targetOptions?: Option[];
    onCreate: (source: number, target: number, weight: number) => void;
}

export function NewEdge({ sourceOptions, targetOptions = sourceOptions, onCreate }: NewEdgeProps) {
    const { t } = useTranslation();

    const [source, setSource] = useState<string>("");
    const [target, setTarget] = useState<string>("");
    const [weight, setWeight] = useState<string>("");

    const canCreate = source !== "" && target !== "" && source !== target;

    const handleSubmit = () => {
        onCreate(
            Number(source),
            Number(target),
            weight === "" ? 1 : Number(weight),
        );
    };

    return (
        <div>
            <div>
                <label htmlFor="edgeSource">{t("source")}:</label>
                <select
                    id="edgeSource"
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                >
                    <option value="" disabled>
                        {t("source")}
                    </option>
                    {sourceOptions.map((option) => (
                        <option key={option.id} value={String(option.id)}>
                            {getGeneEffectLabel(option.name, t)}
                        </option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="edgeTarget">{t("target")}:</label>
                <select
                    id="edgeTarget"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                >
                    <option value="" disabled>
                        {t("target")}
                    </option>
                    {targetOptions.map((option) => (
                        <option key={option.id} value={String(option.id)}>
                            {getGeneEffectLabel(option.name, t)}
                        </option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="edgeWeight">{t("weight")}:</label>
                <input
                    type="number"
                    id="edgeWeight"
                    min={0}
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                />
            </div>

            <button onClick={handleSubmit} disabled={!canCreate}>
                {t("create")}
            </button>
        </div>
    );
}

interface NewEdgeWeightProps {
    onCreate: (weight: number) => void;
}

export function NewEdgeWeight({ onCreate }: NewEdgeWeightProps) {
    const { t } = useTranslation();
    const [weight, setWeight] = useState<string>("");

    const handleSubmit = () => {
        onCreate(weight === "" ? 1 : Number(weight));
    };

    return (
        <div>
            <div>
                <label htmlFor="edgeWeight">{t("weight")}</label>
                <input
                    className="modal-input"
                    type="number"
                    id="edgeWeight"
                    min={0}
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                />
            </div>

            <button className="modal-button" onClick={handleSubmit}>
                {t("create")}
            </button>
        </div>
    );
}