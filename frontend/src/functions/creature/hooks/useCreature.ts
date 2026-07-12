import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { creatureApi } from "../../../api/creatureApi";
import { ApiError } from "../../../api/client";
import type { Creature, TrainingStatus } from "../../../types/api";

const CREATURE_KEY = ["creature", "active"] as const;
const TRAINING_KEY = ["training", "status"] as const;

export function useCreature() {
  const qc = useQueryClient();

  const creatureQuery = useQuery<Creature, ApiError>({
    queryKey: CREATURE_KEY,
    queryFn: creatureApi.getActive,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status === 404) return false;
      return failureCount < 1;
    },
  });

  const trainingQuery = useQuery<TrainingStatus>({
    queryKey: TRAINING_KEY,
    queryFn: creatureApi.getTrainingStatus,
    enabled: creatureQuery.data !== undefined,
    retry: false,
  });

  const is404 = creatureQuery.error instanceof ApiError && creatureQuery.error.status === 404;

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: CREATURE_KEY });
    void qc.invalidateQueries({ queryKey: TRAINING_KEY });
  };

  const createFirst = useMutation({
    mutationFn: () => creatureApi.create(""),
    onSuccess: invalidate,
  });

  const interact = useMutation({
    mutationFn: creatureApi.interact,
    onSuccess: invalidate,
  });

  const freeze = useMutation({
    mutationFn: creatureApi.freeze,
    onSuccess: invalidate,
  });

  const unfreeze = useMutation({
    mutationFn: creatureApi.unfreeze,
    onSuccess: invalidate,
  });

  const setName = useMutation({
    mutationFn: creatureApi.setName,
    onSuccess: invalidate,
  });

  const setBiome = useMutation({
    mutationFn: creatureApi.setBiome,
    onSuccess: invalidate,
  });

  const wake = useMutation({
    mutationFn: creatureApi.wake,
    onSuccess: invalidate,
  });

  const sleep = useMutation({
    mutationFn: creatureApi.sleep,
    onSuccess: invalidate,
  });

  return {
    creature: creatureQuery.data,
    training: trainingQuery.data,
    isLoading: creatureQuery.isLoading,
    error: is404 ? null : creatureQuery.error,
    createFirst,
    interact,
    freeze,
    unfreeze,
    setName,
    setBiome,
    wake,
    sleep,
  };
}
