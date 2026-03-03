import { authService } from "@/services/auth.service";
import { apiClient } from "@/lib/api-client";

jest.mock("@/lib/api-client", () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

const mockPost = apiClient.post as jest.Mock;
const mockGet = apiClient.get as jest.Mock;

const mockUser = {
  id: 1,
  email: "test@example.com",
  username: "testuser",
  full_name: "Test User",
  bio: null,
  is_active: true,
};

const mockTokenResponse = {
  access_token: "access-abc",
  refresh_token: "refresh-xyz",
  token_type: "bearer",
};

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

describe("authService.signup", () => {
  it("calls POST /auth/signup with correct body and returns User", async () => {
    mockPost.mockResolvedValueOnce({ data: mockUser });

    const payload = {
      full_name: "Test User",
      email: "test@example.com",
      password: "password123",
      username: "testuser",
    };
    const result = await authService.signup(payload);

    expect(mockPost).toHaveBeenCalledWith("/auth/signup", payload);
    expect(result).toEqual(mockUser);
  });
});

describe("authService.login", () => {
  it("calls POST /auth/login, stores tokens in localStorage", async () => {
    mockPost.mockResolvedValueOnce({ data: mockTokenResponse });

    await authService.login({
      email: "test@example.com",
      password: "password123",
    });

    expect(mockPost).toHaveBeenCalledWith("/auth/login", {
      email: "test@example.com",
      password: "password123",
    });
    expect(localStorage.getItem("access_token")).toBe("access-abc");
    expect(localStorage.getItem("refresh_token")).toBe("refresh-xyz");
  });
});

describe("authService.getMe", () => {
  it("calls GET /auth/me and returns User", async () => {
    mockGet.mockResolvedValueOnce({ data: mockUser });

    const result = await authService.getMe();

    expect(mockGet).toHaveBeenCalledWith("/auth/me");
    expect(result).toEqual(mockUser);
  });
});

describe("authService.signout", () => {
  it("calls POST /auth/signout and removes tokens from localStorage", async () => {
    localStorage.setItem("access_token", "access-abc");
    localStorage.setItem("refresh_token", "refresh-xyz");
    mockPost.mockResolvedValueOnce({});

    await authService.signout();

    expect(mockPost).toHaveBeenCalledWith("/auth/signout");
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });
});
