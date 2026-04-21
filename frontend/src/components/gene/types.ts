import type { Node } from "../graph/types";

export interface Gene extends Node {
    name: string;
    effect_type: string;
    weight: number;
    threshold: number;
    default_active: boolean;
};
