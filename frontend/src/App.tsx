import { Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Menu } from "src/components/Menu";
import { AppProviders } from "./app/providers";

export function App() {
    const location = useLocation();
    console.log(location.pathname);
    const itemName = location.pathname.slice(1) + '-menu-item';
    const menuItems = document.querySelectorAll('.simulations-menu-item, .genomes-menu-item');
    menuItems.forEach(item => {
        if (item.classList.contains(itemName)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    return (
        <AppProviders>
            <div className="app-shell">
                <Menu />
                <main className="app-main">
                    <Suspense fallback={<p>Loading...</p>}>
                        <Outlet />
                    </Suspense>
                </main>
            </div>
        </AppProviders>
    );
}
