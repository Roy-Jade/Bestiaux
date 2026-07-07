import { useState } from "react";
import { CreatureRenderer } from "../../creature/components/CreatureRenderer";
import { MentorPanel } from "../components/MentorPanel";
import { TrainingActionBar } from "../components/TrainingActionBar";
import { TrainingStatsBar } from "../components/TrainingStatsBar";
import { useTraining } from "../hooks/useTraining";

export function TrainingPage() {
  const {
    creature,
    training,
    eligibleMentors,
    isLoading,
    train,
    freeze,
    unfreeze,
    assignMentor,
    removeMentor,
  } = useTraining();
  const [mentorOpen, setMentorOpen] = useState(false);

  if (isLoading) {
    return <div className="loading-screen">Chargement…</div>;
  }

  if (creature === undefined || training === undefined) {
    return (
      <div className="loading-screen">
        <p>Pas encore de bestiau en cours d&apos;entraînement.</p>
      </div>
    );
  }

  const isFrozen = creature.time_frozen;

  return (
    <div className={`creature-page${mentorOpen ? " creature-page--biome-open" : ""}`}>
      <TrainingStatsBar creature={creature} training={training} />

      <button className="app-menu-btn" aria-label="Menu de l'application" disabled>
        ⚙️
      </button>

      <div
        className={`creature-canvas-wrapper${mentorOpen ? " creature-canvas-wrapper--shifted" : ""}`}
      >
        <CreatureRenderer biomeId={creature.biome_id} />
      </div>

      {mentorOpen && (
        <MentorPanel
          currentMentorId={training.mentor_id}
          eligibleMentors={eligibleMentors}
          assignMentor={assignMentor}
          removeMentor={removeMentor}
          onClose={() => setMentorOpen(false)}
        />
      )}

      <TrainingActionBar
        isFrozen={isFrozen}
        training={training}
        train={train}
        freeze={freeze}
        unfreeze={unfreeze}
        assignMentor={assignMentor}
        removeMentor={removeMentor}
        onOpenMentor={() => setMentorOpen((v) => !v)}
      />
    </div>
  );
}
