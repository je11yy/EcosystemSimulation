// new_agent.tsx

import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { Option } from "./types";

interface NewAgentProps {
    availableGenomes: Option[];
    availableTerritories: Option[];
    onCreate: (sex: string, genome_id: number, territory_id: number) => void;
}

export function NewAgent({ availableGenomes, availableTerritories, onCreate }: NewAgentProps) {
    const { t } = useTranslation();
    const [sex, setSex] = useState("male");
    const [selectedGenome, setSelectedGenome] = useState<number>(availableGenomes[0]?.id || 0);
    const [selectedTerritory, setSelectedTerritory] = useState<number>(availableTerritories[0]?.id || 0);

    const handleSubmit = () => {
        onCreate(sex, selectedGenome, selectedTerritory);
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
                <label>{t('genome')}:</label>
                {availableGenomes.map(genome => (
                    <div key={genome.id}>
                        <input
                            type="radio"
                            id={`genome-${genome.id}`}
                            name="genome"
                            checked={selectedGenome === genome.id}
                            onChange={() => setSelectedGenome(genome.id)}
                        />
                        <label htmlFor={`genome-${genome.id}`}>{genome.name}</label>
                    </div>
                ))}
            </div>
            <div>
                <label htmlFor="territory">{t('territory')}:</label>
                <select id="territory" value={selectedTerritory} onChange={(e) => setSelectedTerritory(Number(e.target.value))}>
                    {availableTerritories.map(territory => (
                        <option key={territory.id} value={territory.id}>{t('territory')} {territory.id}</option>
                    ))}
                </select>
            </div>
            <button onClick={handleSubmit}>{t('create')}</button>
        </div>
    );
}
