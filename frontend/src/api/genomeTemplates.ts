import { apiFetch } from "./client";
import type {
  GenomeTemplateCreatePayload,
  GenomeTemplateDetails,
  GenomeTemplateEdge,
  GenomeTemplateEdgeCreatePayload,
  GenomeTemplateGene,
  GenomeTemplateGeneCreatePayload,
  GenomeTemplateRead,
} from "./types";

export function getGenomeTemplates(userId: number): Promise<GenomeTemplateRead[]> {
  return apiFetch<GenomeTemplateRead[]>(`/genome-templates?user_id=${userId}`);
}

export function createGenomeTemplate(
  userId: number,
  payload: GenomeTemplateCreatePayload
): Promise<GenomeTemplateRead> {
  return apiFetch<GenomeTemplateRead>(`/genome-templates?user_id=${userId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getGenomeTemplate(templateId: number): Promise<GenomeTemplateDetails> {
  return apiFetch<GenomeTemplateDetails>(`/genome-templates/${templateId}`);
}

export function addGeneToGenomeTemplate(
  templateId: number,
  payload: GenomeTemplateGeneCreatePayload
): Promise<GenomeTemplateGene> {
  return apiFetch<GenomeTemplateGene>(`/genome-templates/${templateId}/genes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function addEdgeToGenomeTemplate(
  templateId: number,
  payload: GenomeTemplateEdgeCreatePayload
): Promise<GenomeTemplateEdge> {
  return apiFetch<GenomeTemplateEdge>(`/genome-templates/${templateId}/edges`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateGenomeTemplateGenePosition(
  templateId: number,
  geneId: number,
  payload: { x?: number | null; y?: number | null }
) {
  return apiFetch(`/genome-templates/${templateId}/genes/${geneId}/position`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteGeneFromGenomeTemplate(templateId: number, geneId: number) {
  return apiFetch(`/genome-templates/${templateId}/genes/${geneId}`, {
    method: "DELETE",
  });
}

export function deleteEdgeFromGenomeTemplate(templateId: number, edgeId: number) {
  return apiFetch(`/genome-templates/${templateId}/edges/${edgeId}`, {
    method: "DELETE",
  });
}