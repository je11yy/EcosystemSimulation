// forms/territory.tsx
import { useState } from "react";
import { useTranslation } from "react-i18next";

interface NewTerritoryProps {
    onCreate: (food: number, temperature: number, food_regen_per_tick: number, food_capacity: number) => void;
}

export function NewTerritory({ onCreate }: NewTerritoryProps) {
    const { t } = useTranslation();
    const [food, setFood] = useState<number>(0);
    const [temperature, setTemperature] = useState<number>(20);
    const [foodRegenPerTick, setFoodRegenPerTick] = useState<number>(1);
    const [foodCapacity, setFoodCapacity] = useState<number>(100);

    const handleSubmit = () => {
        onCreate(food, temperature, foodRegenPerTick, foodCapacity);
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
            <button onClick={handleSubmit}>{t('create')}</button>
        </div>
    );
};