import { useState } from "react";
import type { TrainingStatus, TrainTarget } from "../../../types/api";
import type { useTraining } from "../hooks/useTraining";

type Mutations = Pick<
  ReturnType<typeof useTraining>,
  "train" | "freeze" | "unfreeze" | "assignMentor" | "removeMentor"
>;

interface Props extends Mutations {
  isFrozen: boolean;
  training: TrainingStatus;
  onOpenMentor: () => void;
}

interface TrainButtonProps {
  label: string;
  target: TrainTarget;
  disabled: boolean;
  onTrain: (t: TrainTarget) => void;
}

function TrainButton({ label, target, disabled, onTrain }: TrainButtonProps) {
  return (
    <button
      className="action-btn"
      onClick={() => onTrain(target)}
      disabled={disabled}
      aria-label={`Entraîner ${label}`}
    >
      <span className="action-btn__icon">💪</span>
      <span className="action-btn__label">{label}</span>
    </button>
  );
}

export function TrainingActionBar({
  isFrozen,
  training,
  train,
  freeze,
  unfreeze,
  onOpenMentor,
}: Props) {
  const [open, setOpen] = useState(true);

  const canTrain = training.slots_available > 0 && !training.is_asleep && !isFrozen;
  const isPending = train.isPending || freeze.isPending || unfreeze.isPending;

  return (
    <div className={`action-bar${open ? " action-bar--open" : ""}`}>
      <button
        className="action-bar__toggle"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Masquer les actions" : "Afficher les actions"}
        aria-expanded={open}
        aria-controls="training-action-bar-content"
      >
        ☰
      </button>

      {open && (
        <div
          id="training-action-bar-content"
          className="action-bar__content"
          role="group"
          aria-label="Actions d'entraînement"
        >
          <TrainButton
            label="Force"
            target="FORCE"
            disabled={!canTrain || isPending}
            onTrain={(t) => train.mutate(t)}
          />
          <TrainButton
            label="Beauté"
            target="BEAUTY"
            disabled={!canTrain || isPending}
            onTrain={(t) => train.mutate(t)}
          />
          <TrainButton
            label="Taille"
            target="SIZE"
            disabled={!canTrain || isPending}
            onTrain={(t) => train.mutate(t)}
          />

          <div className="action-bar__separator" />

          <button className="action-btn" onClick={onOpenMentor} aria-label="Gérer le mentor">
            <span className="action-btn__icon">🧑‍🏫</span>
            <span className="action-btn__label">Mentor</span>
          </button>

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

function ActionButton({
  label,
  emoji,
  onClick,
  disabled = false,
}: {
  label: string;
  emoji: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button className="action-btn" onClick={onClick} disabled={disabled} aria-label={label}>
      <span className="action-btn__icon">{emoji}</span>
      <span className="action-btn__label">{label}</span>
    </button>
  );
}
