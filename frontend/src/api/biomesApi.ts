import { api } from "./client";
import type { Biome } from "../types/api";

export const biomesApi = {
  list: () => api.get<Biome[]>("/biomes"),
};
