import { useTranslation } from "react-i18next";

type Props = {
    onStart: () => void;
    onStep: () => void;
    onRun: () => void;
    onPause: () => void;
    onStop: () => void;
    isBusy?: boolean;
};

export function Controls({
    onStart,
    onStep,
    onRun,
    onPause,
    onStop,
    isBusy = false,
}: Props) {
    const { t } = useTranslation();

    return (
        <div
            style={{
                display: "flex",
                flexWrap: "wrap",
                gap: 8,
                marginBottom: 16,
            }}
        >
            <button
                type="button"
                onClick={onStart}
                disabled={isBusy}
                aria-label={t("start")}
                title={t("start")}
            >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M5 3.5L12.5 8L5 12.5V3.5Z" />
                </svg>
                <span>{t("start")}</span>
            </button>
            <button
                type="button"
                onClick={onStep}
                disabled={isBusy}
                aria-label={t("step")}
                title={t("step")}
            >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M4 3.5L9.5 8L4 12.5V3.5Z" />
                    <path d="M10 3.5L15.5 8L10 12.5V3.5Z" />
                    <rect x="1" y="3" width="2" height="10" rx="0.5" />
                </svg>
                <span>{t("step")}</span>
            </button>
            <button
                type="button"
                onClick={onRun}
                disabled={isBusy}
                aria-label={t("run")}
                title={t("run")}
            >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M3 3.5L8.5 8L3 12.5V3.5Z" />
                    <path d="M8 3.5L13.5 8L8 12.5V3.5Z" />
                </svg>
                <span>{t("run")}</span>
            </button>
            <button
                type="button"
                onClick={onPause}
                disabled={isBusy}
                aria-label={t("pause")}
                title={t("pause")}
            >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <rect x="3" y="3" width="3" height="10" rx="0.75" />
                    <rect x="10" y="3" width="3" height="10" rx="0.75" />
                </svg>
                <span>{t("pause")}</span>
            </button>
            <button
                type="button"
                onClick={onStop}
                disabled={isBusy}
                aria-label={t("stop")}
                title={t("stop")}
            >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <rect x="3" y="3" width="10" height="10" rx="1" />
                </svg>
                <span>{t("stop")}</span>
            </button>
        </div>
    );
}
