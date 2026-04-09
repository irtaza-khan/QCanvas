"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import toast from "react-hot-toast";

import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/authStore";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAuth, setLoading } = useAuthStore();

  const initialEmail = useMemo(
    () => searchParams.get("email") || "",
    [searchParams],
  );
  const [email, setEmail] = useState(initialEmail);
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resendSeconds, setResendSeconds] = useState(0);

  useEffect(() => {
    if (!initialEmail) return;
    setEmail(initialEmail);
  }, [initialEmail]);

  useEffect(() => {
    if (resendSeconds <= 0) return;
    const timer = setInterval(() => {
      setResendSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [resendSeconds]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || otp.length !== 6) {
      toast.error("Enter your email and 6-digit OTP code");
      return;
    }

    setIsLoading(true);
    setLoading(true);
    try {
      const response = await authApi.verifySignupOtp(email, otp);
      if (
        !response.success ||
        !response.data ||
        !response.data.access_token ||
        !response.data.user
      ) {
        throw new Error(response.error || "OTP verification failed");
      }

      setAuth(response.data.user, response.data.access_token);
      toast.success("Email verified successfully");
      router.push("/app");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Verification failed",
      );
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (!email) {
      toast.error("Enter email first");
      return;
    }

    setIsLoading(true);
    try {
      const response = await authApi.resendSignupOtp(email);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Resend failed");
      }
      setResendSeconds(response.data.cooldown_seconds || 60);
      toast.success(response.data.message);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Unable to resend OTP",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center p-4">
      <div className="w-full max-w-md quantum-glass-dark rounded-2xl p-8 border border-indigo-500/20">
        <h1 className="text-2xl font-bold text-white mb-2">Verify Email</h1>
        <p className="text-sm text-gray-300 mb-6">
          Enter the 6-digit code sent to your email.
        </p>

        <form onSubmit={handleVerify} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">OTP Code</label>
            <input
              inputMode="numeric"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white tracking-[0.4em]"
              placeholder="123456"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-quantum disabled:opacity-50"
          >
            {isLoading ? "Verifying..." : "Verify Email"}
          </button>
        </form>

        <button
          onClick={handleResend}
          disabled={isLoading || resendSeconds > 0}
          className="w-full mt-3 btn-ghost disabled:opacity-50"
        >
          {resendSeconds > 0 ? `Resend in ${resendSeconds}s` : "Resend Code"}
        </button>

        <p className="text-xs text-gray-400 mt-4 text-center">
          Wrong email?{" "}
          <a href="/signup" className="text-indigo-400">
            Create account again
          </a>
        </p>
      </div>
    </div>
  );
}
