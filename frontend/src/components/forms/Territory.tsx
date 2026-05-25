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

    const [food, setFood] = useState<string>(
        initialValue?.food !== undefined ? String(initialValue.food) : "",
    );

    const [temperature, setTemperature] = useState<string>(
        initialValue?.temperature !== undefined ? String(initialValue.temperature) : "",
    );

    const [foodRegenPerTick, setFoodRegenPerTick] = useState<string>(
        initialValue?.food_regen_per_tick !== undefined
            ? String(initialValue.food_regen_per_tick)
            : "",
    );

    const [foodCapacity, setFoodCapacity] = useState<string>(
        initialValue?.food_capacity !== undefined ? String(initialValue.food_capacity) : "",
    );

    const handleSubmit = () => {
        const foodValue = food === "" ? 0 : Number(food);
        const temperatureValue = temperature === "" ? 20 : Number(temperature);
        const foodRegenPerTickValue = foodRegenPerTick === "" ? 1 : Number(foodRegenPerTick);
        const foodCapacityValue = foodCapacity === "" ? 100 : Number(foodCapacity);

        onCreate({
            food: foodValue,
            food_capacity: Math.max(foodCapacityValue, foodValue),
            food_regen_per_tick: foodRegenPerTickValue,
            temperature: temperatureValue,
            position: { x: 100, y: 100 },
        });
    };

    return (
        <div>
            <div>
                <label htmlFor="food">{t("food")}</label>
                <input
                    className="modal-input"
                    type="number"
                    id="food"
                    value={food}
                    onChange={(e) => setFood(e.target.value)}
                    placeholder="65"
                />
            </div>

            <div>
                <label htmlFor="temperature">{t("temperature")}</label>
                <input
                    className="modal-input"
                    type="number"
                    id="temperature"
                    value={temperature}
                    onChange={(e) => setTemperature(e.target.value)}
                    placeholder="25"
                />
            </div>

            <div>
                <label htmlFor="foodRegenPerTick">{t("food_regen_per_tick")}</label>
                <input
                    className="modal-input"
                    type="number"
                    id="foodRegenPerTick"
                    value={foodRegenPerTick}
                    onChange={(e) => setFoodRegenPerTick(e.target.value)}
                    placeholder="5"
                />
            </div>

            <div>
                <label htmlFor="foodCapacity">{t("food_capacity")}</label>
                <input
                    className="modal-input"
                    type="number"
                    id="foodCapacity"
                    value={foodCapacity}
                    onChange={(e) => setFoodCapacity(e.target.value)}
                    placeholder="100"
                />
            </div>

            <button className="modal-button" onClick={handleSubmit}>{submitLabel ?? t("create")}</button>
        </div>
    );
}