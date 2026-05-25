import { useState } from "react";
import { useTranslation } from "react-i18next";
import { getScenarioPresets } from "src/api/simulations";
import { useQuery } from "@tanstack/react-query";
import { useSimulationsListMutations } from "src/hooks/simulations/useSimulationMutations";
import { useNavigate } from "react-router-dom";
import { getScenarioLabel } from "src/i18n/meta";

export function NewSimulation() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const [name, setName] = useState("");

    const scenariosQuery = useQuery({
        queryKey: ["simulation-scenarios"],
        queryFn: getScenarioPresets,
    });

    const { createMutation, createFromScenarioMutation } = useSimulationsListMutations();

    return (
        <div className="simulation-modal">
            <div className="scratch">
                <span>
                    {t("create_from_scratch")}:
                </span>
                <div className="create-form">
                    <input className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder={t("simulation_name")} />
                    <button className="form-input-button" onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
                </div>
            </div>
            <div className="scenario">
                <span>
                    {t("create_from_scenario")}:
                </span>
                <section className="scenario-presets">
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
            </div>
        </div>
    );
}

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
        <div className="scenario-card">
            <div className="label-button">
                <div className="label-icon">
                    <h3>{label.name}</h3>
                    <svg className="question-icon" xmlns="http://www.w3.org/2000/svg" version="1.0" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet">
                        <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="currentColor" stroke="none">
                            <title>{label.description}</title>
                            <path d="M2370 5113 c-468 -44 -862 -180 -1220 -419 -384 -256 -682 -596 -886 -1009 -126 -258 -203 -511 -246 -810 -17 -118 -17 -512 0 -630 42 -295 120 -553 242 -800 137 -280 272 -468 494 -691 221 -220 412 -357 681 -489 188 -92 309 -137 500 -185 500 -126 1002 -102 1490 71 149 53 407 182 540 271 299 199 573 480 769 788 72 113 188 353 235 486 235 662 194 1372 -115 1993 -124 250 -263 447 -458 648 -216 224 -428 378 -711 518 -296 146 -572 225 -900 255 -102 9 -333 11 -415 3z m427 -878 c402 -102 691 -451 720 -870 16 -234 -105 -509 -319 -724 -82 -83 -155 -139 -263 -198 -134 -74 -164 -126 -165 -283 0 -85 -20 -139 -66 -182 -106 -99 -268 -67 -336 66 -18 35 -20 54 -16 180 4 120 8 152 30 214 56 157 167 281 327 367 156 83 287 223 352 375 19 44 24 73 24 145 0 107 -21 181 -75 264 -216 329 -678 333 -896 6 -47 -70 -75 -154 -84 -257 -10 -102 -29 -147 -82 -193 -106 -90 -261 -57 -323 70 -26 53 -28 62 -22 150 31 461 376 830 839 895 94 13 247 2 355 -25z m-123 -2775 c20 -14 49 -43 64 -64 24 -35 27 -49 27 -116 0 -67 -3 -81 -27 -116 -15 -21 -44 -50 -65 -64 -31 -21 -48 -25 -113 -25 -65 0 -82 4 -113 25 -21 14 -50 43 -65 64 -24 35 -27 49 -27 117 0 70 3 81 30 120 45 64 104 91 186 87 50 -3 75 -10 103 -28z" />
                        </g>
                    </svg>
                </div>
                <button type="button" disabled={isPending} onClick={onCreate}>
                    {t("create")}
                </button>
            </div>
        </div>
    );
}