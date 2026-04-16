import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createGenome } from "src/api/genomes";

/** Мутации для страницы списка геномов */
export function useGenomesListMutations() {
    const queryClient = useQueryClient();

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["genomes"] });
    };

    const createMutation = useMutation({
        mutationFn: (name: string) => createGenome(name),
        onSuccess: invalidate,
    });

    return { createMutation };
}
