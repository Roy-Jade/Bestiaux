import { useState } from "react";
import type { TrainingStatus } from "../../../types/api";
import type { useCreature } from "../hooks/useCreature";

type Mutations = Pick<
  ReturnType<typeof useCreature>,
  "interact" | "freeze" | "unfreeze" | "wake" | "sleep"
>;

interface Props extends Mutations {
  isFrozen: boolean;
  training: TrainingStatus | undefined;
}

interface ActionButtonProps {
  label: string;
  emoji: string;
  onClick: () => void;
  disabled?: boolean;
}

function ActionButton({ label, emoji, onClick, disabled = false }: ActionButtonProps) {
  return (
    <button className="action-btn" onClick={onClick} disabled={disabled} aria-label={label}>
      <span className="action-btn__icon">{emoji}</span>
      <span className="action-btn__label">{label}</span>
    </button>
  );
}

export function ActionBar({ isFrozen, training, interact, freeze, unfreeze, wake, sleep }: Props) {
  const [open, setOpen] = useState(false);
  const isPending =
    interact.isPending ||
    freeze.isPending ||
    unfreeze.isPending ||
    wake.isPending ||
    sleep.isPending;

  const isAsleep = training?.is_asleep ?? false;

  return (
    <div className={`action-bar${open ? " action-bar--open" : ""}`}>
      <button
        className="action-bar__toggle"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Masquer les actions" : "Afficher les actions"}
        aria-expanded={open}
        aria-controls="action-bar-content"
      >
        ☰
      </button>

      {open && (
        <div
          id="action-bar-content"
          className="action-bar__content"
          role="group"
          aria-label="Actions"
        >
          <ActionButton
            label="Nourrir"
            emoji="🍖"
            onClick={() => interact.mutate("feed")}
            disabled={isPending || isFrozen || isAsleep}
          />
          <ActionButton
            label="Jouer"
            emoji="🎮"
            onClick={() => interact.mutate("play")}
            disabled={isPending || isFrozen || isAsleep}
          />
          <ActionButton
            label="Soigner"
            emoji="💊"
            onClick={() => interact.mutate("heal")}
            disabled={isPending || isFrozen || isAsleep}
          />

          <div className="action-bar__separator" />

          {isAsleep ? (
            <ActionButton
              label="Réveiller"
              emoji="☀️"
              onClick={() => wake.mutate()}
              disabled={isPending}
            />
          ) : (
            <ActionButton
              label="Dormir"
              emoji="😴"
              onClick={() => sleep.mutate()}
              disabled={isPending || isFrozen}
            />
          )}

          <ActionButton
            label={isFrozen ? "Reprendre" : "Pause"}
            emoji={isFrozen ? "▶️" : "⏸"}
            onClick={() => (isFrozen ? unfreeze.mutate() : freeze.mutate())}
            disabled={isPending}
          />
        </div>
      )}
    </div>
  );
}
