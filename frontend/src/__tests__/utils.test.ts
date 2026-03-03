import { handleError } from "@/utils";

describe("handleError", () => {
  it("returns detail string when detail is a string", () => {
    const err = { response: { data: { detail: "Email already registered" } } };
    expect(handleError(err, "fallback")).toBe("Email already registered");
  });

  it("returns first msg when detail is an array (FastAPI validation)", () => {
    const err = {
      response: {
        data: {
          detail: [
            { msg: "field required", loc: ["body", "email"] },
            { msg: "invalid email", loc: ["body", "email"] },
          ],
        },
      },
    };
    expect(handleError(err, "fallback")).toBe("field required, invalid email");
  });

  it("returns custom_error_msg for unknown error shape", () => {
    const err = { message: "Network Error" };
    expect(handleError(err, "Something went wrong")).toBe(
      "Something went wrong",
    );
  });

  it("returns custom_error_msg when response is undefined", () => {
    expect(handleError({}, "Default error")).toBe("Default error");
  });
});
