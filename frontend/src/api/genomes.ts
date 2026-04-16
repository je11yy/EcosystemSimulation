import { apiFetch } from "./client";
import type { AvailableGenome, Genome, GenomeList, Response } from "./types";

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
