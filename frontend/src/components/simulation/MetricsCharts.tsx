import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import type { Log } from "src/api/types";

type Props = {
    logs: Log[];
};

type BaseChartPoint = {
    tick: number;
    alive_population: number;
    avg_hunger: number;
    avg_satisfaction: number;
    consumed_food: number;
    eat: number;
    move: number;
    mate: number;
    rest: number;
    hunt: number;
    deaths: number;
    births: number;
    successful_hunts: number;
    unsuccessful_hunts: number;
};

type GenericChartPoint = BaseChartPoint & Record<string, number>;

const TERRITORY_COLORS = [
    "#166534",
    "#0f766e",
    "#15803d",
    "#b45309",
    "#7c3aed",
    "#dc2626",
    "#2563eb",
    "#c2410c",
    "#0891b2",
    "#9333ea",
];

export function MetricsCharts({ logs }: Props) {
    const { t } = useTranslation();

    const baseData = useMemo<GenericChartPoint[]>(
        () =>
            logs.map((log) => ({
                tick: log.tick + 1,
                alive_population: log.metrics.alive_population,
                avg_hunger: Number(log.metrics.avg_hunger.toFixed(2)),
                avg_satisfaction: Number((log.metrics.avg_satisfaction ?? 0).toFixed(2)),
                consumed_food: log.metrics.consumed_food,
                eat: log.step_result.eat,
                move: log.step_result.move,
                mate: log.step_result.mate,
                rest: log.step_result.rest,
                hunt: log.step_result.hunt,
                deaths: log.step_result.deaths,
                births: log.step_result.births,
                successful_hunts: log.metrics.successful_hunts,
                unsuccessful_hunts: log.metrics.unsuccessful_hunts,
            })),
        [logs],
    );

    const territoryIds = useMemo(() => {
        const ids = new Set<number>();
        for (const log of logs) {
            for (const territoryId of Object.keys(log.metrics.occupancy_by_territory ?? {})) {
                ids.add(Number(territoryId));
            }
        }
        return [...ids].sort((left, right) => left - right);
    }, [logs]);

    const territoryDistributionData = useMemo<GenericChartPoint[]>(
        () =>
            logs.map((log) => {
                const point: GenericChartPoint = {
                    tick: log.tick + 1,
                    alive_population: 0,
                    avg_hunger: 0,
                    avg_satisfaction: 0,
                    consumed_food: 0,
                    eat: 0,
                    move: 0,
                    mate: 0,
                    rest: 0,
                    hunt: 0,
                    deaths: 0,
                    births: 0,
                    successful_hunts: 0,
                    unsuccessful_hunts: 0,
                };

                for (const territoryId of territoryIds) {
                    point[`territory_${territoryId}`] =
                        log.metrics.occupancy_by_territory?.[territoryId] ?? 0;
                }

                return point;
            }),
        [logs, territoryIds],
    );

    return (
        <section className="metrics-charts">
            <div className="metrics-charts__header">
                <h2>{t("metrics_history")}</h2>
            </div>
            {baseData.length < 2 ? (
                <p className="form-hint">{t("not_enough_metrics_history")}</p>
            ) : (
                <div className="metrics-charts__grid">
                    <MetricLineChart
                        data={baseData}
                        title={t("population_and_resources")}
                        lines={[
                            {
                                key: "alive_population",
                                name: t("alive_population"),
                                color: "#166534",
                            },
                            {
                                key: "consumed_food",
                                name: t("consumed_food"),
                                color: "#0f766e",
                            },
                        ]}
                    />
                    <MetricLineChart
                        data={baseData}
                        title={t("agent_condition")}
                        lines={[
                            {
                                key: "avg_hunger",
                                name: t("avg_hunger"),
                                color: "#b45309",
                            },
                            {
                                key: "avg_satisfaction",
                                name: t("avg_satisfaction"),
                                color: "#15803d",
                            },
                        ]}
                    />
                    <MetricLineChart
                        data={baseData}
                        title={t("agent_actions_history")}
                        lines={[
                            {
                                key: "eat",
                                name: t("eat"),
                                color: "#166534",
                            },
                            {
                                key: "move",
                                name: t("move"),
                                color: "#2563eb",
                            },
                            {
                                key: "mate",
                                name: t("mate"),
                                color: "#9333ea",
                            },
                            {
                                key: "rest",
                                name: t("rest"),
                                color: "#b45309",
                            },
                            {
                                key: "hunt",
                                name: t("hunt"),
                                color: "#b91c1c",
                            },
                        ]}
                    />
                    <MetricLineChart
                        data={baseData}
                        title={t("births_and_deaths")}
                        lines={[
                            {
                                key: "deaths",
                                name: t("mortality"),
                                color: "#7f1d1d",
                            },
                            {
                                key: "births",
                                name: t("births"),
                                color: "#9333ea",
                            },
                        ]}
                    />
                    <MetricLineChart
                        data={baseData}
                        title={t("hunting_activity")}
                        lines={[
                            {
                                key: "successful_hunts",
                                name: t("successful_hunts"),
                                color: "#166534",
                            },
                            {
                                key: "unsuccessful_hunts",
                                name: t("unsuccessful_hunts"),
                                color: "#b91c1c",
                            },
                        ]}
                    />
                    {territoryIds.length > 0 && (
                        <MetricLineChart
                            data={territoryDistributionData}
                            title={t("territory_distribution")}
                            lines={territoryIds.map((territoryId, index) => ({
                                key: `territory_${territoryId}`,
                                name: `${t("territory")} ${territoryId}`,
                                color: TERRITORY_COLORS[index % TERRITORY_COLORS.length],
                            }))}
                        />
                    )}
                </div>
            )}
        </section>
    );
}

function MetricLineChart({
    data,
    title,
    lines,
}: {
    data: GenericChartPoint[];
    title: string;
    lines: Array<{ key: string; name: string; color: string }>;
}) {
    return (
        <div className="metrics-chart">
            <h3>{title}</h3>
            <ResponsiveContainer width="100%" height={260}>
                <LineChart data={data} margin={{ top: 10, right: 18, bottom: 0, left: 0 }}>
                    <CartesianGrid stroke="#d8e2d8" strokeDasharray="4 4" />
                    <XAxis dataKey="tick" tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} width={36} />
                    <Tooltip />
                    {lines.map((line) => (
                        <Line
                            key={line.key}
                            type="monotone"
                            dataKey={line.key}
                            name={line.name}
                            stroke={line.color}
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
