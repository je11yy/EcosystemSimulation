import type { Node } from "../graph/types";

export interface Territory extends Node {
    food: number;
	temperature: number;
	food_regen_per_tick: number;
	food_capacity: number;
	occupant_count?: number;
}
