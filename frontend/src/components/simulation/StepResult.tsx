import { useTranslation } from "react-i18next";
import type { Log } from "src/api/types";

type Props = {
    selectedLog: Log | null;
};

export function StepResult({ selectedLog }: Props) {
    const { t } = useTranslation();

    return (
        <section>
            {!selectedLog ? (
                <p className="form-hint">{t("no_results_yet")}</p>
            ) : (
                <div>
                    <section className="simulation-step-result__panel">
                        <h2>{t("agent_actions_panel")}</h2>
                        <div className="simulation-step-result__grid">
                            <Metric label={t("eat")} value={selectedLog.step_result.eat} />
                            <Metric label={t("move")} value={selectedLog.step_result.move} />
                            <Metric label={t("mate")} value={selectedLog.step_result.mate} />
                            <Metric label={t("rest")} value={selectedLog.step_result.rest} />
                            <Metric label={t("hunt")} value={selectedLog.step_result.hunt} />
                        </div>
                    </section>
                    <section className="simulation-step-result__panel">
                        <h2>{t("tick_outcomes_panel")}</h2>
                        <div className="simulation-step-result__grid">
                            <Metric label={t("births")} value={selectedLog.step_result.births} />
                            <Metric label={t("deaths")} value={selectedLog.step_result.deaths} />
                            <Metric label={t("fights")} value={selectedLog.step_result.fights} />
                        </div>
                    </section>
                </div>
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
