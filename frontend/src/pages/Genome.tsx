import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { getGenomeById } from "src/api/genomes";
import { Modal } from "src/components/Modal";
import { NewEdgeWeight } from "src/components/forms/Edge";
import { NewGene } from "src/components/forms/Gene";
import { GenomeGraphComponent } from "src/components/gene/Graph";
import type { Gene } from "src/components/gene/types";
import { GENE_EFFECT_TYPES } from "src/constants/effectTypes";
import { useGenomeDetailsMutations } from "src/hooks/genomes/useGenomeMutations";
import { getGeneEffectLabel, getTemplateGenomeLabel } from "src/i18n/meta";

type GenomeModal = "gene" | "edge-weight" | null;
type EdgeDraft = { source: number; target: number } | null;

export function GenomePage() {
    const { t } = useTranslation();
    const params = useParams();
    const genomeId = useMemo(() => Number(params.genomeId), [params.genomeId]);
    const [activeModal, setActiveModal] = useState<GenomeModal>(null);
    const [selectedGene, setSelectedGene] = useState<Gene | null>(null);
    const [isEditingGene, setIsEditingGene] = useState(false);
    const [isEdgeMode, setIsEdgeMode] = useState(false);
    const [edgeSourceId, setEdgeSourceId] = useState<number | null>(null);
    const [edgeDraft, setEdgeDraft] = useState<EdgeDraft>(null);

    const genomeQuery = useQuery({
        queryKey: ["genome", genomeId],
        queryFn: () => getGenomeById(genomeId),
        enabled: Number.isFinite(genomeId),
    });

    const {
        createGeneMutation,
        updateGeneMutation,
        deleteGeneMutation,
        createEdgeMutation,
        updatePositionMutation,
    } =
        useGenomeDetailsMutations(genomeId);

    const genome = genomeQuery.data;
    const genes = genome?.genes ?? [];
    const edges = genome?.edges ?? [];
    const isTemplate = genome?.is_template ?? false;
    const isOwned = genome?.is_owned ?? false;
    const canEditGenome = !isTemplate && isOwned;
    const genomeLabel = getTemplateGenomeLabel(
        genome?.template_key,
        genome?.name ?? t("genome"),
        genome?.description,
        t,
    );
    const graphGenes = useMemo(() => autoLayoutGenes(genes), [genes]);
    const geneById = new Map(genes.map(gene => [gene.id, gene]));
    const selectedNodeId = edgeSourceId ?? selectedGene?.id ?? null;

    const resetEdgeMode = () => {
        setIsEdgeMode(false);
        setEdgeSourceId(null);
        setEdgeDraft(null);
    };

    const handleGeneClick = (geneId: number) => {
        if (!isEdgeMode) {
            setSelectedGene(geneById.get(geneId) ?? null);
            setIsEditingGene(false);
            return;
        }

        if (edgeSourceId === null) {
            setEdgeSourceId(geneId);
            setSelectedGene(null);
            return;
        }

        if (edgeSourceId === geneId) {
            setEdgeSourceId(null);
            return;
        }

        setEdgeDraft({ source: edgeSourceId, target: geneId });
        setActiveModal("edge-weight");
    };

    const edgeDraftSource = edgeDraft ? geneById.get(edgeDraft.source) : null;
    const edgeDraftTarget = edgeDraft ? geneById.get(edgeDraft.target) : null;

    return (
        <div>
            <h2>{genomeLabel.name}</h2>
            {genomeLabel.description && <p className="form-hint">{genomeLabel.description}</p>}
            {isTemplate && <p className="template-note">{t("template_genome_readonly")}</p>}
            {!isTemplate && !isOwned && <p className="template-note">{t("runtime_genome_readonly")}</p>}
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                <button onClick={() => setActiveModal("gene")} disabled={!canEditGenome}>
                    {t("add_gene")}
                </button>
                <button
                    onClick={() => {
                        if (isEdgeMode) {
                            resetEdgeMode();
                        } else {
                            setIsEdgeMode(true);
                            setSelectedGene(null);
                        }
                    }}
                    disabled={genes.length < 2 || !canEditGenome}
                >
                    {isEdgeMode ? t("cancel_edge_mode") : t("create_edge")}
                </button>
            </div>
            {isEdgeMode && (
                <p>
                    {edgeSourceId === null
                        ? t("select_source_node")
                        : t("select_target_node")}
                </p>
            )}
            {genomeQuery.isLoading && <p>{t("loading")}...</p>}
            {genomeQuery.isError && <p>{t("error_loading_genome")}</p>}
            {genome && (
                <GenomeGraphComponent
                    graph={{ nodes: graphGenes, edges }}
                    width={800}
                    height={600}
                    selectedNodeId={selectedNodeId}
                    onNodeClick={handleGeneClick}
                    selectedEdgeId={null}
                    onEdgeClick={() => { }}
                    onNodePositionChange={(geneId, position) => {
                        if (canEditGenome) {
                            updatePositionMutation.mutate({ geneId, position });
                        }
                    }}
                    canDragNodes={!isEdgeMode && canEditGenome}
                />
            )}
            {activeModal === "gene" && (
                <Modal title={t("add_gene")} onClose={() => setActiveModal(null)}>
                    <NewGene
                        availableEffectTypes={GENE_EFFECT_TYPES}
                        onCreate={(gene) => {
                            createGeneMutation.mutate(gene, {
                                onSuccess: () => setActiveModal(null),
                            });
                        }}
                    />
                </Modal>
            )}
            {activeModal === "edge-weight" && edgeDraft && edgeDraftSource && edgeDraftTarget && (
                <Modal
                    title={t("create_edge")}
                    onClose={() => {
                        setActiveModal(null);
                        resetEdgeMode();
                    }}
                >
                    <NewEdgeWeight
                        sourceName={`${getGeneEffectLabel(edgeDraftSource.effect_type, t)} ${edgeDraftSource.id}`}
                        targetName={`${getGeneEffectLabel(edgeDraftTarget.effect_type, t)} ${edgeDraftTarget.id}`}
                        onCreate={(weight) => {
                            createEdgeMutation.mutate(
                                { source: edgeDraft.source, target: edgeDraft.target, weight },
                                {
                                    onSuccess: () => {
                                        setActiveModal(null);
                                        resetEdgeMode();
                                    },
                                },
                            );
                        }}
                    />
                </Modal>
            )}
            {selectedGene && (
                <Modal
                    title={`${t("gene")} ${selectedGene.id}`}
                    onClose={() => {
                        setSelectedGene(null);
                        setIsEditingGene(false);
                    }}
                >
                    {isEditingGene ? (
                        <>
                            <NewGene
                                availableEffectTypes={GENE_EFFECT_TYPES}
                                initialValue={{
                                    effect_type: selectedGene.effect_type,
                                    weight: selectedGene.weight,
                                    threshold: selectedGene.threshold,
                                    position: selectedGene.position,
                                    default_active: selectedGene.default_active,
                                }}
                                submitLabel={t("save")}
                                onCreate={(gene) => {
                                    updateGeneMutation.mutate(
                                        { geneId: selectedGene.id, gene },
                                        { onSuccess: () => setIsEditingGene(false) },
                                    );
                                }}
                            />
                            <button type="button" onClick={() => setIsEditingGene(false)}>
                                {t("cancel")}
                            </button>
                        </>
                    ) : (
                        <>
                            <p>{t("id")}: {selectedGene.id}</p>
                            <p>{t("effectType")}: {getGeneEffectLabel(selectedGene.effect_type, t)}</p>
                            <p>{t("gene_weight")}: {selectedGene.weight}</p>
                            <p>{t("threshold")}: {selectedGene.threshold}</p>
                            {selectedGene.default_active && <p>{t("default_active")}</p>}
                            {canEditGenome && (
                                <div style={{ display: "flex", gap: 8 }}>
                                    <button type="button" onClick={() => setIsEditingGene(true)}>
                                        {t("edit")}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            deleteGeneMutation.mutate(selectedGene.id, {
                                                onSuccess: () => {
                                                    setSelectedGene(null);
                                                    setIsEditingGene(false);
                                                },
                                            });
                                        }}
                                    >
                                        {t("delete")}
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </Modal>
            )}
        </div>
    );
}

function autoLayoutGenes(genes: Gene[]): Gene[] {
    if (genes.length <= 1) {
        return genes;
    }

    const uniquePositions = new Set(
        genes.map(gene => `${Math.round(gene.position.x)}:${Math.round(gene.position.y)}`),
    );
    if (uniquePositions.size > Math.floor(genes.length / 2)) {
        return genes;
    }

    const centerX = 400;
    const centerY = 300;
    const radius = Math.max(120, genes.length * 18);

    return genes.map((gene, index) => {
        const angle = (Math.PI * 2 * index) / genes.length;
        return {
            ...gene,
            position: {
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
            },
        };
    });
}
