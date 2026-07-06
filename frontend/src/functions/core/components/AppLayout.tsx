import { NavLink, Outlet } from "react-router-dom";

const tabs = [
  { path: "/creature", label: "Bestiau", icon: "🐾" },
  { path: "/training", label: "Entraîn.", icon: "🏋️" },
  { path: "/breeding", label: "Élevage", icon: "🧬" },
  { path: "/compendium", label: "Compend.", icon: "📖" },
] as const;

export function AppLayout() {
  return (
    <div className="app-layout">
      <div className="app-content">
        <Outlet />
      </div>
      <nav className="tab-bar">
        {tabs.map((tab) => (
          <NavLink
            key={tab.path}
            to={tab.path}
            className={({ isActive }) => `tab-item${isActive ? " tab-item--active" : ""}`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
