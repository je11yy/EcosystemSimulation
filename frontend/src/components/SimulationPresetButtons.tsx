import { useState } from "react";
import { createSimulationFromPreset } from "../api/simulations";
import type { SimulationPreset } from "../api/types";

type Props = {
  userId: number;
  onCreated?: () => Promise<void> | void;
};

const PRESETS: Array<{ key: SimulationPreset; label: string }> = [
  { key: "base_demo", label: "Базовый" },
  { key: "food_scarcity", label: "Дефицит пищи" },
  { key: "cold_climate", label: "Холодный климат" },
  { key: "predator_dominance", label: "Доминирование хищников" },
  { key: "high_density", label: "Высокая плотность" },
  { key: "social_tolerance", label: "Социальная терпимость" },
];

export default function SimulationPresetButtons({ userId, onCreated }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreatePreset(preset: SimulationPreset) {
    try {
      setIsSubmitting(true);
      setError(null);

      await createSimulationFromPreset(userId, {
        preset,
      });

      if (onCreated) {
        await onCreated();
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Не удалось создать preset-сценарий.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section style={{ marginBottom: 24 }}>
      <h3 style={{ marginBottom: 12 }}>Создать сценарий эксперимента</h3>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {PRESETS.map((preset) => (
          <button
            key={preset.key}
            type="button"
            onClick={() => void handleCreatePreset(preset.key)}
            disabled={isSubmitting}
            style={{
              padding: "8px 12px",
              cursor: isSubmitting ? "not-allowed" : "pointer",
            }}
          >
            {preset.label}
          </button>
        ))}
      </div>

      {error ? (
        <p style={{ marginTop: 12, color: "crimson" }}>{error}</p>
      ) : null}
    </section>
  );
}