// forms/territory.tsx
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { TerritoryCreate } from "src/api/types";

interface NewTerritoryProps {
    onCreate: (territory: TerritoryCreate) => void;
    initialValue?: TerritoryCreate;
    submitLabel?: string;
}

export function NewTerritory({ onCreate, initialValue, submitLabel }: NewTerritoryProps) {
    const { t } = useTranslation();
    const [food, setFood] = useState<number>(initialValue?.food ?? 0);
    const [temperature, setTemperature] = useState<number>(initialValue?.temperature ?? 20);
    const [foodRegenPerTick, setFoodRegenPerTick] = useState<number>(
        initialValue?.food_regen_per_tick ?? 1,
    );
    const [foodCapacity, setFoodCapacity] = useState<number>(initialValue?.food_capacity ?? 100);
    const [x, setX] = useState<number>(initialValue?.position.x ?? 100);
    const [y, setY] = useState<number>(initialValue?.position.y ?? 100);

    const handleSubmit = () => {
        onCreate({
            food,
            food_capacity: Math.max(foodCapacity, food),
            food_regen_per_tick: foodRegenPerTick,
            temperature,
            position: { x, y },
        });
    };

    return (
        <div>
            <div>
                <label htmlFor="food">{t('food')}:</label>
                <input type="number" id="food" value={food} onChange={(e) => setFood(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="temperature">{t('temperature')}:</label>
                <input type="number" id="temperature" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="foodRegenPerTick">{t('food_regen_per_tick')}:</label>
                <input type="number" id="foodRegenPerTick" value={foodRegenPerTick} onChange={(e) => setFoodRegenPerTick(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="foodCapacity">{t('food_capacity')}:</label>
                <input type="number" id="foodCapacity" value={foodCapacity} onChange={(e) => setFoodCapacity(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="territoryX">X:</label>
                <input type="number" id="territoryX" value={x} onChange={(e) => setX(Number(e.target.value))} />
            </div>
            <div>
                <label htmlFor="territoryY">Y:</label>
                <input type="number" id="territoryY" value={y} onChange={(e) => setY(Number(e.target.value))} />
            </div>
            <button onClick={handleSubmit}>{submitLabel ?? t('create')}</button>
        </div>
    );
};
