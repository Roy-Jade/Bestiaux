import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import type { Creature, TrainingStatus } from "../../../types/api";

const THRESHOLDS = [25, 50, 75, 100] as const;

interface TrainingStatBarProps {
  label: string;
  committed: number;
  pending: number;
}

function TrainingStatBar({ label, committed, pending }: TrainingStatBarProps) {
  const total = Math.min(committed + pending, 100);
  return (
    <div
      className="training-stat-bar"
      aria-label={`${label} : ${Math.round(committed)} acquis, ${Math.round(pending)} en attente`}
    >
      <div className="training-stat-bar__track">
        {THRESHOLDS.map((t) => (
          <div
            key={t}
            className="training-stat-bar__threshold"
            style={{ left: `${t}%` }}
            aria-hidden="true"
          />
        ))}
        <div className="training-stat-bar__committed" style={{ width: `${committed}%` }} />
        {pending > 0 && (
          <div
            className="training-stat-bar__pending"
            style={{ left: `${committed}%`, width: `${total - committed}%` }}
          />
        )}
      </div>
      <span className="training-stat-bar__label">{label}</span>
    </div>
  );
}

function TrainingToggle() {
  const { pathname } = useLocation();
  const isOnTraining = pathname === "/training";

  return (
    <Link
      to={isOnTraining ? "/creature" : "/training"}
      className={`training-toggle${isOnTraining ? " training-toggle--active" : ""}`}
      aria-label={isOnTraining ? "Retour au bestiau" : "Voir les entraînements"}
    >
      💪
    </Link>
  );
}

interface Props {
  creature: Creature;
  training: TrainingStatus;
}

export function TrainingStatsBar({ creature, training }: Props) {
  const [open, setOpen] = useState(true);

  return (
    <>
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
          <div className="stats-bar__content" role="group" aria-label="Stats d'entraînement">
            <TrainingStatBar
              label="Force"
              committed={creature.training_force}
              pending={training.pending_training_force}
            />
            <TrainingStatBar
              label="Beauté"
              committed={creature.training_beauty}
              pending={training.pending_training_beauty}
            />
            <TrainingStatBar
              label="Taille"
              committed={creature.training_size}
              pending={training.pending_training_size}
            />
            <TrainingToggle />
          </div>
        )}

        {!open && <TrainingToggle />}
      </div>

      {training.is_en_forme && (
        <div className="en-forme-badge" aria-live="polite">
          ⚡ En forme
        </div>
      )}
    </>
  );
}
