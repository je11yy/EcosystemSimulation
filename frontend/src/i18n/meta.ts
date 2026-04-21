import type { ScenarioPreset } from "src/api/types";

type TFunction = (key: string) => string;

export function getScenarioLabel(scenario: ScenarioPreset, t: TFunction) {
    return {
        name: translateWithFallback(
            t,
            `scenario_meta.${scenario.key}.name`,
            scenario.name,
        ),
        description: translateWithFallback(
            t,
            `scenario_meta.${scenario.key}.description`,
            scenario.description,
        ),
    };
}

export function getTemplateGenomeLabel(
    templateKey: string | null | undefined,
    name: string,
    description: string | null | undefined,
    t: TFunction,
) {
    if (!templateKey) {
        return { name, description: description ?? "" };
    }

    return {
        name: translateWithFallback(
            t,
            `template_genome_meta.${templateKey}.name`,
            name,
        ),
        description: translateWithFallback(
            t,
            `template_genome_meta.${templateKey}.description`,
            description ?? "",
        ),
    };
}

export function getGeneEffectLabel(effectType: string, t: TFunction) {
    return translateWithFallback(t, `gene_effect_label.${effectType}`, effectType);
}

function translateWithFallback(t: TFunction, key: string, fallback: string) {
    const translated = t(key);
    return translated === key ? fallback : translated;
}
