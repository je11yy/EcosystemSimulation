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
        <div>
            <h3>{t('id')}: {territory.id}</h3>
            <p>{t('food')}: {territory.food}</p>
            <p>{t('temperature')}: {territory.temperature}</p>
            <p>{t('food_regen_per_tick')}: {territory.food_regen_per_tick}</p>
            <p>{t('food_capacity')}: {territory.food_capacity}</p>
        </div>
    );
};