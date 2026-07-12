import { useEffect } from "react";
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
    error,
    interact,
    freeze,
    unfreeze,
    setName,
    setBiome,
    wake,
    sleep,
    createFirst,
  } = useCreature();

  // Auto-create first creature if none exists (404 from API)
  useEffect(() => {
    if (!isLoading && creature === undefined && error === null) {
      createFirst.mutate();
    }
  }, [isLoading, creature, error, createFirst]);

  if (isLoading || createFirst.isPending) {
    return <div className="loading-screen">Chargement…</div>;
  }

  if (createFirst.isError || (error !== null && creature === undefined)) {
    return (
      <div className="loading-screen">
        <p>Une erreur est survenue. Veuillez recharger la page.</p>
      </div>
    );
  }

  if (creature === undefined) {
    return <div className="loading-screen">Chargement…</div>;
  }

  const isPaused = creature.time_frozen;
  const awaitingName = needsName(creature);
  const awaitingBiome = needsBiome(creature);
  const showBiomePanel = awaitingBiome && !awaitingName;

  return (
    <div className={`creature-page${showBiomePanel ? " creature-page--biome-open" : ""}`}>
      {!awaitingName && !awaitingBiome && <StatsBar creature={creature} training={training} />}

      <button className="app-menu-btn" aria-label="Menu de l'application" disabled>
        ⚙️
      </button>

      <div
        className={`creature-canvas-wrapper${showBiomePanel ? " creature-canvas-wrapper--shifted" : ""}`}
      >
        <CreatureRenderer biomeId={creature.biome_id} />
      </div>

      {showBiomePanel && <BiomeSelector setBiome={setBiome} unfreeze={unfreeze} />}
      {awaitingName && <NameModal setName={setName} unfreeze={unfreeze} />}

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
