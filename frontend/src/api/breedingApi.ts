import { api } from "./client";
import type { CompatiblePartners, Creature, ParentSource } from "../types/api";

export const breedingApi = {
  getCompatible: (parentId?: string) =>
    api.get<CompatiblePartners>(
      parentId ? `/breeding/compatible?parent_id=${parentId}` : "/breeding/compatible",
    ),

  breed: (parent1: ParentSource, parent2: ParentSource) =>
    api.post<Creature>("/breeding", { parent1, parent2 }),
};
