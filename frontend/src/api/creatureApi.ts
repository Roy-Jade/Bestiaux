import { api } from "./client";
import type { Creature, TrainTarget, TrainingStatus } from "../types/api";

export const creatureApi = {
  create: (name: string) => api.post<Creature>("/creature", { name }),

  getActive: () => api.get<Creature>("/creature/active"),

  interact: (action: "feed" | "play" | "heal") =>
    api.post<Creature>("/creature/interact", { action }),

  freeze: () => api.post<Creature>("/creature/freeze"),
  unfreeze: () => api.post<Creature>("/creature/unfreeze"),

  setName: (name: string) => api.post<Creature>("/creature/name", { name }),
  setBiome: (biome_id: string) => api.post<Creature>("/creature/biome", { biome_id }),

  getTrainingStatus: () => api.get<TrainingStatus>("/training/status"),
  train: (target: TrainTarget) => api.post<Creature>("/training/train", { target }),
  wake: () => api.post<Creature>("/training/wake"),
  sleep: () => api.post<Creature>("/training/sleep"),
  assignMentor: (mentor_id: string) => api.post<Creature>("/training/mentor", { mentor_id }),
  removeMentor: () => api.delete<Creature>("/training/mentor"),
};
