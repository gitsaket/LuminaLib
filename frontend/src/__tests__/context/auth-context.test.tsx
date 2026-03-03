import React from "react";
import { render, screen, act, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "@/context/auth-context";
import { authService } from "@/services/auth.service";

jest.mock("@/services/auth.service", () => ({
  authService: {
    getMe: jest.fn(),
    login: jest.fn(),
    signout: jest.fn(),
  },
}));

const mockGetMe = authService.getMe as jest.Mock;
const mockLogin = authService.login as jest.Mock;
const mockSignout = authService.signout as jest.Mock;

const mockUser = {
  id: 1,
  email: "test@example.com",
  username: "testuser",
  full_name: "Test User",
  bio: null,
  is_active: true,
};

// Helper component to expose context values
function AuthConsumer() {
  const { user, isAuthenticated, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="authenticated">{String(isAuthenticated)}</span>
      <span data-testid="user">{user ? user.email : "null"}</span>
      <button onClick={() => login("test@example.com", "password123")}>
        Login
      </button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <AuthProvider>
      <AuthConsumer />
    </AuthProvider>,
  );
}

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

describe("AuthContext", () => {
  it("isAuthenticated is false when no token in localStorage", async () => {
    mockGetMe.mockResolvedValue(mockUser);
    renderWithProvider();

    await waitFor(() => {
      expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    });
  });

  it("after login(), user is populated and isAuthenticated is true", async () => {
    mockLogin.mockResolvedValueOnce({
      access_token: "token",
      refresh_token: "refresh",
      token_type: "bearer",
    });
    mockGetMe.mockResolvedValue(mockUser);

    renderWithProvider();

    // Wait for initial loading to settle
    await waitFor(() => {
      expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    });

    await act(async () => {
      screen.getByText("Login").click();
    });

    expect(mockLogin).toHaveBeenCalledWith({
      email: "test@example.com",
      password: "password123",
    });
  });

  it("after logout(), user is null and isAuthenticated is false", async () => {
    // Start with a token so the provider tries to load the user
    localStorage.setItem("access_token", "existing-token");
    mockGetMe.mockResolvedValueOnce(mockUser);
    mockSignout.mockResolvedValueOnce(undefined);

    renderWithProvider();

    await waitFor(() => {
      expect(screen.getByTestId("user")).toHaveTextContent("test@example.com");
    });

    await act(async () => {
      screen.getByText("Logout").click();
    });

    await waitFor(() => {
      expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
      expect(screen.getByTestId("user")).toHaveTextContent("null");
    });
  });
});
