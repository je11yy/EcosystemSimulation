// подробности о территории, отображаемые при клике на нее
import React from "react";
import { useTranslation } from "react-i18next";
import type { Territory } from "./types";

interface Props {
    territory: Territory;
}

export const TerritoryDetails: React.FC<Props> = ({ territory }) => {
    const { t } = useTranslation();
    return (
        <div className="territory-details">
            <p>{t('food')}: {territory.food.toFixed(2)}</p>
            <p>{t('temperature')}: {territory.temperature.toFixed(2)}</p>
            <p>{t('food_regen_per_tick')}: {territory.food_regen_per_tick.toFixed(2)}</p>
            <p>{t('food_capacity')}: {territory.food_capacity.toFixed(2)}</p>
        </div>
    );
};