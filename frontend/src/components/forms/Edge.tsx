import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { Option } from "./types";

interface NewEdgeProps {
    sourceOptions: Option[];
    targetOptions?: Option[];
    onCreate: (source: number, target: number, weight: number) => void;
}

export function NewEdge({ sourceOptions, targetOptions = sourceOptions, onCreate }: NewEdgeProps) {
    const { t } = useTranslation();
    const [source, setSource] = useState(sourceOptions[0]?.id ?? 0);
    const [target, setTarget] = useState(targetOptions[1]?.id ?? targetOptions[0]?.id ?? 0);
    const [weight, setWeight] = useState(1);

    const canCreate = source > 0 && target > 0 && source !== target;

    return (
        <div>
            <div>
                <label htmlFor="edgeSource">{t("source")}:</label>
                <select id="edgeSource" value={source} onChange={(e) => setSource(Number(e.target.value))}>
                    {sourceOptions.map(option => (
                        <option key={option.id} value={option.id}>{option.name}</option>
                    ))}
                </select>
            </div>
            <div>
                <label htmlFor="edgeTarget">{t("target")}:</label>
                <select id="edgeTarget" value={target} onChange={(e) => setTarget(Number(e.target.value))}>
                    {targetOptions.map(option => (
                        <option key={option.id} value={option.id}>{option.name}</option>
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
                    onChange={(e) => setWeight(Number(e.target.value))}
                />
            </div>
            <button onClick={() => onCreate(source, target, weight)} disabled={!canCreate}>
                {t("create")}
            </button>
        </div>
    );
}

interface NewEdgeWeightProps {
    sourceName: string;
    targetName: string;
    onCreate: (weight: number) => void;
}

export function NewEdgeWeight({ sourceName, targetName, onCreate }: NewEdgeWeightProps) {
    const { t } = useTranslation();
    const [weight, setWeight] = useState(1);

    return (
        <div>
            <p>
                {sourceName} -&gt; {targetName}
            </p>
            <div>
                <label htmlFor="edgeWeight">{t("weight")}:</label>
                <input
                    type="number"
                    id="edgeWeight"
                    min={0}
                    value={weight}
                    onChange={(e) => setWeight(Number(e.target.value))}
                />
            </div>
            <button onClick={() => onCreate(weight)}>
                {t("create")}
            </button>
        </div>
    );
}
