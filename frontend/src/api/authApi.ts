import { api } from "./client";
import type { User } from "../types/api";

export const authApi = {
  register: (username: string, email: string, password: string) =>
    api.post<User>("/auth/register", { username, email, password }),

  login: (email: string, password: string) => api.post<User>("/auth/login", { email, password }),

  logout: () => api.post<{ detail: string }>("/auth/logout"),

  me: () => api.get<User>("/auth/me"),
};
