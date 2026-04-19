import { useState } from "react";
import { useTranslation } from "react-i18next";
import { getSimulationLogs } from "src/api/simulations";
import type { AgentDecision, Log } from "src/api/types";

type Props = {
    simulationId: number;
    logs: Log[];
    logsCount: number;
};

export function SimulationLogsModal({ simulationId, logs, logsCount }: Props) {
    const { t } = useTranslation();
    const [isDownloading, setIsDownloading] = useState(false);
    const hasMoreLogs = logsCount > logs.length;

    const downloadLogs = async () => {
        setIsDownloading(true);
        try {
            const allLogs = await getSimulationLogs(simulationId);
            const blob = new Blob([JSON.stringify(allLogs, null, 2)], {
                type: "application/json",
            });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `simulation-${simulationId}-logs.json`;
            link.click();
            URL.revokeObjectURL(url);
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <div className="logs-modal">
            <div className="logs-modal__toolbar">
                <p className="form-hint">
                    {t("showing_last_logs", { count: logs.length, total: logsCount })}
                </p>
                {hasMoreLogs && (
                    <button type="button" onClick={downloadLogs} disabled={isDownloading}>
                        {isDownloading ? t("loading") : t("download")}
                    </button>
                )}
            </div>

            {logs.length === 0 ? (
                <p className="form-hint">{t("no_step_result")}</p>
            ) : (
                <div className="logs-modal__list">
                    {logs.map((log) => (
                        <article className="tick-log" key={log.id}>
                            <header>
                                <h3>{t("tick")} {log.tick}</h3>
                                <span>{new Date(log.created_at).toLocaleString()}</span>
                            </header>

                            <section>
                                <h4>{t("agent_actions")}</h4>
                                {log.agent_decisions.length === 0 ? (
                                    <p className="form-hint">{t("no_decisions")}</p>
                                ) : (
                                    <ul>
                                        {log.agent_decisions.map((decision) => (
                                            <li key={`${log.id}-decision-${decision.agent_id}`}>
                                                {formatDecision(decision, t)}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </section>

                            <EventSection
                                title={t("action_results")}
                                events={log.events?.applied_results ?? []}
                                emptyText={t("no_action_results")}
                            />
                            <EventSection
                                title={t("deaths")}
                                events={log.events?.deaths ?? []}
                                emptyText={t("no_deaths")}
                            />
                            <EventSection
                                title={t("births")}
                                events={log.events?.births ?? []}
                                emptyText={t("no_births")}
                            />
                            <EventSection
                                title={t("fights")}
                                events={log.events?.fights ?? []}
                                emptyText={t("no_fights")}
                            />
                            <EventSection
                                title={t("hunts")}
                                events={log.events?.hunts ?? []}
                                emptyText={t("no_hunts")}
                            />
                        </article>
                    ))}
                </div>
            )}
        </div>
    );
}

function EventSection({
    title,
    events,
    emptyText,
}: {
    title: string;
    events: Array<Record<string, unknown>>;
    emptyText: string;
}) {
    return (
        <section>
            <h4>{title}</h4>
            {events.length === 0 ? (
                <p className="form-hint">{emptyText}</p>
            ) : (
                <ul>
                    {events.map((event, index) => (
                        <li key={`${title}-${index}`}>
                            {formatEvent(event)}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}

function formatDecision(decision: AgentDecision, t: (key: string) => string): string {
    const parts = [`#${decision.agent_id}: ${t(decision.action)}`];
    if (decision.to_territory !== null && decision.to_territory !== undefined) {
        parts.push(`${t("to_territory")}: ${decision.to_territory}`);
    }
    if (decision.partner_id !== null && decision.partner_id !== undefined) {
        parts.push(`${t("partner")}: ${decision.partner_id}`);
    }
    if (decision.target_id !== null && decision.target_id !== undefined) {
        parts.push(`${t("target")}: ${decision.target_id}`);
    }
    return parts.join(", ");
}

function formatEvent(event: Record<string, unknown>): string {
    return Object.entries(event)
        .filter(([, value]) => value !== "" && value !== null && value !== undefined)
        .map(([key, value]) => `${key}: ${String(value)}`)
        .join(", ");
}
