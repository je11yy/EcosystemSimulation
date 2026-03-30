import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addEdgeToGenomeTemplate,
  addGeneToGenomeTemplate,
  deleteEdgeFromGenomeTemplate,
  deleteGeneFromGenomeTemplate,
  getGenomeTemplate,
  updateGenomeTemplateGenePosition,
} from "../api/genomeTemplates";
import { GenomeGraph } from "../components/GenomeGraph";
import { CreateGenomeTemplateGeneForm } from "../components/CreateGenomeTemplateGeneForm";
import { CreateGenomeTemplateEdgeForm } from "../components/CreateGenomeTemplateEdgeForm";
import { GeneDetailsPanel } from "../components/GeneDetailsPanel";
import { GeneEdgeDetailsPanel } from "../components/GeneEdgeDetailsPanel";

export function GenomeTemplateDetailsPage() {
  const params = useParams();
  const queryClient = useQueryClient();

  const [selectedGeneId, setSelectedGeneId] = useState<number | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<number | null>(null);

  const templateId = useMemo(() => Number(params.templateId), [params.templateId]);

  const templateQuery = useQuery({
    queryKey: ["genome-template", templateId],
    queryFn: () => getGenomeTemplate(templateId),
    enabled: Number.isFinite(templateId),
  });

  const addGeneMutation = useMutation({
    mutationFn: (payload: {
      name: string;
      effect_type: string;
      chromosome_id: string;
      position: number;
      default_active: boolean;
      threshold: number;
      x?: number | null;
      y?: number | null;
    }) => addGeneToGenomeTemplate(templateId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["genome-template", templateId] });
    },
  });

  const addEdgeMutation = useMutation({
    mutationFn: (payload: {
      source_gene_id: number;
      target_gene_id: number;
      weight: number;
    }) => addEdgeToGenomeTemplate(templateId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["genome-template", templateId] });
    },
  });

  const moveGeneMutation = useMutation({
    mutationFn: (payload: { geneId: number; x: number; y: number }) =>
      updateGenomeTemplateGenePosition(templateId, payload.geneId, {
        x: payload.x,
        y: payload.y,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["genome-template", templateId] });
    },
  });

  const deleteGeneMutation = useMutation({
    mutationFn: (geneId: number) => deleteGeneFromGenomeTemplate(templateId, geneId),
    onSuccess: async () => {
      setSelectedGeneId(null);
      await queryClient.invalidateQueries({ queryKey: ["genome-template", templateId] });
    },
  });

  const deleteEdgeMutation = useMutation({
    mutationFn: (edgeId: number) => deleteEdgeFromGenomeTemplate(templateId, edgeId),
    onSuccess: async () => {
      setSelectedEdgeId(null);
      await queryClient.invalidateQueries({ queryKey: ["genome-template", templateId] });
    },
  });

  if (templateQuery.isLoading) {
    return <div style={{ padding: 24 }}>Загрузка...</div>;
  }

  if (templateQuery.isError || !templateQuery.data) {
    return <div style={{ padding: 24 }}>Не удалось загрузить шаблон.</div>;
  }

  const data = templateQuery.data;

  const selectedGene =
    data.genes.find((gene) => gene.id === selectedGeneId) ?? null;

  const selectedGeneState =
    selectedGene != null
      ? data.gene_states.find((state) => state.id === selectedGene.id) ?? null
      : null;

  const selectedEdge =
    data.edges.find((edge) => edge.id === selectedEdgeId) ?? null;

  const isBusy =
    addGeneMutation.isPending ||
    addEdgeMutation.isPending ||
    moveGeneMutation.isPending ||
    deleteGeneMutation.isPending ||
    deleteEdgeMutation.isPending;

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <Link to="/genome-templates">← К шаблонам генома</Link>
      </div>

      <h1>{data.template.name}</h1>
      <p>
        species group: <b>{data.template.species_group}</b>
      </p>
      {data.template.description && <p>{data.template.description}</p>}
      {data.template.is_builtin && (
        <p style={{ color: "#1d4ed8" }}>
          Это встроенный шаблон. Он доступен только для просмотра.
        </p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 24,
          marginBottom: 24,
        }}
      >
        <CreateGenomeTemplateGeneForm
          onSubmit={(payload) => addGeneMutation.mutate(payload)}
          isBusy={addGeneMutation.isPending || data.template.is_builtin}
        />
        <CreateGenomeTemplateEdgeForm
          genes={data.genes}
          onSubmit={(payload) => addEdgeMutation.mutate(payload)}
          isBusy={addEdgeMutation.isPending || data.template.is_builtin}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: 24,
        }}
      >
        <GenomeGraph
          genes={data.genes}
          edges={data.edges}
          geneStates={data.gene_states}
          selectedGeneId={selectedGeneId}
          selectedEdgeId={selectedEdgeId}
          draggable={!data.template.is_builtin}
          onGeneClick={(geneId) => {
            setSelectedEdgeId(null);
            setSelectedGeneId(geneId);
          }}
          onEdgeClick={(edgeId) => {
            setSelectedGeneId(null);
            setSelectedEdgeId(edgeId);
          }}
          onGeneMoveEnd={(geneId, x, y) =>
            moveGeneMutation.mutate({ geneId, x, y })
          }
        />

        <div style={{ display: "grid", gap: 24 }}>
          <GeneDetailsPanel
            gene={selectedGene}
            geneState={selectedGeneState}
            onDelete={(geneId) => deleteGeneMutation.mutate(geneId)}
            isBusy={isBusy || data.template.is_builtin}
          />

          <GeneEdgeDetailsPanel
            edge={selectedEdge}
            genes={data.genes}
            onDelete={(edgeId) => deleteEdgeMutation.mutate(edgeId)}
            isBusy={isBusy || data.template.is_builtin}
          />
        </div>
      </div>
    </div>
  );
}