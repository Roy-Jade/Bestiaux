import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import type { Creature, TrainingStatus } from "../../../types/api";

interface Props {
  creature: Creature;
  training: TrainingStatus | undefined;
}

function StatBar({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div
      className="stat-bar"
      role="meter"
      aria-label={label}
      aria-valuenow={Math.round(value)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div className="stat-bar__fill" style={{ width: `${value}%`, backgroundColor: color }} />
    </div>
  );
}

function TrainingToggle({ training }: { training: TrainingStatus | undefined }) {
  const { pathname } = useLocation();
  const isOnTraining = pathname === "/training";
  const slots = training?.slots_available ?? 0;

  return (
    <Link
      to={isOnTraining ? "/creature" : "/training"}
      className={`training-toggle${isOnTraining ? " training-toggle--active" : ""}`}
      aria-label={
        isOnTraining
          ? "Retour au bestiau"
          : slots > 0
            ? `${slots} séance${slots > 1 ? "s" : ""} d'entraînement disponible${slots > 1 ? "s" : ""} — voir l'entraînement`
            : "Voir l'entraînement"
      }
    >
      💪{slots > 0 && !isOnTraining ? ` ${slots}⚡` : ""}
    </Link>
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
          <span className="sr-only">
            Phase : {creature.life_stage.toLowerCase()}.
            {creature.biome_id !== null ? ` Biome : ${creature.biome_id}.` : ""}
          </span>

          <StatBar value={creature.hunger} label="Faim" color="#f6a623" />
          <StatBar value={creature.happiness} label="Bonheur" color="#7ed321" />
          <StatBar value={creature.health} label="Santé" color="#e94560" />

          <TrainingToggle training={training} />
        </div>
      )}

      {!open && <TrainingToggle training={training} />}
    </div>
  );
}
