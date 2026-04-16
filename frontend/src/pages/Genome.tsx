import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { Gene } from "../components/gene/types";
import { NewGene } from "../components/forms/Gene";
import { Modal } from "../components/Modal"

interface GenomeProps {
    genes?: Gene[];
    availableEffectTypes?: { id: number; name: string }[];
    onAddGene?: (effectType: string, threshold: number) => void;
}

export function GenomePage({ genes = [], availableEffectTypes = [], onAddGene }: GenomeProps) {
    const { t } = useTranslation();
    const [showNewGeneForm, setShowNewGeneForm] = useState(false);

    return (
        <div>
            <h2>{t('genome')}</h2>
            <button onClick={() => setShowNewGeneForm(true)}>{t('add_gene')}</button>
            {showNewGeneForm && (
                <Modal title={t('add_gene')} onClose={() => setShowNewGeneForm(false)}>
                    <NewGene availableEffectTypes={availableEffectTypes} onCreate={(effectType, threshold) => {
                        onAddGene?.(effectType, threshold);
                        setShowNewGeneForm(false);
                    }} />
                </Modal>
            )}
            <div>
                {genes.map(gene => (
                    <div key={gene.id}>
                        <p>{t('id')}: {gene.id}</p>
                        <p>{t('effectType')}: {gene.effect_type}</p>
                        <p>{t('threshold')}: {gene.threshold}</p>
                        {gene.is_active && <p>{t('active')}</p>}
                    </div>
                ))}
            </div>
        </div>
    );
};
