// new_agent.tsx

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import type { Option } from "./types";

interface NewAgentProps {
    availableGenomes: Option[];
    availableTerritories: Option[];
    onCreate: (sex: string, genome_id: number | null, territory_id: number) => void;
    initialValue?: {
        sex: string;
        genome_id: number | null;
        territory_id: number;
    };
    submitLabel?: string;
}

export function NewAgent({
    availableGenomes,
    availableTerritories,
    onCreate,
    initialValue,
    submitLabel,
}: NewAgentProps) {
    const { t } = useTranslation();
    const [sex, setSex] = useState(initialValue?.sex ?? "male");
    const [selectedGenome, setSelectedGenome] = useState<number>(
        initialValue?.genome_id ?? availableGenomes[0]?.id ?? 0,
    );
    const [selectedTerritory, setSelectedTerritory] = useState<number>(
        initialValue?.territory_id ?? availableTerritories[0]?.id ?? 0,
    );

    useEffect(() => {
        if (initialValue === undefined) {
            setSelectedGenome(availableGenomes[0]?.id || 0);
        }
    }, [availableGenomes, initialValue]);

    useEffect(() => {
        if (initialValue === undefined) {
            setSelectedTerritory(availableTerritories[0]?.id || 0);
        }
    }, [availableTerritories, initialValue]);

    const handleSubmit = () => {
        onCreate(sex, selectedGenome || null, selectedTerritory);
    };

    return (
        <div>
            <div>
                <label htmlFor="sex">{t('sex')}:</label>
                <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}>
                    <option value="male">{t('male')}</option>
                    <option value="female">{t('female')}</option>
                </select>
            </div>
            <div>
                <label htmlFor="genome">{t('genome')}:</label>
                <select id="genome" value={selectedGenome} onChange={(e) => setSelectedGenome(Number(e.target.value))}>
                    <option value={0}>{t('without_genome')}</option>
                    {availableGenomes.map(genome => (
                        <option key={genome.id} value={genome.id}>{genome.name}</option>
                    ))}
                </select>
            </div>
            <div>
                <label htmlFor="territory">{t('territory')}:</label>
                <select id="territory" value={selectedTerritory} onChange={(e) => setSelectedTerritory(Number(e.target.value))}>
                    {availableTerritories.map(territory => (
                        <option key={territory.id} value={territory.id}>{t('territory')} {territory.id}</option>
                    ))}
                </select>
            </div>
            <button onClick={handleSubmit} disabled={!selectedTerritory}>
                {submitLabel ?? t('create')}
            </button>
        </div>
    );
}
