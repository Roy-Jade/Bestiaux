import { useState } from "react";
import { CreatureRenderer } from "../../creature/components/CreatureRenderer";
import { BreedingModal } from "../components/BreedingModal";
import { useBreeding } from "../hooks/useBreeding";

export function BreedingPage() {
  const { creature, isLoading, breed, createFresh } = useBreeding();
  const [modalOpen, setModalOpen] = useState(true);

  if (isLoading) {
    return <div className="loading-screen">Chargement…</div>;
  }

  return (
    <div className="creature-page">
      <button className="app-menu-btn" aria-label="Menu de l'application" disabled>
        ⚙️
      </button>

      <div className="creature-canvas-wrapper">
        <CreatureRenderer biomeId={creature?.biome_id ?? null} />
      </div>

      {!modalOpen && (
        <div className="breeding-open-btn-wrapper">
          <button className="btn-primary" onClick={() => setModalOpen(true)}>
            Nouvelle génération
          </button>
        </div>
      )}

      {modalOpen && (
        <BreedingModal
          activeCreature={creature}
          breed={breed}
          createFresh={createFresh}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}
