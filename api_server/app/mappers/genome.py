from typing import Any

from app.mappers.common import iso, position
from app.models import Gene, GeneEdge, Genome


def gene_to_dict(gene: Gene) -> dict[str, Any]:
    return {
        "id": gene.id,
        "name": gene.name,
        "position": position(gene.x, gene.y),
        "effect_type": gene.effect_type,
        "threshold": gene.threshold,
        "weight": gene.weight,
        "default_active": gene.default_active,
    }


def gene_edge_to_dict(edge: GeneEdge) -> dict[str, Any]:
    return {
        "id": edge.id,
        "source": edge.source_id,
        "target": edge.target_id,
        "weight": edge.weight,
    }


def genome_list_item_to_dict(genome: Genome, user_id: int | None = None) -> dict[str, Any]:
    return {
        "id": genome.id,
        "name": genome.name,
        "user_id": user_id if user_id is not None else genome.user_id,
        "description": genome.description,
        "is_template": genome.is_template,
        "updated_at": iso(genome.updated_at),
    }


def genome_to_dict(genome: Genome) -> dict[str, Any]:
    genes = [link.gene for link in genome.gene_links]
    gene_ids = {gene.id for gene in genes}
    edges = [edge for gene in genes for edge in gene.outgoing_edges if edge.target_id in gene_ids]
    return {
        "id": genome.id,
        "name": genome.name,
        "description": genome.description,
        "is_template": genome.is_template,
        "genes": [gene_to_dict(gene) for gene in genes],
        "edges": [gene_edge_to_dict(edge) for edge in edges],
    }
