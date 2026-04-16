import type { Gene } from "src/components/gene/types";
import type { Edge, Position } from "src/components/graph/types";
import type { Territory } from "src/components/territory/types";

// basic types

export type Response = {
    success: boolean;
    message?: string;
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
    occupancy_by_territory: Record<number, number>;
    deaths_by_reason: Record<string, number>;
    successful_hunts: number;
    unsuccessful_hunts: number;
    consumed_food: number;
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

// genomes

export interface AvailableGenome {
    id: number;
    name: string;
}

export interface Genome extends AvailableGenome {
    genes: Gene[];
    edges: Edge[];
}

export interface GenomeList {
    id: number;
    name: string;
    user_id: number;
    updated_at: string;
}
