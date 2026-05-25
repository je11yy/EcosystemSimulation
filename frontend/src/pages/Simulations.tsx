// список симуляций
// при клике на симуляцию открывается страница с симуляцией

import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { getSimulations } from "src/api/simulations";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { Modal } from "src/components/Modal";
import { NewSimulation } from "src/components/simulation/NewSimulation";

export function SimulationsPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [isModalActive, setIsModalActive] = useState(false);

    const simulationsQuery = useQuery({
        queryKey: ["simulations"],
        queryFn: getSimulations,
    });

    return (
        <div>
            <a className="create-simulation-link" onClick={() => setIsModalActive(true)}>
                <svg className="icon" xmlns="http://www.w3.org/2000/svg" version="1.0" width="512.000000pt" height="512.000000pt" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet">
                    <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="currentColor" stroke="none">
                        <path d="M2375 4900 c-791 -70 -1478 -511 -1864 -1197 -324 -576 -385 -1281 -167 -1912 116 -334 288 -611 540 -869 826 -848 2142 -945 3095 -230 182 137 399 367 529 560 453 677 523 1534 187 2279 -114 254 -266 471 -479 685 -240 240 -480 400 -774 518 -334 134 -729 196 -1067 166z m263 -1076 c44 -18 87 -57 110 -99 15 -26 18 -86 22 -490 l5 -460 460 -5 c503 -5 487 -3 547 -67 76 -80 76 -206 0 -286 -60 -64 -44 -62 -547 -67 l-460 -5 -5 -460 c-5 -503 -3 -487 -67 -547 -80 -76 -206 -76 -286 0 -64 60 -62 44 -67 547 l-5 460 -460 5 c-503 5 -487 3 -547 67 -76 80 -76 206 0 286 60 64 44 62 547 67 l460 5 5 460 c5 503 3 487 67 547 59 56 148 73 221 42z" />
                    </g>
                </svg>
                <span>
                    {t("create_new_simulation")}
                </span>
            </a>
            {isModalActive && (
                <Modal title={t("create_simulation")} onClose={() => setIsModalActive(false)}>
                    <NewSimulation />
                </Modal>
            )}
            {simulationsQuery.isLoading && <p>{t("loading")}...</p>}
            {simulationsQuery.isError && <p>{t("error_loading_simulations")}</p>}
            {simulationsQuery.data && (
                <ul className="simulations-list">
                    {simulationsQuery.data.map(simulation => (
                        <li key={simulation.id} onClick={() => navigate(`/simulations/${simulation.id}`)}>
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
