import { useState } from "react";
import { Link } from "react-router-dom";
import type { Creature, TrainingStatus } from "../../../types/api";

interface Props {
  creature: Creature;
  training: TrainingStatus | undefined;
}

function StatBar({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div className="stat-bar" aria-label={`${label} : ${Math.round(value)} sur 100`}>
      <div className="stat-bar__fill" style={{ width: `${value}%`, backgroundColor: color }} />
    </div>
  );
}

export function StatsBar({ creature, training }: Props) {
  const [open, setOpen] = useState(true);

  return (
    <div className={`stats-bar${open ? "" : " stats-bar--collapsed"}`}>
      <button
        className="stats-bar__toggle"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Masquer les stats" : "Afficher les stats"}
        aria-expanded={open}
      >
        ☰
      </button>

      {open && (
        <div className="stats-bar__content" role="group" aria-label="État du bestiau">
          {/* Accessibility: phase et biome lisibles par les lecteurs d'écran */}
          <span className="sr-only">
            Phase : {creature.life_stage.toLowerCase()}.
            {creature.biome_id !== null ? ` Biome : ${creature.biome_id}.` : ""}
          </span>

          <StatBar value={creature.hunger} label="Faim" color="#f6a623" />
          <StatBar value={creature.happiness} label="Bonheur" color="#7ed321" />
          <StatBar value={creature.health} label="Santé" color="#e94560" />

          {training !== undefined && training.slots_available > 0 && (
            <Link
              to="/training"
              className="stats-bar__training-slot"
              aria-label={`${training.slots_available} séance${training.slots_available > 1 ? "s" : ""} d'entraînement disponible${training.slots_available > 1 ? "s" : ""}`}
            >
              💪 {training.slots_available}⚡
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
