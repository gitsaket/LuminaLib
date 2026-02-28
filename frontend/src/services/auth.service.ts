import type { TokenResponse, User } from "@/types";
import { apiClient } from "@/lib/api-client";

export interface SingupPayload {
  full_name: string;
  email: string;
  password: string;
  username: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authService = {
  async signup(payload: SingupPayload): Promise<User> {
    const { data } = await apiClient.post<User>("/auth/signup", payload);
    return data;
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>(
      "/auth/login",
      payload,
    );
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return data;
  },

  async getMe(): Promise<User> {
    const { data } = await apiClient.get<User>("/auth/me");
    return data;
  },

  async signout(): Promise<void> {
    await apiClient.post("/auth/signout");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};
