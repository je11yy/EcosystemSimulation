import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQueries, useQuery } from "@tanstack/react-query";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    BarChart,
    Bar,
} from "recharts";
import { downloadBlob, exportSimulationMetricsHistory, getSimulations, getSimulationState } from "../api/simulations";

const USER_ID = 1;

type MetricsHistoryPoint = {
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
};

type LoadedSimulationSeries = {
    simulationId: number;
    simulationName: string;
    history: MetricsHistoryPoint[];
};

function buildMergedHistory(
    seriesList: LoadedSimulationSeries[],
    valueKey:
        | "alive_population"
        | "avg_hunger_alive"
        | "avg_hp_alive"
        | "avg_hunt_cooldown_alive"
        | "successful_hunts"
        | "births_count"
        | "deaths_count"
) {
    const ticks = Array.from(
        new Set(seriesList.flatMap((series) => series.history.map((point) => point.tick)))
    ).sort((a, b) => a - b);

    return ticks.map((tick) => {
        const row: Record<string, number | string> = { tick };

        for (const series of seriesList) {
            const point = series.history.find((item) => item.tick === tick);
            row[series.simulationName] = point ? point[valueKey] : 0;
        }

        return row;
    });
}

export function SimulationComparisonPage() {
    const [selectedIds, setSelectedIds] = useState<number[]>([]);

    const simulationsQuery = useQuery({
        queryKey: ["simulations", USER_ID],
        queryFn: () => getSimulations(USER_ID),
    });

    const selectedSimulations = useMemo(() => {
        if (!simulationsQuery.data) {
            return [];
        }

        return simulationsQuery.data.filter((simulation) =>
            selectedIds.includes(simulation.id)
        );
    }, [simulationsQuery.data, selectedIds]);

    const stateQueries = useQueries({
        queries: selectedSimulations.map((simulation) => ({
            queryKey: ["simulation-state", simulation.id],
            queryFn: () => getSimulationState(simulation.id),
        })),
    });

    const comparisonSeries = useMemo<LoadedSimulationSeries[]>(() => {
        return selectedSimulations.flatMap((simulation, index) => {
            const query = stateQueries[index];
            const history = query?.data?.metrics_history ?? [];

            if (history.length === 0) {
                return [];
            }

            return [
                {
                    simulationId: simulation.id,
                    simulationName: simulation.name,
                    history,
                },
            ];
        });
    }, [selectedSimulations, stateQueries]);

    const alivePopulationData = useMemo(
        () => buildMergedHistory(comparisonSeries, "alive_population"),
        [comparisonSeries]
    );

    const avgHungerData = useMemo(
        () => buildMergedHistory(comparisonSeries, "avg_hunger_alive"),
        [comparisonSeries]
    );

    const avgHpData = useMemo(
        () => buildMergedHistory(comparisonSeries, "avg_hp_alive"),
        [comparisonSeries]
    );

    const successfulHuntsData = useMemo(
        () => buildMergedHistory(comparisonSeries, "successful_hunts"),
        [comparisonSeries]
    );

    const birthDeathData = useMemo(() => {
        const ticks = Array.from(
            new Set(comparisonSeries.flatMap((series) => series.history.map((point) => point.tick)))
        ).sort((a, b) => a - b);

        return ticks.map((tick) => {
            const row: Record<string, number | string> = { tick };

            for (const series of comparisonSeries) {
                const point = series.history.find((item) => item.tick === tick);
                row[`${series.simulationName} births`] = point ? point.births_count : 0;
                row[`${series.simulationName} deaths`] = point ? point.deaths_count : 0;
            }

            return row;
        });
    }, [comparisonSeries]);

    const toggleSelection = (simulationId: number) => {
        setSelectedIds((prev) => {
            if (prev.includes(simulationId)) {
                return prev.filter((id) => id !== simulationId);
            }

            if (prev.length >= 3) {
                return prev;
            }

            return [...prev, simulationId];
        });
    };

    const handleExport = async (
        simulationId: number,
        simulationName: string,
        format: "csv" | "json"
    ) => {
        const blob = await exportSimulationMetricsHistory(simulationId, USER_ID, format);

        const safeName = simulationName
            .toLowerCase()
            .replaceAll(" ", "_")
            .replaceAll(":", "")
            .replaceAll("/", "_");

        downloadBlob(blob, `${safeName}_metrics_history.${format}`);
    };

    const isLoadingAnyState = stateQueries.some((query) => query.isLoading);
    const isErrorAnyState = stateQueries.some((query) => query.isError);

    return (
        <div style={{ padding: 24 }}>
            <div style={{ display: "flex", gap: 16, marginBottom: 16 }}>
                <Link to="/">Назад к симуляциям</Link>
                <Link to="/genome-templates">Шаблоны генома</Link>
            </div>

            <h1>Сравнение сценариев</h1>

            <p style={{ marginBottom: 16 }}>
                Выбери до трёх симуляций, чтобы сравнить их динамику по метрикам.
            </p>

            {simulationsQuery.isLoading && <p>Загрузка списка симуляций...</p>}
            {simulationsQuery.isError && <p>Ошибка загрузки списка симуляций.</p>}

            {simulationsQuery.data && (
                <div style={{ marginBottom: 24 }}>
                    <h3 style={{ marginBottom: 8 }}>Доступные симуляции</h3>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                        {simulationsQuery.data.map((simulation) => {
                            const isSelected = selectedIds.includes(simulation.id);

                            return (
                                <button
                                    key={simulation.id}
                                    onClick={() => toggleSelection(simulation.id)}
                                    style={{
                                        border: "1px solid #ccc",
                                        padding: "8px 12px",
                                        cursor: "pointer",
                                        fontWeight: isSelected ? 700 : 400,
                                    }}
                                >
                                    {isSelected ? "✓ " : ""}
                                    {simulation.name}
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}

            <div style={{ marginBottom: 24 }}>
                <h3 style={{ marginBottom: 8 }}>Выбрано</h3>
                {selectedSimulations.length === 0 ? (
                    <p>Пока ничего не выбрано.</p>
                ) : (
                    <ul style={{ margin: 0, paddingLeft: 20 }}>
                        {selectedSimulations.map((simulation) => (
                            <li key={simulation.id} style={{ marginBottom: 8 }}>
                                <div>
                                    {simulation.name} (id: {simulation.id})
                                </div>
                                <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                                    <button
                                        onClick={() => handleExport(simulation.id, simulation.name, "csv")}
                                    >
                                        Экспорт CSV
                                    </button>
                                    <button
                                        onClick={() => handleExport(simulation.id, simulation.name, "json")}
                                    >
                                        Экспорт JSON
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {isLoadingAnyState && <p>Загрузка history выбранных симуляций...</p>}
            {isErrorAnyState && <p>Ошибка загрузки состояния одной из симуляций.</p>}

            {comparisonSeries.length > 0 && (
                <div style={{ display: "grid", gap: 24 }}>
                    <section>
                        <h3 style={{ marginBottom: 12 }}>Численность живых агентов</h3>
                        <div style={{ width: "100%", height: 320 }}>
                            <ResponsiveContainer>
                                <LineChart data={alivePopulationData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="tick" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    {comparisonSeries.map((series) => (
                                        <Line
                                            key={series.simulationId}
                                            type="monotone"
                                            dataKey={series.simulationName}
                                            name={series.simulationName}
                                            dot={false}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </section>

                    <section>
                        <h3 style={{ marginBottom: 12 }}>Средний голод живых агентов</h3>
                        <div style={{ width: "100%", height: 320 }}>
                            <ResponsiveContainer>
                                <LineChart data={avgHungerData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="tick" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    {comparisonSeries.map((series) => (
                                        <Line
                                            key={series.simulationId}
                                            type="monotone"
                                            dataKey={series.simulationName}
                                            name={series.simulationName}
                                            dot={false}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </section>

                    <section>
                        <h3 style={{ marginBottom: 12 }}>Средний HP живых агентов</h3>
                        <div style={{ width: "100%", height: 320 }}>
                            <ResponsiveContainer>
                                <LineChart data={avgHpData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="tick" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    {comparisonSeries.map((series) => (
                                        <Line
                                            key={series.simulationId}
                                            type="monotone"
                                            dataKey={series.simulationName}
                                            name={series.simulationName}
                                            dot={false}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </section>

                    <section>
                        <h3 style={{ marginBottom: 12 }}>Успешные охоты</h3>
                        <div style={{ width: "100%", height: 320 }}>
                            <ResponsiveContainer>
                                <LineChart data={successfulHuntsData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="tick" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    {comparisonSeries.map((series) => (
                                        <Line
                                            key={series.simulationId}
                                            type="monotone"
                                            dataKey={series.simulationName}
                                            name={series.simulationName}
                                            dot={false}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </section>

                    <section>
                        <h3 style={{ marginBottom: 12 }}>Рождения и смерти</h3>
                        <div style={{ width: "100%", height: 360 }}>
                            <ResponsiveContainer>
                                <BarChart data={birthDeathData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="tick" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    {comparisonSeries.flatMap((series) => [
                                        <Bar
                                            key={`${series.simulationId}-births`}
                                            dataKey={`${series.simulationName} births`}
                                            name={`${series.simulationName} births`}
                                        />,
                                        <Bar
                                            key={`${series.simulationId}-deaths`}
                                            dataKey={`${series.simulationName} deaths`}
                                            name={`${series.simulationName} deaths`}
                                        />,
                                    ])}
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </section>
                </div>
            )}
        </div>
    );
}