import { apiFetch } from "./client";
import type {
    AvailableGenome,
    GeneCreate,
    GeneEdgeCreate,
    Genome,
    GenomeList,
    Position,
    Response,
} from "./types";

export function getAvailableGenomes(): Promise<AvailableGenome[]> {
    return apiFetch<AvailableGenome[]>("/genomes/available");
}

export function getGenomes(): Promise<GenomeList[]> {
    return apiFetch<GenomeList[]>("/genomes");
}

export function getGenomeById(genomeId: number): Promise<Genome> {
    return apiFetch<Genome>(`/genomes/${genomeId}`);
}

export function createGenome(name: string): Promise<Response> {
    return apiFetch<Response>("/genomes", {
        method: "POST",
        body: JSON.stringify({ name }),
    });
}

export function createGene(genomeId: number, gene: GeneCreate): Promise<Response> {
    return apiFetch<Response>(`/genomes/${genomeId}/genes`, {
        method: "POST",
        body: JSON.stringify(gene),
    });
}

export function updateGene(genomeId: number, geneId: number, gene: GeneCreate): Promise<Response> {
    return apiFetch<Response>(`/genomes/${genomeId}/genes/${geneId}`, {
        method: "PUT",
        body: JSON.stringify(gene),
    });
}

export function deleteGene(genomeId: number, geneId: number): Promise<Response> {
    return apiFetch<Response>(`/genomes/${genomeId}/genes/${geneId}`, {
        method: "DELETE",
    });
}

export function createGeneEdge(genomeId: number, edge: GeneEdgeCreate): Promise<Response> {
    return apiFetch<Response>(`/genomes/${genomeId}/edges`, {
        method: "POST",
        body: JSON.stringify(edge),
    });
}

export function updateGenePosition(
    genomeId: number,
    geneId: number,
    position: Position,
): Promise<Response> {
    return apiFetch<Response>(`/genomes/${genomeId}/genes/${geneId}/position`, {
        method: "PUT",
        body: JSON.stringify(position),
    });
}
