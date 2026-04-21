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

type ChartPoint = {
    tick: number;
    alive_population: number;
    avg_hunger: number;
    avg_satisfaction: number;
    consumed_food: number;
};

export function MetricsCharts({ logs }: Props) {
    const { t } = useTranslation();
    const data = useMemo<ChartPoint[]>(
        () =>
            logs.map((log) => ({
                tick: log.tick,
                alive_population: log.metrics.alive_population,
                avg_hunger: Number(log.metrics.avg_hunger.toFixed(2)),
                avg_satisfaction: Number((log.metrics.avg_satisfaction ?? 0).toFixed(2)),
                consumed_food: log.metrics.consumed_food,
            })),
        [logs],
    );

    return (
        <section className="metrics-charts">
            <div className="metrics-charts__header">
                <h2>{t("metrics_history")}</h2>
                <span>{logs.length} {t("ticks_short")}</span>
            </div>
            {data.length < 2 ? (
                <p className="form-hint">{t("not_enough_metrics_history")}</p>
            ) : (
                <div className="metrics-charts__grid">
                    <MetricLineChart
                        data={data}
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
                        data={data}
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
    data: ChartPoint[];
    title: string;
    lines: Array<{ key: keyof ChartPoint; name: string; color: string }>;
}) {
    return (
        <div className="metrics-chart">
            <h3>{title}</h3>
            <ResponsiveContainer width="100%" height={240}>
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
