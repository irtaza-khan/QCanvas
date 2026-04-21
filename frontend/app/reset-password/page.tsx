"use client";

import { Suspense, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import toast from "react-hot-toast";

import { authApi } from "@/lib/api";

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resetToken = useMemo(
    () => searchParams.get("token") || "",
    [searchParams],
  );

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!resetToken) {
      toast.error("Missing reset token. Restart the password reset process.");
      return;
    }

    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setIsLoading(true);
    try {
      const response = await authApi.completePasswordReset(
        resetToken,
        newPassword,
        confirmPassword,
      );
      if (!response.success || !response.data) {
        throw new Error(response.error || "Unable to reset password");
      }
      toast.success("Password reset successful. Please sign in.");
      router.push("/login");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Unable to reset password",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center p-4">
      <div className="w-full max-w-md quantum-glass-dark rounded-2xl p-8 border border-indigo-500/20">
        <h1 className="text-2xl font-bold text-white mb-2">Set New Password</h1>
        <p className="text-sm text-gray-300 mb-6">
          Choose a new password for your account.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
            placeholder="New password"
            required
          />

          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
            placeholder="Confirm password"
            required
          />

          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-quantum disabled:opacity-50"
          >
            {isLoading ? "Updating..." : "Update Password"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0a0a1a]" />}>
      <ResetPasswordContent />
    </Suspense>
  );
}
