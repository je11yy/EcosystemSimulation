// gene/details.tsx

import type { Gene } from "./types";
import { useTranslation } from "react-i18next";

export function GeneDetails({ gene, onDelete }: { gene: Gene; onDelete?: () => void }) {
    const { t } = useTranslation();
    return <div>
        <h3>{t('id')}: {gene.id}</h3>
        <p>{t('effectType')}: {gene.effect_type}</p>
        <p>{t('gene_weight')}: {gene.weight}</p>
        <p>{t('threshold')}: {gene.threshold}</p>
        {gene.default_active && <p>{t('default_active')}</p>}
        {onDelete && <button onClick={onDelete}>{t('delete')}</button>}
    </div>
};
