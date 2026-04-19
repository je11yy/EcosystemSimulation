import type { Gene } from "src/components/gene/types";
import type { Edge, Position } from "src/components/graph/types";
import type { Territory } from "src/components/territory/types";

export type { Position } from "src/components/graph/types";

// basic types

export type Response = {
    success: boolean;
    message?: string;
}

export type ScenarioPreset = {
    key: string;
    name: string;
    description: string;
}

export type ScenarioCreateResponse = Response & {
    simulation_id: number;
}

export type User = {
    id: number;
    nickname: string;
}

export type SimulationStatus = "draft" | "loaded" | "running" | "paused" | "stopped";

export interface Step {
    eat: number;
    move: number;
    mate: number;
    rest: number;
    hunt: number;

    deaths: number;
    births: number;
    fights: number;
}

export interface TickMetrics {
    alive_population: number;
    avg_hunger: number;
    avg_satisfaction: number;
    occupancy_by_territory: Record<number, number>;
    deaths_by_reason: Record<string, number>;
    successful_hunts: number;
    unsuccessful_hunts: number;
    consumed_food: number;
}

export interface StepEvents {
    applied_results: Array<Record<string, unknown>>;
    deaths: Array<Record<string, unknown>>;
    births: Array<Record<string, unknown>>;
    fights: Array<Record<string, unknown>>;
    hunts: Array<Record<string, unknown>>;
}

export interface AgentDecision {
    agent_id: number;
    action: "eat" | "move" | "mate" | "rest" | "hunt";
    to_territory?: number | null;
    partner_id?: number | null;
    target_id?: number | null;
    metadata: Record<string, unknown>;
}

export interface Log {
    id: number;
    simulation_id: number;
    tick: number;
    agent_decisions: AgentDecision[];
    step_result: Step;
    metrics: TickMetrics;
    events: StepEvents;
    created_at: string;
}

// simulations

export interface Simulation {
    id: number;
    name: string;
    user_id: number;
    updated_at: string;
    status: SimulationStatus;
    tick: number;
};

export interface SimulationDetails extends Simulation {
    territories: Territory[];
    territories_edges: Edge[];

    last_log: Log | null;
    logs: Log[];
    logs_count: number;
    last_step: Step | null;
};

// agents

export interface AgentCreate {
    territory_id: number;
    genome_id: number | null;
    
    sex: string;
}

export interface Agent extends AgentCreate {
    id: number;
    is_alive: boolean;

    hunger: number;
    hp: number;

    strength: number;
    defense: number;
    temp_pref: number;

    pregnant: boolean;
	ticks_to_birth: number | null;

    satisfaction: number;
}

// territories

export interface TerritoryCreate {
    food?: number;
    food_capacity: number;
    food_regen_per_tick: number;
    temperature: number;

    position: Position;
    simulation_id?: number;
}

export interface TerritoryEdgeCreate {
    source: number;
    target: number;
    weight: number;
    simulation_id?: number;
}

export interface TerritoryEdge extends TerritoryEdgeCreate {
    id: number;
}

// genes

export type GeneEffectType =
    | "MAX_HP"
    | "STRENGTH"
    | "DEFENSE"
    | "METABOLISM"
    | "HUNGER_DRIVE"
    | "DISPERSAL_DRIVE"
    | "SITE_FIDELITY"
    | "REPRODUCTION_DRIVE"
    | "HEAT_RESISTANCE"
    | "COLD_RESISTANCE"
    | "AGGRESSION_DRIVE"
    | "PREDATION_DRIVE"
    | "CARNIVORE_DIGESTION"
    | "CANNIBAL_TOLERANCE"
    | "SOCIAL_TOLERANCE"
    | "MUTATION_RATE";

export interface GeneCreate {
    name: string;
    effect_type: GeneEffectType | string;
    weight: number;
    threshold: number;
    position: Position;
    default_active: boolean;
}

export interface GeneEdgeCreate {
    source: number;
    target: number;
    weight: number;
}

// genomes

export interface AvailableGenome {
    id: number;
    name: string;
    is_template: boolean;
}

export interface Genome extends AvailableGenome {
    description?: string | null;
    genes: Gene[];
    edges: Edge[];
}

export interface GenomeList {
    id: number;
    name: string;
    user_id: number | null;
    description?: string | null;
    is_template: boolean;
    updated_at: string;
}
