import { api } from "./client";
import type { Creature } from "../types/api";

type ParentSource = { type: "creature"; id: string } | { type: "wild" };

export const breedingApi = {
  breed: (parent1: ParentSource, parent2: ParentSource) =>
    api.post<Creature>("/breeding", { parent1, parent2 }),
};
