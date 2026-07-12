import { NavLink, Outlet } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { creatureApi } from "../../../api/creatureApi";
import type { Creature } from "../../../types/api";

function useShowBreedingTab() {
  const { data: creature } = useQuery<Creature>({
    queryKey: ["creature", "active"],
    queryFn: creatureApi.getActive,
    retry: false,
    staleTime: 30_000,
  });

  if (creature === undefined) return false;
  return creature.life_stage === "YOUNG_ADULT" || !creature.is_alive;
}

const BASE_TABS = [
  { path: "/creature", label: "Bestiau", icon: "🐾" },
  { path: "/training", label: "Entraîn.", icon: "🏋️" },
  { path: "/compendium", label: "Compend.", icon: "📖" },
] as const;

const BREEDING_TAB = { path: "/breeding", label: "Élevage", icon: "🧬" } as const;

export function AppLayout() {
  const showBreeding = useShowBreedingTab();

  const tabs = showBreeding
    ? [BASE_TABS[0], BASE_TABS[1], BREEDING_TAB, BASE_TABS[2]]
    : [...BASE_TABS];

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
