import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { creatureApi } from "../../../api/creatureApi";
import type { Creature, TrainingStatus } from "../../../types/api";

const CREATURE_KEY = ["creature", "active"] as const;
const TRAINING_KEY = ["training", "status"] as const;

export function useCreature() {
  const qc = useQueryClient();

  const creatureQuery = useQuery<Creature>({
    queryKey: CREATURE_KEY,
    queryFn: creatureApi.getActive,
    retry: false,
  });

  const trainingQuery = useQuery<TrainingStatus>({
    queryKey: TRAINING_KEY,
    queryFn: creatureApi.getTrainingStatus,
    enabled: creatureQuery.data !== undefined,
    retry: false,
  });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: CREATURE_KEY });
    void qc.invalidateQueries({ queryKey: TRAINING_KEY });
  };

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
    error: creatureQuery.error,
    interact,
    freeze,
    unfreeze,
    setName,
    setBiome,
    wake,
    sleep,
  };
}
