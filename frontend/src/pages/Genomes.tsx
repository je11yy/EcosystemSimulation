// список геномов
// при клике на геном открывается страница с геномом

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { getGenomes } from "src/api/genomes";
import { useTranslation } from "react-i18next";
import { useGenomesListMutations } from "src/hooks/genomes/useGenomeMutations";
import { getTemplateGenomeLabel } from "src/i18n/meta";

export function GenomesPage() {
    const { t } = useTranslation();
    const [name, setName] = useState("");

    const genomesQuery = useQuery({
        queryKey: ["genomes"],
        queryFn: getGenomes,
    });

    const { createMutation } = useGenomesListMutations();

    return (
        <div>
            <h1>{t("genomes")}</h1>
            <div className="create-form">
                <input className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder={t("genome_name")} />
                <button className="form-input-button" onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
            </div>
            {genomesQuery.isLoading && <p>{t("loading")}...</p>}
            {genomesQuery.isError && <p>{t("error_loading_genomes")}</p>}
            {genomesQuery.data && (
                <ul>
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

    return (
        <li>
            <Link to={`/genomes/${genome.id}`}>
                {label.name}
            </Link>
            {genome.is_template && (
                <span className="template-badge">{t("template")}</span>
            )}
            {label.description && <p className="form-hint">{label.description}</p>}
        </li>
    );
}
