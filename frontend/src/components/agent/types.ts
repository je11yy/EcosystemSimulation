import type { Gene } from "../gene/types";

export type Agent = {
    id: number;
    is_alive: boolean;

    sex: string;
    genome: Gene[];

    territory_id: number;
    genome_id: number | null;

    hunger: number;
    hp: number;

    strength: number;
    defense: number;
    temp_pref: number;

    satisfaction: number;

    pregnant: boolean;
	ticks_to_birth: number | null;
}
