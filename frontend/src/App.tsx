import { Outlet } from "react-router-dom";
import { Menu } from "src/components/Menu";
import { AppProviders } from "./app/providers";

export function App() {
    return (
        <AppProviders>
            <Menu />
            <Outlet />
        </AppProviders>
    );
}