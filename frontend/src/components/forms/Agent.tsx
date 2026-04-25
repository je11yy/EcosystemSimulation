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

    const [sex, setSex] = useState<string>(initialValue?.sex ?? "");
    const [selectedGenome, setSelectedGenome] = useState<string>(
        initialValue?.genome_id !== undefined && initialValue.genome_id !== null
            ? String(initialValue.genome_id)
            : "",
    );
    const [selectedTerritory, setSelectedTerritory] = useState<string>(
        initialValue?.territory_id !== undefined ? String(initialValue.territory_id) : "",
    );

    useEffect(() => {
        if (initialValue === undefined) {
            setSelectedGenome("");
        }
    }, [availableGenomes, initialValue]);

    useEffect(() => {
        if (initialValue === undefined) {
            setSelectedTerritory("");
        }
    }, [availableTerritories, initialValue]);

    const handleSubmit = () => {
        onCreate(
            sex || "male",
            selectedGenome === "" ? null : Number(selectedGenome),
            Number(selectedTerritory),
        );
    };

    return (
        <div>
            <div>
                <label htmlFor="sex">{t("sex")}</label>
                <div className="select-container">
                    <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}>
                        <option value="" disabled>
                            {t("sex")}
                        </option>
                        <option value="male">{t("male")}</option>
                        <option value="female">{t("female")}</option>
                    </select>
                </div>
            </div>

            <div>
                <label htmlFor="genome">{t("genome")}</label>
                <div className="select-container">
                    <select
                        id="genome"
                        value={selectedGenome}
                        onChange={(e) => setSelectedGenome(e.target.value)}
                    >
                        <option value="">{t("without_genome")}</option>
                        {availableGenomes.map((genome) => (
                            <option key={genome.id} value={String(genome.id)}>
                                {genome.name}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div>
                <label htmlFor="territory">{t("territory")}</label>
                <div className="select-container">
                    <select
                        id="territory"
                        value={selectedTerritory}
                        onChange={(e) => setSelectedTerritory(e.target.value)}
                    >
                        <option value="" disabled>
                            {t("territory")}
                        </option>
                        {availableTerritories.map((territory) => (
                            <option key={territory.id} value={String(territory.id)}>
                                {t("territory")} {territory.id}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <button className="modal-button" onClick={handleSubmit} disabled={!selectedTerritory}>
                {submitLabel ?? t("create")}
            </button>
        </div>
    );
}