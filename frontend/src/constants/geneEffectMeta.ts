import type { GeneEffectType } from "src/api/types";

type GeneEffectMeta = {
    descriptionKey: string;
    thresholdKey: string;
    weightKey: string;
};

const DEFAULT_META: GeneEffectMeta = {
    descriptionKey: "gene_effect_meta.default.description",
    thresholdKey: "gene_effect_meta.default.threshold",
    weightKey: "gene_effect_meta.default.weight",
};

export const GENE_EFFECT_META: Record<GeneEffectType, GeneEffectMeta> = {
    MAX_HP: {
        descriptionKey: "gene_effect_meta.MAX_HP.description",
        thresholdKey: "gene_effect_meta.MAX_HP.threshold",
        weightKey: "gene_effect_meta.MAX_HP.weight",
    },
    STRENGTH: {
        descriptionKey: "gene_effect_meta.STRENGTH.description",
        thresholdKey: "gene_effect_meta.STRENGTH.threshold",
        weightKey: "gene_effect_meta.STRENGTH.weight",
    },
    DEFENSE: {
        descriptionKey: "gene_effect_meta.DEFENSE.description",
        thresholdKey: "gene_effect_meta.DEFENSE.threshold",
        weightKey: "gene_effect_meta.DEFENSE.weight",
    },
    METABOLISM: {
        descriptionKey: "gene_effect_meta.METABOLISM.description",
        thresholdKey: "gene_effect_meta.METABOLISM.threshold",
        weightKey: "gene_effect_meta.METABOLISM.weight",
    },
    HUNGER_DRIVE: {
        descriptionKey: "gene_effect_meta.HUNGER_DRIVE.description",
        thresholdKey: "gene_effect_meta.HUNGER_DRIVE.threshold",
        weightKey: "gene_effect_meta.HUNGER_DRIVE.weight",
    },
    DISPERSAL_DRIVE: {
        descriptionKey: "gene_effect_meta.DISPERSAL_DRIVE.description",
        thresholdKey: "gene_effect_meta.DISPERSAL_DRIVE.threshold",
        weightKey: "gene_effect_meta.DISPERSAL_DRIVE.weight",
    },
    SITE_FIDELITY: {
        descriptionKey: "gene_effect_meta.SITE_FIDELITY.description",
        thresholdKey: "gene_effect_meta.SITE_FIDELITY.threshold",
        weightKey: "gene_effect_meta.SITE_FIDELITY.weight",
    },
    REPRODUCTION_DRIVE: {
        descriptionKey: "gene_effect_meta.REPRODUCTION_DRIVE.description",
        thresholdKey: "gene_effect_meta.REPRODUCTION_DRIVE.threshold",
        weightKey: "gene_effect_meta.REPRODUCTION_DRIVE.weight",
    },
    HEAT_RESISTANCE: {
        descriptionKey: "gene_effect_meta.HEAT_RESISTANCE.description",
        thresholdKey: "gene_effect_meta.HEAT_RESISTANCE.threshold",
        weightKey: "gene_effect_meta.HEAT_RESISTANCE.weight",
    },
    COLD_RESISTANCE: {
        descriptionKey: "gene_effect_meta.COLD_RESISTANCE.description",
        thresholdKey: "gene_effect_meta.COLD_RESISTANCE.threshold",
        weightKey: "gene_effect_meta.COLD_RESISTANCE.weight",
    },
    AGGRESSION_DRIVE: {
        descriptionKey: "gene_effect_meta.AGGRESSION_DRIVE.description",
        thresholdKey: "gene_effect_meta.AGGRESSION_DRIVE.threshold",
        weightKey: "gene_effect_meta.AGGRESSION_DRIVE.weight",
    },
    PREDATION_DRIVE: {
        descriptionKey: "gene_effect_meta.PREDATION_DRIVE.description",
        thresholdKey: "gene_effect_meta.PREDATION_DRIVE.threshold",
        weightKey: "gene_effect_meta.PREDATION_DRIVE.weight",
    },
    CARNIVORE_DIGESTION: {
        descriptionKey: "gene_effect_meta.CARNIVORE_DIGESTION.description",
        thresholdKey: "gene_effect_meta.CARNIVORE_DIGESTION.threshold",
        weightKey: "gene_effect_meta.CARNIVORE_DIGESTION.weight",
    },
    CANNIBAL_TOLERANCE: {
        descriptionKey: "gene_effect_meta.CANNIBAL_TOLERANCE.description",
        thresholdKey: "gene_effect_meta.CANNIBAL_TOLERANCE.threshold",
        weightKey: "gene_effect_meta.CANNIBAL_TOLERANCE.weight",
    },
    SOCIAL_TOLERANCE: {
        descriptionKey: "gene_effect_meta.SOCIAL_TOLERANCE.description",
        thresholdKey: "gene_effect_meta.SOCIAL_TOLERANCE.threshold",
        weightKey: "gene_effect_meta.SOCIAL_TOLERANCE.weight",
    },
};

export function getGeneEffectMeta(effectType: string): GeneEffectMeta {
    return GENE_EFFECT_META[effectType as GeneEffectType] ?? DEFAULT_META;
}
