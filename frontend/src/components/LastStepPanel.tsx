type DecisionView = {
  tick: number;
  agent_id: string;
  chosen: {
    type: string;
    to_territory: string | null;
    partner_id: string | null;
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

export type LastStepResult = {
  tick: number;
  decisions: DecisionView[];
  applied_results: AppliedResultView[];
  deaths: DeathView[];
  births: BirthView[];
  fights: FightView[];
};

type Props = {
  stepResult: LastStepResult | null;
};

export function LastStepPanel({ stepResult }: Props) {
  if (!stepResult) {
    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "#fff",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Последний шаг</h3>
        <p style={{ marginBottom: 0 }}>Пока нет данных о последнем ручном шаге.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Последний шаг</h3>
      <p>
        tick шага: <b>{stepResult.tick}</b>
      </p>

      <div style={{ display: "grid", gap: 16 }}>
        <section>
          <h4 style={{ marginBottom: 8 }}>Решения</h4>
          {stepResult.decisions.length === 0 ? (
            <p>Нет решений.</p>
          ) : (
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {stepResult.decisions.map((decision, index) => (
                <li key={`${decision.agent_id}-${index}`}>
                  агент #{decision.agent_id} → {decision.chosen.type}
                  {decision.chosen.to_territory ? ` (to ${decision.chosen.to_territory})` : ""}
                  {decision.chosen.partner_id ? ` (partner ${decision.chosen.partner_id})` : ""}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <h4 style={{ marginBottom: 8 }}>Применение действий</h4>
          {stepResult.applied_results.length === 0 ? (
            <p>Нет результатов применения.</p>
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
                  territory #{fight.territory_id}: победитель #{fight.winner_id}, проигравший #
                  {fight.loser_id}, урон {fight.loser_hp_loss}
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
                  родитель #{birth.parent_id} → ребёнок #{birth.child_id}
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
    </div>
  );
}