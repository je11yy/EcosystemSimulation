// список симуляций
// при клике на симуляцию открывается страница с симуляцией

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getScenarioPresets, getSimulations } from "src/api/simulations";
import { useTranslation } from "react-i18next";
import { useSimulationsListMutations } from "src/hooks/simulations/useSimulationMutations";

export function SimulationsPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [name, setName] = useState("");

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
            <h1>{t("simulations")}</h1>
            <input className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder={t("simulation_name")} />
            <button className="form-input-button" onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
            <section className="scenario-presets">
                <h2>{t("scenario_presets")}</h2>
                <p className="form-hint">{t("scenario_presets_hint")}</p>
                {scenariosQuery.isLoading && <p>{t("loading")}...</p>}
                {scenariosQuery.data && (
                    <div className="scenario-presets__grid">
                        {scenariosQuery.data.map((scenario) => (
                            <article className="scenario-card" key={scenario.key}>
                                <h3>{scenario.name}</h3>
                                <p>{scenario.description}</p>
                                <button
                                    type="button"
                                    disabled={createFromScenarioMutation.isPending}
                                    onClick={() => {
                                        createFromScenarioMutation.mutate(scenario.key, {
                                            onSuccess: (response) => {
                                                navigate(`/simulations/${response.simulation_id}`);
                                            },
                                        });
                                    }}
                                >
                                    {t("create_from_scenario")}
                                </button>
                            </article>
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
