// gene/details.tsx

import type { Gene } from "./types";
import { useTranslation } from "react-i18next";
import { getGeneEffectLabel } from "src/i18n/meta";

export function GeneDetails({ gene, onDelete }: { gene: Gene; onDelete?: () => void }) {
    const { t } = useTranslation();
    return <div>
        <p>{t('effectType')}: {getGeneEffectLabel(gene.effect_type, t)}</p>
        <p>{t('gene_weight')}: {gene.weight}</p>
        <p>{t('threshold')}: {gene.threshold}</p>
        {gene.default_active && <p>{t('default_active')}</p>}
        {onDelete && <button onClick={onDelete}>{t('delete')}</button>}
    </div>
};
