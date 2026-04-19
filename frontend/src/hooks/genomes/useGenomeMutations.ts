import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
    createGene,
    createGeneEdge,
    createGenome,
    deleteGene,
    updateGene,
    updateGenePosition,
} from "src/api/genomes";
import type { GeneCreate, GeneEdgeCreate, Position } from "src/api/types";

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

/** Мутации для страницы конкретного генома */
export function useGenomeDetailsMutations(genomeId: number) {
    const queryClient = useQueryClient();

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["genome", genomeId] });
        queryClient.invalidateQueries({ queryKey: ["genomes"] });
    };

    const createGeneMutation = useMutation({
        mutationFn: (gene: GeneCreate) => createGene(genomeId, gene),
        onSuccess: invalidate,
    });

    const updateGeneMutation = useMutation({
        mutationFn: ({ geneId, gene }: { geneId: number; gene: GeneCreate }) =>
            updateGene(genomeId, geneId, gene),
        onSuccess: invalidate,
    });

    const deleteGeneMutation = useMutation({
        mutationFn: (geneId: number) => deleteGene(genomeId, geneId),
        onSuccess: invalidate,
    });

    const createEdgeMutation = useMutation({
        mutationFn: (edge: GeneEdgeCreate) => createGeneEdge(genomeId, edge),
        onSuccess: invalidate,
    });

    const updatePositionMutation = useMutation({
        mutationFn: ({ geneId, position }: { geneId: number; position: Position }) =>
            updateGenePosition(genomeId, geneId, position),
        onSuccess: invalidate,
    });

    return {
        createGeneMutation,
        updateGeneMutation,
        deleteGeneMutation,
        createEdgeMutation,
        updatePositionMutation,
    };
}
