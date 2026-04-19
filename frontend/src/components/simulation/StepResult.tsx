import { useTranslation } from "react-i18next";
import type { Log } from "src/api/types";

type Props = {
    status?: string;
    tick?: number;
    lastLog: Log | null;
};

export function StepResult({ status, tick, lastLog }: Props) {
    const { t } = useTranslation();

    return (
        <section className="simulation-step-result">
            <div className="simulation-step-result__header">
                <div>
                    <h2>{t("latest_step")}</h2>
                    <p>
                        {t("simulation_status")}: {status ?? "-"} · {t("tick")}: {tick ?? 0}
                    </p>
                </div>
                {lastLog && (
                    <span className="simulation-step-result__tick">
                        {t("tick")} {lastLog.tick}
                    </span>
                )}
            </div>

            {!lastLog ? (
                <p className="form-hint">{t("no_step_result")}</p>
            ) : (
                <>
                    <div className="simulation-step-result__grid">
                        <Metric label={t("eat")} value={lastLog.step_result.eat} />
                        <Metric label={t("move")} value={lastLog.step_result.move} />
                        <Metric label={t("mate")} value={lastLog.step_result.mate} />
                        <Metric label={t("rest")} value={lastLog.step_result.rest} />
                        <Metric label={t("hunt")} value={lastLog.step_result.hunt} />
                        <Metric label={t("births")} value={lastLog.step_result.births} />
                        <Metric label={t("deaths")} value={lastLog.step_result.deaths} />
                        <Metric label={t("fights")} value={lastLog.step_result.fights} />
                    </div>

                    <h3>{t("metrics")}</h3>
                    <div className="simulation-step-result__grid">
                        <Metric
                            label={t("alive_population")}
                            value={lastLog.metrics.alive_population}
                        />
                        <Metric
                            label={t("avg_hunger")}
                            value={lastLog.metrics.avg_hunger.toFixed(2)}
                        />
                        <Metric
                            label={t("avg_satisfaction")}
                            value={(lastLog.metrics.avg_satisfaction ?? 0).toFixed(2)}
                        />
                        <Metric label={t("consumed_food")} value={lastLog.metrics.consumed_food} />
                        <Metric
                            label={t("successful_hunts")}
                            value={lastLog.metrics.successful_hunts}
                        />
                        <Metric
                            label={t("unsuccessful_hunts")}
                            value={lastLog.metrics.unsuccessful_hunts}
                        />
                    </div>

                    <h3>{t("decisions")}</h3>
                    {lastLog.agent_decisions.length === 0 ? (
                        <p className="form-hint">{t("no_decisions")}</p>
                    ) : (
                        <ul className="simulation-step-result__decisions">
                            {lastLog.agent_decisions.slice(0, 8).map((decision) => (
                                <li key={`${lastLog.id}-${decision.agent_id}`}>
                                    #{decision.agent_id}: {t(decision.action)}
                                </li>
                            ))}
                        </ul>
                    )}
                </>
            )}
        </section>
    );
}

function Metric({ label, value }: { label: string; value: string | number }) {
    return (
        <div className="simulation-step-result__metric">
            <span>{label}</span>
            <strong>{value}</strong>
        </div>
    );
}
