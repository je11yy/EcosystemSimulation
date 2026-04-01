import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	createSimulation,
	createSimulationFromPreset,
	getSimulations,
} from "../api/simulations";
import type { SimulationPreset } from "../api/types";

const USER_ID = 1;

const SIMULATION_PRESETS: Array<{
	key: SimulationPreset;
	label: string;
}> = [
		{ key: "base_demo", label: "Базовый" },
		{ key: "food_scarcity", label: "Дефицит пищи" },
		{ key: "cold_climate", label: "Холодный климат" },
		{ key: "predator_dominance", label: "Доминирование хищников" },
		{ key: "high_density", label: "Высокая плотность" },
		{ key: "social_tolerance", label: "Социальная терпимость" },
	];

export function SimulationsPage() {
	const queryClient = useQueryClient();
	const [name, setName] = useState("");

	const simulationsQuery = useQuery({
		queryKey: ["simulations", USER_ID],
		queryFn: () => getSimulations(USER_ID),
	});

	const createMutation = useMutation({
		mutationFn: (simulationName: string) => createSimulation(USER_ID, simulationName),
		onSuccess: () => {
			setName("");
			queryClient.invalidateQueries({ queryKey: ["simulations", USER_ID] });
		},
	});

	const createPresetMutation = useMutation({
		mutationFn: (preset: SimulationPreset) =>
			createSimulationFromPreset(USER_ID, { preset }),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["simulations", USER_ID] });
		},
	});

	return (
		<div style={{ padding: 24 }}>
			<div style={{ display: "flex", gap: 16, marginBottom: 16 }}>
				<Link to="/genome-templates">Перейти к шаблонам генома</Link>
				<Link to="/simulations/compare">Сравнение сценариев</Link>
			</div>

			<h1>Симуляции</h1>

			<div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
				<input
					value={name}
					onChange={(e) => setName(e.target.value)}
					placeholder="Название симуляции"
				/>
				<button
					onClick={() => {
						if (!name.trim()) return;
						createMutation.mutate(name.trim());
					}}
				>
					Создать
				</button>
			</div>

			<div style={{ marginBottom: 24 }}>
				<p style={{ marginBottom: 8 }}>Быстрое создание сценария:</p>
				<div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
					{SIMULATION_PRESETS.map((preset) => (
						<button
							key={preset.key}
							onClick={() => {
								createPresetMutation.mutate(preset.key);
							}}
							disabled={createPresetMutation.isPending}
						>
							{preset.label}
						</button>
					))}
				</div>
			</div>

			{simulationsQuery.isLoading && <p>Загрузка...</p>}
			{simulationsQuery.isError && <p>Ошибка загрузки симуляций</p>}

			<ul>
				{simulationsQuery.data?.map((simulation) => (
					<li key={simulation.id}>
						<Link to={`/simulations/${simulation.id}`}>{simulation.name}</Link>{" "}
						— статус: {simulation.status}, tick: {simulation.tick}
					</li>
				))}
			</ul>
		</div>
	);
}