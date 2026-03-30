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

type DecisionView = {
  tick: number;
  agent_id: string;
  chosen: {
    type: string;
    to_territory: string | null;
    partner_id: string | null;
    target_id: string | null;
    tag: string | null;
  };
};

type AppliedResultView = {
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
};

type DeathView = {
  agent_id: string;
  reason: string;
  tick: number;
};

type BirthView = {
  parent_id: string;
  child_id: string;
  tick: number;
};

type FightView = {
  territory_id: string;
  winner_id: string;
  loser_id: string;
  loser_hp_loss: number;
};

type HuntView = {
  territory_id: string;
  hunter_id: string;
  target_id: string;
  success: boolean;
  damage_to_target: number;
  damage_to_hunter: number;
  target_died: boolean;
  hunter_died: boolean;
  hunger_restored: number;
};

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

export type LastStepResult = {
  tick: number;
  decisions: DecisionView[];
  applied_results: AppliedResultView[];
  deaths: DeathView[];
  births: BirthView[];
  fights: FightView[];
  hunts: HuntView[];
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
  metrics_history: MetricsHistoryPoint[];
};

type Props = {
  stepResult: LastStepResult | null;
};

function MetricsCharts({
  history,
}: {
  history: MetricsHistoryPoint[];
}) {
  if (history.length === 0) {
    return <p>История метрик пока пуста.</p>;
  }

  const speciesGroups = Array.from(
    new Set(
      history.flatMap((point) => Object.keys(point.population_by_species_group))
    )
  );

  const speciesChartData = history.map((point) => {
    const row: Record<string, number> = { tick: point.tick };
    for (const speciesGroup of speciesGroups) {
      row[speciesGroup] = point.population_by_species_group[speciesGroup] ?? 0;
    }
    return row;
  });

  return (
    <section>
      <h4 style={{ marginBottom: 12 }}>Графики динамики</h4>

      <div style={{ display: "grid", gap: 16 }}>
        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="tick" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="alive_population" name="alive population" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="tick" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="avg_hunger_alive" name="avg hunger alive" dot={false} />
              <Line type="monotone" dataKey="avg_hp_alive" name="avg hp alive" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="tick" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="avg_hunt_cooldown_alive"
                name="avg hunt cooldown alive"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="successful_hunts"
                name="successful hunts"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <BarChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="tick" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="births_count" name="births" />
              <Bar dataKey="deaths_count" name="deaths" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {speciesGroups.length > 0 && (
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={speciesChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="tick" />
                <YAxis />
                <Tooltip />
                <Legend />
                {speciesGroups.map((speciesGroup) => (
                  <Line
                    key={speciesGroup}
                    type="monotone"
                    dataKey={speciesGroup}
                    name={speciesGroup}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </section>
  );
}

export default function LastStepPanel({ stepResult }: Props) {
  if (!stepResult) {
    return (
      <div>
        <h3>Последний шаг</h3>
        <p>Шагов пока нет.</p>
      </div>
    );
  }

  return (
    <div>
      <h3>Последний шаг</h3>
      <p>tick шага: {stepResult.tick}</p>

      <section>
        <h4 style={{ marginBottom: 8 }}>Метрики шага</h4>
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          <li>alive population: {stepResult.metrics.alive_population}</li>
          <li>avg hunger alive: {stepResult.metrics.avg_hunger_alive.toFixed(2)}</li>
          <li>avg hp alive: {stepResult.metrics.avg_hp_alive.toFixed(2)}</li>
          <li>
            avg hunt cooldown alive:{" "}
            {stepResult.metrics.avg_hunt_cooldown_alive.toFixed(2)}
          </li>
          <li>successful hunts: {stepResult.metrics.successful_hunts}</li>
          <li>births count: {stepResult.metrics.births_count}</li>
          <li>deaths count: {stepResult.metrics.deaths_count}</li>
        </ul>
      </section>

      <MetricsCharts history={stepResult.metrics_history} />

      <section>
        <h4 style={{ marginBottom: 8 }}>Решения</h4>
        {stepResult.decisions.length === 0 ? (
          <p>Решений не было.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {stepResult.decisions.map((decision, index) => (
              <li key={`${decision.agent_id}-${index}`}>
                агент #{decision.agent_id} → {decision.chosen.type}
                {decision.chosen.to_territory
                  ? ` (to ${decision.chosen.to_territory})`
                  : ""}
                {decision.chosen.partner_id
                  ? ` (partner ${decision.chosen.partner_id})`
                  : ""}
                {decision.chosen.target_id
                  ? ` (target ${decision.chosen.target_id})`
                  : ""}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 style={{ marginBottom: 8 }}>Применение действий</h4>
        {stepResult.applied_results.length === 0 ? (
          <p>Действий не было.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {stepResult.applied_results.map((result, index) => (
              <li key={`${result.agent_id}-${result.action_type}-${index}`}>
                агент #{result.agent_id} → {result.action_type} | success:{" "}
                {String(result.success)}
                {result.reason ? ` | reason: ${result.reason}` : ""}
                {result.consumed_food ? " | ate food" : ""}
                {result.created_pregnancy ? " | pregnancy created" : ""}
                {result.hp_loss > 0 ? ` | hp loss: ${result.hp_loss}` : ""}
                {result.hunger_restored > 0
                  ? ` | hunger restored: ${result.hunger_restored}`
                  : ""}
                {result.hunger_delta !== 0
                  ? ` | hunger delta: ${result.hunger_delta}`
                  : ""}
                {result.target_id ? ` | target: ${result.target_id}` : ""}
                {result.damage_to_target > 0
                  ? ` | damage to target: ${result.damage_to_target}`
                  : ""}
                {result.target_died ? " | target died" : ""}
                {result.hunter_died ? " | hunter died" : ""}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 style={{ marginBottom: 8 }}>Драки</h4>
        {stepResult.fights.length === 0 ? (
          <p>Драк не было.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {stepResult.fights.map((fight, index) => (
              <li key={`${fight.winner_id}-${fight.loser_id}-${index}`}>
                territory #{fight.territory_id}: победитель #{fight.winner_id},
                проигравший #{fight.loser_id}, урон {fight.loser_hp_loss}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 style={{ marginBottom: 8 }}>Охота</h4>
        {stepResult.hunts.length === 0 ? (
          <p>Охоты не было.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {stepResult.hunts.map((hunt, index) => (
              <li key={`${hunt.hunter_id}-${hunt.target_id}-${index}`}>
                territory #{hunt.territory_id}: охотник #{hunt.hunter_id} → цель #
                {hunt.target_id} | success: {String(hunt.success)}
                {hunt.damage_to_target > 0
                  ? ` | damage to target: ${hunt.damage_to_target}`
                  : ""}
                {hunt.damage_to_hunter > 0
                  ? ` | damage to hunter: ${hunt.damage_to_hunter}`
                  : ""}
                {hunt.hunger_restored > 0
                  ? ` | hunger restored: ${hunt.hunger_restored}`
                  : ""}
                {hunt.target_died ? " | target died" : ""}
                {hunt.hunter_died ? " | hunter died" : ""}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 style={{ marginBottom: 8 }}>Рождения</h4>
        {stepResult.births.length === 0 ? (
          <p>Рождений не было.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {stepResult.births.map((birth, index) => (
              <li key={`${birth.child_id}-${index}`}>
                ребёнок #{birth.child_id}, мать #{birth.parent_id}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 style={{ marginBottom: 8 }}>Смерти</h4>
        {stepResult.deaths.length === 0 ? (
          <p>Смертей не было.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {stepResult.deaths.map((death, index) => (
              <li key={`${death.agent_id}-${index}`}>
                агент #{death.agent_id} умер, причина: {death.reason}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}