import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { GeneCreate } from "src/api/types";
import { getGeneEffectMeta } from "src/constants/geneEffectMeta";
import type { Option } from "./types";

interface NewGeneProps {
    availableEffectTypes: Option[];
    onCreate: (gene: GeneCreate) => void;
    initialValue?: GeneCreate;
    submitLabel?: string;
}

export function NewGene({ availableEffectTypes, onCreate, initialValue, submitLabel }: NewGeneProps) {
    const { t } = useTranslation();
    const [name, setName] = useState(initialValue?.name ?? "");
    const [selectedEffectType, setSelectedEffectType] = useState<string>(
        initialValue?.effect_type ?? availableEffectTypes[0]?.name ?? "",
    );
    const [threshold, setThreshold] = useState<number>(initialValue?.threshold ?? 0);
    const [weight, setWeight] = useState<number>(initialValue?.weight ?? 1);
    const [x, setX] = useState<number>(initialValue?.position.x ?? 100);
    const [y, setY] = useState<number>(initialValue?.position.y ?? 100);
    const [defaultActive, setDefaultActive] = useState(initialValue?.default_active ?? true);
    const effectMeta = getGeneEffectMeta(selectedEffectType);

    const handleSubmit = () => {
        onCreate({
            name: name || selectedEffectType,
            effect_type: selectedEffectType,
            weight,
            threshold,
            position: { x, y },
            default_active: defaultActive,
        });
    };

    return (
        <div>
            <div>
                <label htmlFor="geneName">{t('gene_name')}:</label>
                <input
                    id="geneName"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={selectedEffectType}
                />
            </div>
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
                <p className="form-hint">{t(effectMeta.descriptionKey)}</p>
            </div>
            <div>
                <label htmlFor="threshold">{t('threshold')}:</label>
                <input
                    type="number"
                    id="threshold"
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                />
                <p className="form-hint">{t(effectMeta.thresholdKey)}</p>
            </div>
            <div>
                <label htmlFor="geneWeight">{t('gene_weight')}:</label>
                <input
                    type="number"
                    id="geneWeight"
                    min={0}
                    step={0.1}
                    value={weight}
                    onChange={(e) => setWeight(Number(e.target.value))}
                />
                <p className="form-hint">{t(effectMeta.weightKey)}</p>
            </div>
            <div>
                <label htmlFor="geneX">X:</label>
                <input type="number" id="geneX" value={x} onChange={(e) => setX(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="geneY">Y:</label>
                <input type="number" id="geneY" value={y} onChange={(e) => setY(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="geneDefaultActive">{t('default_active')}:</label>
                <input
                    id="geneDefaultActive"
                    type="checkbox"
                    checked={defaultActive}
                    onChange={(e) => setDefaultActive(e.target.checked)}
                />
                <p className="form-hint">{t('default_active_hint')}</p>
            </div>
            <button onClick={handleSubmit}>{submitLabel ?? t('create')}</button>
        </div>
    );
};
