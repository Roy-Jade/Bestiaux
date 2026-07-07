import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { compendiumApi } from "../../../api/compendiumApi";
import { isApiError } from "../../../stores/AuthContext";
import type { CreatureDetail, CreatureSummary } from "../../../types/api";
import type { useTraining } from "../hooks/useTraining";

type Mutations = Pick<ReturnType<typeof useTraining>, "assignMentor" | "removeMentor">;

interface Props extends Mutations {
  currentMentorId: string | null;
  eligibleMentors: CreatureSummary[];
  onClose: () => void;
}

function MentorDetail({
  creature,
  onAssign,
  isPending,
}: {
  creature: CreatureDetail;
  onAssign: (id: string) => void;
  isPending: boolean;
}) {
  return (
    <div className="mentor-detail">
      <h3 className="mentor-detail__name">{creature.name}</h3>
      <dl className="mentor-detail__stats">
        <div className="mentor-detail__stat">
          <dt>Autonomie</dt>
          <dd>{Math.round(creature.autonomy)}%</dd>
        </div>
        <div className="mentor-detail__stat">
          <dt>Force</dt>
          <dd>{Math.round(creature.training_force)}</dd>
        </div>
        <div className="mentor-detail__stat">
          <dt>Beauté</dt>
          <dd>{Math.round(creature.training_beauty)}</dd>
        </div>
        <div className="mentor-detail__stat">
          <dt>Taille</dt>
          <dd>{Math.round(creature.training_size)}</dd>
        </div>
      </dl>
      <button className="btn-primary" onClick={() => onAssign(creature.id)} disabled={isPending}>
        {isPending ? "Assignation…" : "Assigner ce mentor"}
      </button>
    </div>
  );
}

export function MentorPanel({
  currentMentorId,
  eligibleMentors,
  assignMentor,
  removeMentor,
  onClose,
}: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const detailQuery = useQuery<CreatureDetail>({
    queryKey: ["compendium", "creature", selectedId],
    queryFn: () => compendiumApi.getCreatureDetail(selectedId!),
    enabled: selectedId !== null,
  });

  const handleAssign = (id: string) => {
    assignMentor.mutate(id, { onSuccess: onClose });
  };

  const error = assignMentor.error ?? removeMentor.error;

  return (
    <div
      className="biome-selector"
      role="dialog"
      aria-modal="true"
      aria-labelledby="mentor-panel-title"
    >
      <div className="mentor-panel__header">
        <h2 id="mentor-panel-title" className="biome-selector__title">
          {selectedId !== null ? "Détail du mentor" : "Choisir un mentor"}
        </h2>
        {selectedId !== null && (
          <button
            className="mentor-panel__back"
            onClick={() => setSelectedId(null)}
            aria-label="Retour à la liste"
          >
            ←
          </button>
        )}
      </div>

      {error !== null && (
        <p className="form-error">{isApiError(error) ? error.detail : "Erreur inattendue"}</p>
      )}

      {currentMentorId !== null && selectedId === null && (
        <button
          className="mentor-panel__remove"
          onClick={() => removeMentor.mutate(undefined, { onSuccess: onClose })}
          disabled={removeMentor.isPending}
        >
          Retirer le mentor actuel
        </button>
      )}

      {selectedId === null && (
        <ul className="biome-selector__list" role="listbox" aria-label="Mentors disponibles">
          {eligibleMentors.length === 0 && (
            <li className="biome-selector__loading">Aucun mentor disponible.</li>
          )}
          {eligibleMentors.map((c) => (
            <li key={c.id} role="option" aria-selected={c.id === currentMentorId}>
              <button
                className={`biome-selector__item${c.id === currentMentorId ? " biome-selector__item--current" : ""}`}
                onClick={() => setSelectedId(c.id)}
              >
                <span className="biome-selector__item-name">
                  {c.name}
                  {c.id === currentMentorId && " (actuel)"}
                </span>
                <span className="biome-selector__item-desc">
                  F {Math.round(c.training_force)} · B {Math.round(c.training_beauty)} · T{" "}
                  {Math.round(c.training_size)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selectedId !== null && (
        <>
          {detailQuery.isLoading && <p className="biome-selector__loading">Chargement…</p>}
          {detailQuery.data !== undefined && (
            <MentorDetail
              creature={detailQuery.data}
              onAssign={handleAssign}
              isPending={assignMentor.isPending}
            />
          )}
        </>
      )}
    </div>
  );
}
