// список симуляций
// при клике на симуляцию открывается страница с симуляцией

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { getSimulations } from "src/api/simulations";
import { useTranslation } from "react-i18next";
import { useSimulationsListMutations } from "src/hooks/simulations/useSimulationMutations";

export function SimulationsPage() {
    const { t } = useTranslation();
    const [name, setName] = useState("");

    const simulationsQuery = useQuery({
        queryKey: ["simulations"],
        queryFn: getSimulations,
    });

    const { createMutation } = useSimulationsListMutations();

    return (
        <div>
            <h1>{t("simulations")}</h1>
            <input value={name} onChange={e => setName(e.target.value)} placeholder={t("simulation_name")} />
            <button onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
            {simulationsQuery.isLoading && <p>{t("loading")}...</p>}
            {simulationsQuery.isError && <p>{t("error_loading_simulations")}</p>}
            {simulationsQuery.data && (
                <ul>
                    {simulationsQuery.data.map(simulation => (
                        <li key={simulation.id}>
                            {simulation.name}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
};
