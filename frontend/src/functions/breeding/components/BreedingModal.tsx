import { useState } from "react";
import { isApiError } from "../../../stores/AuthContext";
import type { CompatibleCreature, Creature, ParentSource } from "../../../types/api";
import { useCompatiblePartners } from "../hooks/useBreeding";
import type { useBreeding } from "../hooks/useBreeding";

type BreedMutation = ReturnType<typeof useBreeding>["breed"];
type CreateFreshMutation = ReturnType<typeof useBreeding>["createFresh"];

type Step =
  | { kind: "choose_option" }
  | { kind: "choose_parent2"; parent1: ParentSource; parent1Label: string }
  | {
      kind: "confirm";
      parent1: ParentSource;
      parent1Label: string;
      parent2: ParentSource;
      parent2Label: string;
    };

interface Props {
  activeCreature: Creature | undefined;
  breed: BreedMutation;
  createFresh: CreateFreshMutation;
  onClose: () => void;
}

function PartnerList({
  parentId,
  onSelectOwned,
  onSelectWild,
}: {
  parentId: string;
  onSelectOwned: (c: CompatibleCreature) => void;
  onSelectWild: () => void;
}) {
  const { data, isLoading } = useCompatiblePartners(parentId);

  return (
    <div className="breeding-partner-list">
      {isLoading && <p className="biome-selector__loading">Chargement…</p>}

      {data?.wild_available && (
        <button className="biome-selector__item" onClick={onSelectWild}>
          <span className="biome-selector__item-name">🌿 Sauvage</span>
          <span className="biome-selector__item-desc">Partenaire issu du gene pool sauvage</span>
        </button>
      )}

      {data?.creatures.map((c) => (
        <button key={c.id} className="biome-selector__item" onClick={() => onSelectOwned(c)}>
          <span className="biome-selector__item-name">{c.name}</span>
          <span className="biome-selector__item-desc">
            Gén. {c.generation} · F {Math.round(c.training_force)} · B{" "}
            {Math.round(c.training_beauty)} · T {Math.round(c.training_size)}
          </span>
        </button>
      ))}

      {data !== undefined && data.creatures.length === 0 && !data.wild_available && (
        <p className="biome-selector__loading">Aucun partenaire compatible disponible.</p>
      )}
    </div>
  );
}

export function BreedingModal({ activeCreature, breed, createFresh, onClose }: Props) {
  const [step, setStep] = useState<Step>({ kind: "choose_option" });

  const isPending = breed.isPending || createFresh.isPending;
  const error = breed.error ?? createFresh.error;

  const handleConfirm = () => {
    if (step.kind !== "confirm") return;
    breed.mutate({ parent1: step.parent1, parent2: step.parent2 });
  };

  const goToParent2 = (parent1: ParentSource, parent1Label: string) =>
    setStep({ kind: "choose_parent2", parent1, parent1Label });

  const goToConfirm = (
    parent1: ParentSource,
    parent1Label: string,
    parent2: ParentSource,
    parent2Label: string,
  ) => setStep({ kind: "confirm", parent1, parent1Label, parent2, parent2Label });

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="breeding-modal-title"
    >
      <div className="modal breeding-modal">
        <div className="breeding-modal__header">
          <h2 id="breeding-modal-title" className="modal__title">
            {step.kind === "choose_option" && "Nouvelle génération"}
            {step.kind === "choose_parent2" && "Choisir le second parent"}
            {step.kind === "confirm" && "Confirmer la reproduction"}
          </h2>
          <button
            className="mentor-panel__back"
            onClick={
              step.kind === "choose_option" ? onClose : () => setStep({ kind: "choose_option" })
            }
            aria-label={step.kind === "choose_option" ? "Fermer" : "Retour"}
          >
            {step.kind === "choose_option" ? "✕" : "←"}
          </button>
        </div>

        {error !== null && (
          <p className="form-error">{isApiError(error) ? error.detail : "Erreur inattendue"}</p>
        )}

        {step.kind === "choose_option" && (
          <div className="breeding-options">
            {activeCreature?.life_stage === "YOUNG_ADULT" && (
              <button
                className="biome-selector__item"
                onClick={() =>
                  goToParent2({ type: "creature", id: activeCreature.id }, activeCreature.name)
                }
              >
                <span className="biome-selector__item-name">🐾 {activeCreature.name} (actuel)</span>
                <span className="biome-selector__item-desc">
                  Utiliser mon Jeune Adulte comme parent
                </span>
              </button>
            )}

            <button
              className="biome-selector__item"
              onClick={() =>
                setStep({
                  kind: "choose_parent2",
                  parent1: { type: "wild" },
                  parent1Label: "Un autre adulte",
                })
              }
              disabled
              aria-disabled="true"
              title="Sélection d'un adulte existant — choisissez d'abord l'adulte"
            >
              <span className="biome-selector__item-name">👥 Un adulte possédé</span>
              <span className="biome-selector__item-desc">
                Choisir un adulte de ma lignée comme parent
              </span>
            </button>

            <button
              className="biome-selector__item"
              onClick={() => createFresh.mutate()}
              disabled={isPending}
            >
              <span className="biome-selector__item-name">🌱 Nouvelle lignée</span>
              <span className="biome-selector__item-desc">
                Repartir de zéro avec un bébé de base
              </span>
            </button>
          </div>
        )}

        {step.kind === "choose_parent2" && (
          <PartnerList
            parentId={step.parent1.type === "creature" ? step.parent1.id : ""}
            onSelectWild={() =>
              goToConfirm(step.parent1, step.parent1Label, { type: "wild" }, "Sauvage")
            }
            onSelectOwned={(c) =>
              goToConfirm(step.parent1, step.parent1Label, { type: "creature", id: c.id }, c.name)
            }
          />
        )}

        {step.kind === "confirm" && (
          <div className="breeding-confirm">
            <div className="breeding-confirm__parents">
              <div className="breeding-confirm__parent">
                <span className="breeding-confirm__label">Parent 1</span>
                <span className="breeding-confirm__name">{step.parent1Label}</span>
              </div>
              <span className="breeding-confirm__cross">×</span>
              <div className="breeding-confirm__parent">
                <span className="breeding-confirm__label">Parent 2</span>
                <span className="breeding-confirm__name">{step.parent2Label}</span>
              </div>
            </div>

            <button className="btn-primary" onClick={handleConfirm} disabled={isPending}>
              {isPending ? "Génération en cours…" : "Confirmer et générer le bébé"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
