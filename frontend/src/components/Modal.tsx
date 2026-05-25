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
                    <svg onClick={onClose} className="icon-button" xmlns="http://www.w3.org/2000/svg" version="1.0" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet">
                        <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="#000000" stroke="none">
                            <path d="M95 5106 c-41 -18 -83 -69 -91 -111 -15 -81 -69 -23 1174 -1267 l1167 -1168 -1167 -1168 c-1029 -1029 -1167 -1171 -1173 -1204 -20 -109 73 -203 182 -184 34 7 152 122 1206 1174 l1167 1167 1168 -1167 c1053 -1052 1171 -1167 1205 -1174 110 -19 205 78 182 188 -6 27 -218 244 -1173 1201 l-1167 1167 1167 1168 c1052 1053 1167 1171 1174 1205 19 110 -78 205 -188 182 -27 -6 -244 -218 -1201 -1173 l-1167 -1167 -1163 1162 c-659 659 -1174 1167 -1190 1173 -37 13 -75 12 -112 -4z" />
                        </g>
                    </svg>
                </div>
                <div className="modal-body">
                    {children}
                </div>
            </div>
        </div>
    );
};
