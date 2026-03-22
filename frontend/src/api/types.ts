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
  gene_id: string;
  is_active: boolean;
}

export interface Gene {
  id: string;
  name: string;
  chromosome_id: string;
  position: number;
  default_active: boolean;
  threshold: number;
}

export interface GeneEdge {
  source_gene_id: string;
  target_gene_id: string;
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