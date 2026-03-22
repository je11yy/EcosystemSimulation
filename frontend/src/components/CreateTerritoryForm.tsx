import { useState } from "react";

type Props = {
  onSubmit: (payload: {
    food: number;
    temperature: number;
    food_regen_per_tick: number;
    food_capacity: number;
    x?: number | null;
    y?: number | null;
  }) => void;
  isBusy?: boolean;
};

export function CreateTerritoryForm({ onSubmit, isBusy = false }: Props) {
  const [food, setFood] = useState(5);
  const [temperature, setTemperature] = useState(20);
  const [regen, setRegen] = useState(0.5);
  const [capacity, setCapacity] = useState(10);
  const [x, setX] = useState("");
  const [y, setY] = useState("");

  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 16,
        background: "#fff",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Новая территория</h3>

      <div style={{ display: "grid", gap: 8 }}>
        <input type="number" value={food} onChange={(e) => setFood(Number(e.target.value))} placeholder="Food" />
        <input type="number" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} placeholder="Temperature" />
        <input type="number" value={regen} onChange={(e) => setRegen(Number(e.target.value))} placeholder="Food regen" />
        <input type="number" value={capacity} onChange={(e) => setCapacity(Number(e.target.value))} placeholder="Food capacity" />
        <input value={x} onChange={(e) => setX(e.target.value)} placeholder="x (optional)" />
        <input value={y} onChange={(e) => setY(e.target.value)} placeholder="y (optional)" />

        <button
          disabled={isBusy}
          onClick={() =>
            onSubmit({
              food,
              temperature,
              food_regen_per_tick: regen,
              food_capacity: capacity,
              x: x.trim() === "" ? null : Number(x),
              y: y.trim() === "" ? null : Number(y),
            })
          }
        >
          Создать территорию
        </button>
      </div>
    </div>
  );
}