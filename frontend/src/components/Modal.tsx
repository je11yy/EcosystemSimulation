import type { ReactNode } from "react";

interface ModalProps {
    title: string;
    onClose: () => void;
    children: ReactNode;
}

export function Modal({ title, onClose, children }: ModalProps) {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h2>{title}</h2>
                {children}
                <button onClick={onClose}>Close</button>
            </div>
        </div>
    );
};