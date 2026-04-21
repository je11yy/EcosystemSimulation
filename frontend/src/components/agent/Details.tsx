import type { Agent } from "./types";
import { useTranslation } from "react-i18next";
import { NewAgent } from "src/components/forms/Agent";
import type { Option } from "src/components/forms/types";
import { Link } from "react-router-dom";

export function AgentDetails({
    agent,
    availableGenomes = [],
    availableTerritories = [],
    isEditing = false,
    onEdit,
    onCancelEdit,
    onUpdate,
    onDelete,
}: {
    agent: Agent;
    availableGenomes?: Option[];
    availableTerritories?: Option[];
    isEditing?: boolean;
    onEdit?: () => void;
    onCancelEdit?: () => void;
    onUpdate?: (sex: string, genome_id: number | null, territory_id: number) => void;
    onDelete?: (id: number) => void;
}) {
    const { t } = useTranslation();
    if (isEditing) {
        return (
            <div>
                <NewAgent
                    availableGenomes={availableGenomes}
                    availableTerritories={availableTerritories}
                    initialValue={{
                        sex: agent.sex,
                        genome_id: agent.genome_id,
                        territory_id: agent.territory_id,
                    }}
                    submitLabel={t("save")}
                    onCreate={(sex, genome_id, territory_id) =>
                        onUpdate?.(sex, genome_id, territory_id)
                    }
                />
                <button type="button" onClick={onCancelEdit}>{t("cancel")}</button>
            </div>
        );
    }

    return <div>
        <h3>{t('id')}: {agent.id}</h3>
        <p>{t('hunger')}: {agent.hunger}</p>
        <p>{t('health')}: {agent.hp}</p>
        <p>{t('strength')}: {agent.strength}</p>
        <p>{t('defense')}: {agent.defense}</p>
        <p>{t('temp_preference')}: {agent.temp_pref}</p>
        <p>{t('satisfaction')}: {agent.satisfaction.toFixed(2)} / 5</p>
        {agent.pregnant && <p>{t('pregnant')}</p> && <p>{t('ticks_to_birth')}: {agent.ticks_to_birth}</p>}
        <div className="agent-actions">
            {agent.genome_id !== null && (
                <Link className="button-link" to={`/genomes/${agent.genome_id}`}>
                    {t("open_agent_genome")}
                </Link>
            )}
            <button type="button" onClick={onEdit}>{t('edit')}</button>
            <button onClick={() => onDelete?.(agent.id)}>{t('delete_agent')}</button>
        </div>
    </div>
}
