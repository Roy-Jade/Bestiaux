import { useQuery } from "@tanstack/react-query";
import { biomesApi } from "../../../api/biomesApi";
import { isApiError } from "../../../stores/AuthContext";
import type { Biome } from "../../../types/api";
import type { useCreature } from "../hooks/useCreature";

interface Props {
  setBiome: ReturnType<typeof useCreature>["setBiome"];
  unfreeze: ReturnType<typeof useCreature>["unfreeze"];
}

export function BiomeSelector({ setBiome, unfreeze }: Props) {
  const { data: biomes, isLoading } = useQuery<Biome[]>({
    queryKey: ["biomes"],
    queryFn: biomesApi.list,
  });

  const handleSelect = async (biomeId: string) => {
    await setBiome.mutateAsync(biomeId);
    unfreeze.mutate();
  };

  const error = setBiome.error ?? unfreeze.error;
  const isPending = setBiome.isPending || unfreeze.isPending;

  return (
    <div
      className="biome-selector"
      role="dialog"
      aria-modal="true"
      aria-labelledby="biome-selector-title"
    >
      <h2 id="biome-selector-title" className="biome-selector__title">
        Choisis un biome
      </h2>
      <p className="biome-selector__subtitle">
        Il définira l'apparence et les affinités de ton bestiau.
      </p>

      {isLoading && <p className="biome-selector__loading">Chargement…</p>}

      {error !== null && (
        <p className="form-error">{isApiError(error) ? error.detail : "Erreur inattendue"}</p>
      )}

      <ul className="biome-selector__list" role="listbox" aria-label="Biomes disponibles">
        {biomes?.map((biome) => (
          <li key={biome.id} role="option" aria-selected={false}>
            <button
              className="biome-selector__item"
              onClick={() => {
                void handleSelect(biome.id);
              }}
              disabled={isPending}
            >
              <span className="biome-selector__item-name">{biome.name}</span>
              {biome.description !== "" && (
                <span className="biome-selector__item-desc">{biome.description}</span>
              )}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
