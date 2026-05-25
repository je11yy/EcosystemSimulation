import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useGenomesListMutations } from "src/hooks/genomes/useGenomeMutations";

export function NewGenome() {
    const { t } = useTranslation();

    const [name, setName] = useState("");

    const { createMutation } = useGenomesListMutations();

    return (
        <div className="simulation-modal">
            <div className="scratch">
                <div className="create-form">
                    <input className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder={t("genome_name")} />
                    <button className="form-input-button" onClick={() => createMutation.mutate(name, { onSuccess: () => setName("") })} disabled={createMutation.isPending || !name}>{t("create")}</button>
                </div>
            </div>
        </div>
    );
}