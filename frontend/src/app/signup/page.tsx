"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { BookOpen } from "lucide-react";
import { authService } from "@/services/auth.service";
import { useAuth } from "@/context/auth-context";
import { Button, Input } from "@/components/ui";
import { toast } from "sonner";
import { handleError } from "@/utils/";

export default function SignupPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    full_name: "",
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.email) errs.email = "Email is required";
    if (form.username.length < 3)
      errs.username = "Username must be at least 3 characters";
    if (form.password.length < 8)
      errs.password = "Password must be at least 8 characters";
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
      await authService.signup(form);
      await login(form.email, form.password);
      toast.success("Account created! Welcome to LuminaLib.");
      router.push("/books");
    } catch (err: any) {
      toast.error(handleError(err, "Signup failed"));
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
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-50 to-gray-100 px-4">
      <div className="card w-full max-w-sm p-8">
        <div className="mb-8 flex flex-col items-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 mb-3">
            <BookOpen className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-bold text-gray-900">
            Create your account
          </h1>
        </div>

        <div className="space-y-4">
          <Input
            label="Full Name"
            placeholder="Full Name"
            {...field("full_name")}
          />
          <Input
            label="Email *"
            type="email"
            placeholder="you@example.com"
            {...field("email")}
          />
          <Input
            label="Username *"
            placeholder="username"
            {...field("username")}
          />
          <Input
            label="Password *"
            type="password"
            placeholder="Min. 8 characters"
            {...field("password")}
          />

          <Button className="w-full" isLoading={loading} onClick={handleSubmit}>
            Create Account
          </Button>
        </div>

        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-indigo-600 hover:underline"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
