export type SimulationStatus = "draft" | "loaded" | "running" | "paused" | "stopped";

export interface SimulationRead {
	id: number;
	user_id: number;
	name: string;
	status: SimulationStatus;
	tick: number;
	created_at: string;
	updated_at: string;
}

export interface TerritoryState {
	id: string;
	food: number;
	temperature: number;
	food_regen_per_tick: number;
	food_capacity: number;
	x?: number | null;
	y?: number | null;
}

export interface TerritoryEdgeState {
	source_id: string;
	target_id: string;
	movement_cost: number;
}

export interface GeneState {
	gene_id: number;
	is_active: boolean;
}

export interface Gene {
	id: number;
	name: string;
	chromosome_id: string;
	position: number;
	default_active: boolean;
	effect_type: string;
	threshold: number;
}

export interface GeneEdge {
	source_gene_id: number;
	target_gene_id: number;
	weight: number;
}

export interface AgentState {
	id: string;
	location: string;
	hunger: number;
	hp: number;
	base_strength: number;
	base_defense: number;
	sex: string;
	pregnant: boolean;
	ticks_to_birth: number;
	father_id: string | null;
	base_temp_pref: number;
	satisfaction: number;
	alive: boolean;
	genes: Gene[];
	gene_edges: GeneEdge[];
	gene_states: GeneState[];
}

export interface SimulationStateResponse {
	simulation_id: number;
	tick: number;
	territories: TerritoryState[];
	territory_edges: TerritoryEdgeState[];
	agents: AgentState[];
}

export interface SimulationStateStepSnapshot {
	simulation_id: number;
	tick: number;
	territories: TerritoryState[];
	territory_edges: TerritoryEdgeState[];
	agents: AgentState[];
	metrics_history: MetricsHistoryPoint[];
}

export interface StartSimulationResponse {
	simulation_id: number;
	status: string;
	runtime: {
		ok: boolean;
		simulation_id: string;
		tick: number;
		loaded_agents: number;
		loaded_territories: number;
	};
}

export interface StopSimulationResponse {
	simulation_id: number;
	status: string;
	runtime: {
		ok: boolean;
		simulation_id: string;
		removed: boolean;
	};
}

export interface StepSimulationResponse {
	simulation_id: number;
	state: {
		tick: number;
		territories: TerritoryState[];
		agents: AgentState[];
	};
	step_result: {
		tick: number;
		decisions: Array<{
			tick: number;
			agent_id: string;
			chosen: {
				type: string;
				to_territory: string | null;
				partner_id: string | null;
				target_id: string | null;
				tag: string | null;
			};
		}>;
		applied_results: Array<{
			agent_id: string;
			action_type: string;
			success: boolean;
			reason: string | null;
			consumed_food: boolean;
			created_pregnancy: boolean;
			hp_loss: number;
			hunger_restored: number;
			target_id: string | null;
			damage_to_target: number;
			target_died: boolean;
			hunter_died: boolean;
			hunger_delta: number;
		}>;
		deaths: Array<{
			agent_id: string;
			reason: string;
			tick: number;
		}>;
		births: Array<{
			parent_id: string;
			child_id: string;
			tick: number;
		}>;
		fights: Array<{
			territory_id: string;
			winner_id: string;
			loser_id: string;
			loser_hp_loss: number;
		}>;
		hunts: Array<{
			territory_id: string;
			hunter_id: string;
			target_id: string;
			success: boolean;
			damage_to_target: number;
			damage_to_hunter: number;
			target_died: boolean;
			hunter_died: boolean;
			hunger_restored: number;
		}>;
		metrics: {
			alive_population: number;
			population_by_species_group: Record<string, number>;
			avg_hunger_alive: number;
			avg_hp_alive: number;
			avg_hunt_cooldown_alive: number;
			occupancy_by_territory: Record<string, number>;
			action_counts: Record<string, number>;
			successful_hunts: number;
			births_count: number;
			deaths_count: number;
			deaths_by_reason: Record<string, number>;
		};
		metrics_history: Array<{
			tick: number;
			alive_population: number;
			avg_hunger_alive: number;
			avg_hp_alive: number;
			avg_hunt_cooldown_alive: number;
			successful_hunts: number;
			births_count: number;
			deaths_count: number;
			population_by_species_group: Record<string, number>;
			occupancy_by_territory: Record<string, number>;
			action_counts: Record<string, number>;
			deaths_by_reason: Record<string, number>;
		}>;
	};
}

export interface TerritoryCreatePayload {
	food: number;
	temperature: number;
	food_regen_per_tick: number;
	food_capacity: number;
	x?: number | null;
	y?: number | null;
}

export interface AgentCreatePayload {
	territory_id: number;
	hunger: number;
	hp: number;
	base_strength: number;
	base_defense: number;
	sex: string;
	pregnant: boolean;
	ticks_to_birth: number;
	father_id?: number | null;
	base_temp_pref: number;
	satisfaction: number;
	alive: boolean;
}

export interface TerritoryEdgeCreatePayload {
	source_territory_id: number;
	target_territory_id: number;
	movement_cost: number;
}

export interface TerritoryUpdatePayload {
	food?: number;
	temperature?: number;
	food_regen_per_tick?: number;
	food_capacity?: number;
	x?: number | null;
	y?: number | null;
}

export interface TerritoryEdgeState {
	id: number;
	source_id: string;
	target_id: string;
	movement_cost: number;
}

export interface GenomeTemplateRead {
	id: number;
	user_id: number;
	name: string;
	description: string | null;
	is_builtin: boolean;
	species_group: string;
	created_at: string;
	updated_at: string;
}

export interface GenomeTemplateCreatePayload {
	name: string;
	description?: string | null;
	species_group: string;
}

export interface GenomeTemplateGene {
	id: number;
	genome_template_id: number;
	effect_type: string;
	name: string;
	chromosome_id: string;
	position: number;
	default_active: boolean;
	threshold: number;
	x?: number | null;
	y?: number | null;
}

export interface GenomeTemplateGeneCreatePayload {
	effect_type: string;
	name: string;
	chromosome_id: string;
	position: number;
	default_active: boolean;
	threshold: number;
}

export interface GenomeTemplateEdge {
	id: number;
	genome_template_id: number;
	source_gene_id: number;
	target_gene_id: number;
	weight: number;
}

export interface GenomeTemplateEdgeCreatePayload {
	source_gene_id: number;
	target_gene_id: number;
	weight: number;
}

export interface GenomeTemplateGeneState {
	id: number;
	genome_template_id: number;
	effect_type: string;
	is_active: boolean;
}

export interface GenomeTemplateDetails {
	template: GenomeTemplateRead;
	genes: GenomeTemplateGene[];
	edges: GenomeTemplateEdge[];
	gene_states: GenomeTemplateGeneState[];
}

export type SimulationPreset =
	| "base_demo"
	| "food_scarcity"
	| "cold_climate"
	| "predator_dominance"
	| "high_density"
	| "social_tolerance";

export interface SimulationPresetCreatePayload {
	preset: SimulationPreset;
	name?: string | null;
}

export interface MetricsHistoryPoint {
	tick: number;
	alive_population: number;
	avg_hunger_alive: number;
	avg_hp_alive: number;
	avg_hunt_cooldown_alive: number;
	successful_hunts: number;
	births_count: number;
	deaths_count: number;
	population_by_species_group: Record<string, number>;
	occupancy_by_territory: Record<string, number>;
	action_counts: Record<string, number>;
	deaths_by_reason: Record<string, number>;
}