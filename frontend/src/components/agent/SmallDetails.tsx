import type { Agent } from "./types";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { AgentDetails } from "./Details";
import type { Option } from "src/components/forms/types";

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
            >
                <span>{t('id')}: {agent.id}</span>
                <span className="accordion-arrow" aria-hidden="true">
                    {expanded ? "▲" : "▼"}
                </span>
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
