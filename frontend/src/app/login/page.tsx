"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { Button, Input } from "@/components/ui";
import { toast } from "sonner";
import { handleError } from "@/utils/";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.email) errs.email = "Email is required";
    if (!form.password) errs.password = "Password is required";
    return errs;
  };

  const handleSubmit = async () => {
    const errs = validate();
    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }
    setLoading(true);
    try {
      await login(form.email, form.password);
      router.push("/books");
    } catch (err: any) {
      toast.error(handleError(err, "Invalid credentials"));
    } finally {
      setLoading(false);
    }
  };

  const field = (key: keyof typeof form) => ({
    value: form[key],
    error: errors[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
      setForm((f) => ({ ...f, [key]: e.target.value }));
      setErrors((e) => {
        const next = { ...e };
        delete next[key];
        return next;
      });
    },
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === "Enter") handleSubmit();
    },
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-50 to-gray-100 px-4">
      <div className="card w-full max-w-sm p-8">
        <div className="mb-8 flex flex-col items-center">
          <h1 className="text-xl font-bold text-gray-900">
            Welcome to LuminaLib
          </h1>
          <p className="text-sm text-gray-500">Sign in to your account</p>
        </div>

        <div className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            {...field("email")}
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            {...field("password")}
          />

          <Button className="w-full" isLoading={loading} onClick={handleSubmit}>
            Sign in
          </Button>
        </div>

        <p className="mt-6 text-center text-sm text-gray-500">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="font-medium text-indigo-600 hover:underline"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
