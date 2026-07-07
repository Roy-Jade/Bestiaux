import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { compendiumApi } from "../../../api/compendiumApi";
import { creatureApi } from "../../../api/creatureApi";
import type { Creature, CreatureSummary, TrainingStatus, TrainTarget } from "../../../types/api";

const CREATURE_KEY = ["creature", "active"] as const;
const TRAINING_KEY = ["training", "status"] as const;
const HISTORY_KEY = ["compendium", "history"] as const;

export function useTraining() {
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

  const historyQuery = useQuery<CreatureSummary[]>({
    queryKey: HISTORY_KEY,
    queryFn: async () => {
      const res = await compendiumApi.getHistory();
      return res.creatures;
    },
    retry: false,
  });

  const eligibleMentors = (historyQuery.data ?? []).filter((c) => c.life_stage === "ADULT");

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: CREATURE_KEY });
    void qc.invalidateQueries({ queryKey: TRAINING_KEY });
  };

  const train = useMutation({
    mutationFn: (target: TrainTarget) => creatureApi.train(target),
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

  const assignMentor = useMutation({
    mutationFn: (mentor_id: string) => creatureApi.assignMentor(mentor_id),
    onSuccess: invalidate,
  });

  const removeMentor = useMutation({
    mutationFn: creatureApi.removeMentor,
    onSuccess: invalidate,
  });

  return {
    creature: creatureQuery.data,
    training: trainingQuery.data,
    eligibleMentors,
    isLoading: creatureQuery.isLoading,
    train,
    freeze,
    unfreeze,
    assignMentor,
    removeMentor,
  };
}
