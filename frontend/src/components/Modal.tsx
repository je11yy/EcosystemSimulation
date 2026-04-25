import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

interface ModalProps {
    title: string;
    onClose: () => void;
    children: ReactNode;
}

export function Modal({ title, onClose, children }: ModalProps) {
    const { t } = useTranslation();

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{title}</h2>
                    <button className="icon-button" type="button" onClick={onClose} aria-label={t("close")}>
                        &times;
                    </button>
                </div>
                <div className="modal-body">
                    {children}
                </div>
            </div>
        </div>
    );
};
