import { api } from "./client";
import type { AlleleDetail, CreatureDetail, CreatureSummary, FormEntry } from "../types/api";

export const compendiumApi = {
  getForms: () => api.get<{ forms: FormEntry[] }>("/compendium/forms"),
  getHistory: () => api.get<{ creatures: CreatureSummary[] }>("/compendium/history"),
  getCreatureDetail: (id: string) => api.get<CreatureDetail>(`/compendium/creature/${id}`),
  getUnlockedAlleles: () => api.get<{ alleles: AlleleDetail[] }>("/compendium/alleles"),
};
