import { ActionBar } from "../components/ActionBar";
import { BiomeSelector } from "../components/BiomeSelector";
import { CreatureRenderer } from "../components/CreatureRenderer";
import { NameModal } from "../components/NameModal";
import { StatsBar } from "../components/StatsBar";
import { useCreature } from "../hooks/useCreature";

function needsName(creature: { name: string }): boolean {
  return creature.name === "";
}

function needsBiome(creature: { life_stage: string; biome_id: string | null }): boolean {
  return creature.life_stage === "CHILD" && creature.biome_id === null;
}

export function CreaturePage() {
  const {
    creature,
    training,
    isLoading,
    interact,
    freeze,
    unfreeze,
    setName,
    setBiome,
    wake,
    sleep,
  } = useCreature();

  if (isLoading) {
    return <div className="loading-screen">Chargement…</div>;
  }

  if (creature === undefined) {
    return (
      <div className="loading-screen">
        <p>Pas encore de bestiau. Lance un élevage pour commencer !</p>
      </div>
    );
  }

  const isPaused = creature.time_frozen;
  const awaitingName = needsName(creature);
  const awaitingBiome = needsBiome(creature);
  const showBiomePanel = awaitingBiome && !awaitingName;

  return (
    <div className={`creature-page${showBiomePanel ? " creature-page--biome-open" : ""}`}>
      {/* Stats bar — masquée en cas de pause système */}
      {!awaitingName && !awaitingBiome && <StatsBar creature={creature} training={training} />}

      {/* Bouton app menu (hors scope — emplacement réservé) */}
      <button className="app-menu-btn" aria-label="Menu de l'application" disabled>
        ⚙️
      </button>

      {/* Canvas Pixi */}
      <div
        className={`creature-canvas-wrapper${showBiomePanel ? " creature-canvas-wrapper--shifted" : ""}`}
      >
        <CreatureRenderer biomeId={creature.biome_id} />
      </div>

      {/* Sélecteur de biome (glisse depuis la droite) */}
      {showBiomePanel && <BiomeSelector setBiome={setBiome} unfreeze={unfreeze} />}

      {/* Modale de nommage */}
      {awaitingName && <NameModal setName={setName} unfreeze={unfreeze} />}

      {/* Action bar — masquée en cas de pause système */}
      {!awaitingName && !awaitingBiome && (
        <ActionBar
          isFrozen={isPaused}
          training={training}
          interact={interact}
          freeze={freeze}
          unfreeze={unfreeze}
          wake={wake}
          sleep={sleep}
        />
      )}
    </div>
  );
}
