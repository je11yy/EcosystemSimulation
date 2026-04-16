import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { Option } from "./types";

interface NewGeneProps {
    availableEffectTypes: Option[];
    onCreate: (effectType: string, threshold: number) => void;
}

export function NewGene({ availableEffectTypes, onCreate }: NewGeneProps) {
    const { t } = useTranslation();
    const [selectedEffectType, setSelectedEffectType] = useState<string>(availableEffectTypes[0]?.name || "");
    const [threshold, setThreshold] = useState<number>(0);

    const handleSubmit = () => {
        onCreate(selectedEffectType, threshold);
    };

    return (
        <div>
            <div>
                <label>{t('effectType')}:</label>
                {availableEffectTypes.map(effectType => (
                    <div key={effectType.id}>
                        <input
                            type="radio"
                            id={`effectType-${effectType.id}`}
                            name="effectType"
                            checked={selectedEffectType === effectType.name}
                            onChange={() => setSelectedEffectType(effectType.name)}
                        />
                        <label htmlFor={`effectType-${effectType.id}`}>{effectType.name}</label>
                    </div>
                ))}
            </div>
            <div>
                <label htmlFor="threshold">{t('threshold')}:</label>
                <input
                    type="number"
                    id="threshold"
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                />
            </div>
            <button onClick={handleSubmit}>{t('create')}</button>
        </div>
    );
};