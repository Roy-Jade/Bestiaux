export type LifeStage = "BABY" | "CHILD" | "ADOLESCENT" | "YOUNG_ADULT" | "ADULT";
export type DeathCause = "STARVATION" | "DISEASE" | "ESCAPE";
export type TrainTarget = "FORCE" | "BEAUTY" | "SIZE";
export type TraitCategory = "EYES" | "SKULL_TOP" | "DORSAL" | "CAUDAL" | "COLOR";

export interface User {
  id: string;
  username: string;
  email: string;
  currency: number;
  created_at: string;
}

export interface Creature {
  id: string;
  name: string;
  life_stage: LifeStage;
  biome_id: string | null;
  generation: number;
  is_alive: boolean;
  death_cause: DeathCause | null;
  max_stage_reached: LifeStage;
  autonomy: number;
  hunger: number;
  health: number;
  happiness: number;
  training_force: number;
  training_beauty: number;
  training_size: number;
  time_frozen: boolean;
  created_at: string | null;
}

export interface TrainingStatus {
  slots_available: number;
  trainings_done_today: number;
  last_trained_at: string | null;
  pending_training_force: number;
  pending_training_beauty: number;
  pending_training_size: number;
  mentor_id: string | null;
  mentor_since: string | null;
  is_asleep: boolean;
  woke_up_at: string | null;
  went_to_sleep_at: string | null;
}

export interface FormEntry {
  form_id: string;
  biome_id: string;
  level: number;
  dominant_stats: string[];
  discovered: boolean;
  latest_creature_id: string | null;
  latest_creature_name: string | null;
}

export interface CreatureSummary {
  id: string;
  name: string;
  generation: number;
  life_stage: LifeStage;
  is_alive: boolean;
  is_active: boolean;
  biome_id: string | null;
  form_id: string | null;
  training_force: number;
  training_beauty: number;
  training_size: number;
  max_stage_reached: LifeStage;
  created_at: string | null;
}

export interface GenomeGene {
  trait_category: TraitCategory;
  allele_from_parent1: string;
  allele_from_parent2: string;
  expressed_allele: string;
}

export interface CreatureDetail extends CreatureSummary {
  autonomy: number;
  hunger: number;
  health: number;
  happiness: number;
  form_id: string | null;
  genome: GenomeGene[];
  parent1_id: string | null;
  parent2_id: string | null;
}

export interface AlleleDetail {
  id: string;
  trait_category: TraitCategory;
  name: string;
  is_dominant: boolean;
  sprite_key: string;
}
