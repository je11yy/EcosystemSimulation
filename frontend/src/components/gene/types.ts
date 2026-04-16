import type { Node } from "../graph/types";

export interface Gene extends Node {
    effect_type: string;
    threshold: number;
    is_active: boolean;
};
