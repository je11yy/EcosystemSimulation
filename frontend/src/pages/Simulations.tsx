// список симуляций
// при клике на симуляцию открывается страница с симуляцией

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getScenarioPresets, getSimulations } from "src/api/simulations";
import { useTranslation } from "react-i18next";
import { useSimulationsListMutations } from "src/hooks/simulations/useSimulationMutations";
import { getScenarioLabel } from "src/i18n/meta";

export function SimulationsPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [name, setName] = useState("");
    const [expanded, setExpanded] = useState(false);

    const simulationsQuery = useQuery({
        queryKey: ["simulations"],
        queryFn: getSimulations,
    });

    const scenariosQuery = useQuery({
        queryKey: ["simulation-scenarios"],
        queryFn: getScenarioPresets,
    });

    const { createMutation, createFromScenarioMutation } = useSimulationsListMutations();

    return (
        <div>
            <div className="create-form">
                <input className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder={t("simulation_name")} />
                <button className="form-input-button" onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
            </div>
            <section className="scenario-presets shortened">
                <div className="scenario-presets__container">
                    <div className="scenario-presets__header">
                        <h3>{t("scenario_presets")}</h3>
                        <p className="form-hint">{t("scenario_presets_hint")}</p>
                    </div>
                    <button
                        className="accordion-button"
                        type="button"
                        onClick={() => {
                            setExpanded(!expanded);
                            const presets = document.querySelector(".scenario-presets");
                            if (presets) {
                                presets.classList.toggle("shortened");
                            }
                        }}
                    >
                        <div className="accordion-arrow" aria-hidden="true"></div>
                    </button>
                </div>
                {scenariosQuery.isLoading && <p>{t("loading")}...</p>}
                {scenariosQuery.data && (
                    <div className="scenario-presets__grid">
                        {scenariosQuery.data.map((scenario) => (
                            <ScenarioCard
                                key={scenario.key}
                                scenario={scenario}
                                isPending={createFromScenarioMutation.isPending}
                                onCreate={() => {
                                    createFromScenarioMutation.mutate(scenario.key, {
                                        onSuccess: (response) => {
                                            navigate(`/simulations/${response.simulation_id}`);
                                        },
                                    });
                                }}
                            />
                        ))}
                    </div>
                )}
            </section>
            {simulationsQuery.isLoading && <p>{t("loading")}...</p>}
            {simulationsQuery.isError && <p>{t("error_loading_simulations")}</p>}
            {simulationsQuery.data && (
                <ul>
                    {simulationsQuery.data.map(simulation => (
                        <li key={simulation.id}>
                            <Link to={`/simulations/${simulation.id}`}>
                                {simulation.name}
                            </Link>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
};

function ScenarioCard({
    scenario,
    isPending,
    onCreate,
}: {
    scenario: Awaited<ReturnType<typeof getScenarioPresets>>[number];
    isPending: boolean;
    onCreate: () => void;
}) {
    const { t } = useTranslation();
    const label = getScenarioLabel(scenario, t);

    return (
        <article className="scenario-card">
            <h3>{label.name}</h3>
            <p>{label.description}</p>
            <button type="button" disabled={isPending} onClick={onCreate}>
                {t("create_from_scenario")}
            </button>
        </article>
    );
}
