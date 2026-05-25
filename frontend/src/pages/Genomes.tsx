// список геномов
// при клике на геном открывается страница с геномом

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getGenomes } from "src/api/genomes";
import { useTranslation } from "react-i18next";
import { getTemplateGenomeLabel } from "src/i18n/meta";
import { Modal } from "src/components/Modal";
import { NewGenome } from "src/components/genome/newGenome";

export function GenomesPage() {
    const { t } = useTranslation();
    const [isModalActive, setIsModalActive] = useState(false);

    const genomesQuery = useQuery({
        queryKey: ["genomes"],
        queryFn: getGenomes,
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
                    {t("create_new_genome")}
                </span>
            </a>
            {isModalActive && (
                <Modal title={t("create_genome")} onClose={() => setIsModalActive(false)}>
                    <NewGenome />
                </Modal>
            )}
            {genomesQuery.isLoading && <p>{t("loading")}...</p>}
            {genomesQuery.isError && <p>{t("error_loading_genomes")}</p>}
            {genomesQuery.data && (
                <ul className="list">
                    {genomesQuery.data.map(genome => (
                        <GenomeListItem key={genome.id} genome={genome} />
                    ))}
                </ul>
            )}
        </div>
    )
};

function GenomeListItem({
    genome,
}: {
    genome: Awaited<ReturnType<typeof getGenomes>>[number];
}) {
    const { t } = useTranslation();
    const label = getTemplateGenomeLabel(
        genome.template_key,
        genome.name,
        genome.description,
        t,
    );
    const navigate = useNavigate();

    return (
        <li onClick={() => navigate(`/genomes/${genome.id}`)}>
            <div className="label-icon">
                {genome.is_template && (
                    <div className="template">
                        <svg className="icon" xmlns="http://www.w3.org/2000/svg" version="1.0" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet">
                            <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="currentColor" stroke="none">
                                <path d="M2741 4784 c-102 -27 -166 -71 -291 -198 -337 -344 -1925 -2017 -1950 -2055 -58 -86 -74 -145 -74 -266 0 -129 19 -189 88 -282 24 -32 363 -376 752 -764 784 -780 753 -753 911 -781 125 -21 276 18 373 98 20 16 514 514 1098 1107 1000 1016 1064 1082 1097 1150 19 40 40 96 45 126 6 32 10 331 10 755 0 598 -2 711 -15 761 -45 172 -179 305 -352 350 -84 22 -1610 21 -1692 -1z m1665 -330 c15 -11 37 -33 48 -48 21 -27 21 -38 24 -727 2 -577 0 -704 -11 -731 -9 -20 -443 -470 -1066 -1105 -930 -948 -1057 -1074 -1093 -1084 -83 -22 -92 -16 -337 221 -337 325 -1197 1191 -1211 1219 -22 42 -15 117 13 159 49 70 1981 2087 2017 2105 33 16 87 17 812 15 767 -3 777 -3 804 -24z" />
                                <path d="M3548 4151 c-192 -62 -308 -227 -308 -438 0 -131 39 -229 128 -325 245 -263 678 -168 782 171 76 245 -66 516 -311 592 -80 25 -213 25 -291 0z m247 -326 c135 -102 44 -308 -117 -264 -131 35 -166 210 -55 280 46 29 123 22 172 -16z" />
                            </g>
                        </svg>
                    </div>
                )}
                <Link to={`/genomes/${genome.id}`}>
                    {label.name}
                </Link>
            </div>
            {label.description && <p className="form-hint">{label.description}</p>}
        </li>
    );
}
