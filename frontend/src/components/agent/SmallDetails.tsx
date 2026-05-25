import type { Agent } from "./types";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { AgentDetails } from "./Details";
import type { Option } from "src/components/forms/types";
function getSatisfactionColor(satisfaction: number): string {
    const normalized = Math.max(0, Math.min(1, satisfaction / 5));

    if (normalized < 0.5) {
        const green = Math.round(80 + (normalized / 0.5) * 100);
        const red = Math.round(180 + (normalized / 0.5) * 40);
        return `rgb(${red}, ${green}, 80)`;
    }

    const red = Math.round(80 + ((1 - normalized) / 0.5) * 100);
    const green = Math.round(180 + ((1 - normalized) / 0.5) * 40);
    return `rgb(${red}, ${green}, 80)`;
}

export function AgentSmallDetails({
    agent,
    availableGenomes = [],
    availableTerritories = [],
    onDelete,
    onUpdate,
}: {
    agent: Agent;
    availableGenomes?: Option[];
    availableTerritories?: Option[];
    onDelete?: (id: number) => void;
    onUpdate?: (agentId: number, sex: string, genome_id: number | null, territory_id: number) => void;
}) {
    const { t } = useTranslation();
    const [expanded, setExpanded] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const borderColor = getSatisfactionColor(agent.satisfaction);
    const backgroundColor = borderColor.replace('rgb(', 'rgba(').replace(')', ', 0.1)');
    return (
        <div className="agent-accordion" style={{ borderColor }}>
            <button
                className="agent-accordion-header"
                type="button"
                aria-expanded={expanded}
                onClick={() => {
                    setExpanded(!expanded);
                    if (expanded) {
                        setIsEditing(false);
                    }
                }}
                style={{ color: borderColor, backgroundColor }}
            >
                <span>{t('id')}: {agent.id}</span>
                <span className={`accordion-arrow${expanded ? " expanded" : ""}`} style={{ borderColor }} aria-hidden="true" />
            </button>
            {expanded && (
                <div className="agent-accordion-body">
                    <AgentDetails
                        agent={agent}
                        availableGenomes={availableGenomes}
                        availableTerritories={availableTerritories}
                        isEditing={isEditing}
                        onEdit={() => setIsEditing(true)}
                        onCancelEdit={() => setIsEditing(false)}
                        onDelete={onDelete}
                        onUpdate={(sex, genome_id, territory_id) => {
                            onUpdate?.(agent.id, sex, genome_id, territory_id);
                            setIsEditing(false);
                        }}
                    />
                </div>
            )}
        </div>
    );
};
