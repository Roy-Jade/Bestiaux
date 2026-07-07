import { useState } from "react";
import { isApiError } from "../../../stores/AuthContext";
import type { useCreature } from "../hooks/useCreature";

interface Props {
  setName: ReturnType<typeof useCreature>["setName"];
  unfreeze: ReturnType<typeof useCreature>["unfreeze"];
}

export function NameModal({ setName, unfreeze }: Props) {
  const [name, setNameValue] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() === "") return;
    await setName.mutateAsync(name.trim());
    unfreeze.mutate();
  };

  const error = setName.error ?? unfreeze.error;
  const isPending = setName.isPending || unfreeze.isPending;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="name-modal-title"
    >
      <div className="modal">
        <h2 id="name-modal-title" className="modal__title">
          Ton bestiau est né !
        </h2>
        <p className="modal__subtitle">Donne-lui un nom pour commencer.</p>

        <form
          className="auth-form"
          onSubmit={(e) => {
            void handleSubmit(e);
          }}
        >
          <div className="form-group">
            <label htmlFor="creature-name">Nom du bestiau</label>
            <input
              id="creature-name"
              className="form-input"
              type="text"
              maxLength={32}
              autoFocus
              value={name}
              onChange={(e) => setNameValue(e.target.value)}
              required
            />
          </div>

          {error !== null && (
            <p className="form-error">{isApiError(error) ? error.detail : "Erreur inattendue"}</p>
          )}

          <button className="btn-primary" type="submit" disabled={isPending || name.trim() === ""}>
            {isPending ? "En cours…" : "Confirmer"}
          </button>
        </form>
      </div>
    </div>
  );
}
