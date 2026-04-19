// список геномов
// при клике на геном открывается страница с геномом

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { getGenomes } from "src/api/genomes";
import { useTranslation } from "react-i18next";
import { useGenomesListMutations } from "src/hooks/genomes/useGenomeMutations";

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
            <input value={name} onChange={e => setName(e.target.value)} placeholder={t("genome_name")} />
            <button onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
            {genomesQuery.isLoading && <p>{t("loading")}...</p>}
            {genomesQuery.isError && <p>{t("error_loading_genomes")}</p>}
            {genomesQuery.data && (
                <ul>
                    {genomesQuery.data.map(genome => (
                        <li key={genome.id}>
                            <Link to={`/genomes/${genome.id}`}>
                                {genome.name}
                            </Link>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
};
