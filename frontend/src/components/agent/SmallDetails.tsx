import type { Agent } from "./types";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { AgentDetails } from "./Details";

function getSatisfactionColor(satisfaction: number): string {
    if (satisfaction > 75) {
        return "green";
    } else if (satisfaction > 50) {
        return "yellow";
    } else if (satisfaction > 25) {
        return "orange";
    } else {
        return "red";
    }
};

export function AgentSmallDetails({ agent, onDelete }: { agent: Agent; onDelete?: (id: number) => void }) {
    const { t } = useTranslation();
    const [expanded, setExpanded] = useState(false);
    const borderColor = getSatisfactionColor(agent.satisfaction);
    return (
        <div onClick={() => setExpanded(!expanded)} style={expanded ? {} : { border: `2px solid ${borderColor}`, padding: "5px", margin: "5px", cursor: "pointer" }}>
            {expanded ? (
                <AgentDetails agent={agent} onDelete={onDelete} />
            ) : (
                <h4>{t('id')}: {agent.id}</h4>
            )}
        </div>
    );
};