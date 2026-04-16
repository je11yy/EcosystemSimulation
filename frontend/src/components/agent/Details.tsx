import type { Agent } from "./types";
import { useTranslation } from "react-i18next";

export function AgentDetails({ agent, onDelete }: { agent: Agent; onDelete?: (id: number) => void }) {
    const { t } = useTranslation();
    return <div>
        <h3>{t('id')}: {agent.id}</h3>
        <p>{t('hunger')}: {agent.hunger}</p>
        <p>{t('health')}: {agent.hp}</p>
        <p>{t('strength')}: {agent.strength}</p>
        <p>{t('defense')}: {agent.defense}</p>
        <p>{t('temp_preference')}: {agent.temp_pref}</p>
        <p>{t('satisfaction')}: {agent.satisfaction}</p>
        {agent.pregnant && <p>{t('pregnant')}</p> && <p>{t('ticks_to_birth')}: {agent.ticks_to_birth}</p>}
        <button onClick={() => onDelete?.(agent.id)}>{t('delete_agent')}</button>
    </div>
}