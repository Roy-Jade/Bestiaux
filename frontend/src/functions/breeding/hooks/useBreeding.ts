import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { breedingApi } from "../../../api/breedingApi";
import { creatureApi } from "../../../api/creatureApi";
import type { CompatiblePartners, Creature, ParentSource } from "../../../types/api";

const CREATURE_KEY = ["creature", "active"] as const;

export function useBreeding() {
  const qc = useQueryClient();
  const navigate = useNavigate();

  const creatureQuery = useQuery<Creature>({
    queryKey: CREATURE_KEY,
    queryFn: creatureApi.getActive,
    retry: false,
  });

  const breed = useMutation({
    mutationFn: ({ parent1, parent2 }: { parent1: ParentSource; parent2: ParentSource }) =>
      breedingApi.breed(parent1, parent2),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: CREATURE_KEY });
      void navigate("/creature");
    },
  });

  const createFresh = useMutation({
    mutationFn: () => creatureApi.create(""),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: CREATURE_KEY });
      void navigate("/creature");
    },
  });

  return {
    creature: creatureQuery.data,
    isLoading: creatureQuery.isLoading,
    breed,
    createFresh,
  };
}

export function useCompatiblePartners(parentId: string | null) {
  return useQuery<CompatiblePartners>({
    queryKey: ["breeding", "compatible", parentId],
    queryFn: () => breedingApi.getCompatible(parentId!),
    enabled: parentId !== null,
    retry: false,
  });
}

export function useEligibleParents() {
  return useQuery<CompatiblePartners>({
    queryKey: ["breeding", "eligible"],
    queryFn: () => breedingApi.getCompatible(),
    retry: false,
  });
}
