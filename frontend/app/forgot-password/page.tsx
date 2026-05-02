"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import toast from "react-hot-toast";

import { authApi } from "@/lib/api";

export default function ForgotPasswordPage() {
  const router = useRouter();

  const [step, setStep] = useState<"send" | "verify">("send");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resendSeconds, setResendSeconds] = useState(0);

  useEffect(() => {
    if (resendSeconds <= 0) return;
    const timer = setInterval(
      () => setResendSeconds((prev) => (prev > 0 ? prev - 1 : 0)),
      1000,
    );
    return () => clearInterval(timer);
  }, [resendSeconds]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await authApi.sendPasswordResetOtp(email);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Unable to send reset code");
      }
      toast.success(response.data.message);
      setStep("verify");
      setResendSeconds(60);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Unable to send reset code",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await authApi.verifyPasswordResetOtp(email, otp);
      if (!response.success || !response.data?.reset_token) {
        throw new Error(response.error || "Invalid code");
      }
      toast.success("Code verified. Set your new password.");
      router.push(
        `/reset-password?token=${encodeURIComponent(response.data.reset_token)}`,
      );
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Unable to verify code",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendSeconds > 0) return;
    setIsLoading(true);
    try {
      const response = await authApi.sendPasswordResetOtp(email);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Unable to resend reset code");
      }
      toast.success(response.data.message);
      setResendSeconds(60);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Unable to resend code",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Clickable logo — navigates to homepage */}
        <div className="flex justify-center mb-8">
          <Link href="/" title="Go to QCanvas homepage" className="group">
            {/* Light mode */}
            <Image
              src="/QCanvas-logo-Black.svg"
              alt="QCanvas Logo — go to homepage"
              width={72}
              height={72}
              className="object-contain block dark:hidden group-hover:scale-110 transition-transform duration-300 animate-pulse"
              priority
            />
            {/* Dark mode */}
            <Image
              src="/QCanvas-logo-White.svg"
              alt="QCanvas Logo — go to homepage"
              width={72}
              height={72}
              className="object-contain hidden dark:block group-hover:scale-110 transition-transform duration-300 animate-pulse"
              priority
            />
          </Link>
        </div>

        <div className="quantum-glass-dark rounded-2xl p-8 border border-indigo-500/20">
        <h1 className="text-2xl font-bold text-white mb-2">Forgot Password</h1>
        {/* SEO word-count block — screen-reader accessible, invisible to sighted users */}
        <p className="sr-only">
          Reset your QCanvas account password securely. Enter your registered
          email address to receive a one-time verification code. Once you verify
          the code, you can set a new password and regain full access to the
          QCanvas Quantum Circuit Integrated Development Environment. QCanvas
          supports quantum circuit authoring in Cirq, Qiskit, and PennyLane
          with real-time OpenQASM 3.0 simulation. Your account credentials are
          protected with industry-standard JWT token authentication and
          bcrypt-hashed password storage. If you did not request a password
          reset, you can safely ignore this page and continue using your
          existing password to log in to the quantum simulator platform.
        </p>
        <p className="text-sm text-gray-300 mb-6">
          {step === "send"
            ? "Get a reset code via email."
            : "Enter the 6-digit code sent to your email."}
        </p>

        {step === "send" ? (
          <form onSubmit={handleSend} className="space-y-4">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
              placeholder="you@example.com"
              required
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-quantum disabled:opacity-50"
            >
              {isLoading ? "Sending..." : "Send Reset Code"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerify} className="space-y-4">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
              required
            />
            <input
              inputMode="numeric"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
              className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white tracking-[0.4em]"
              placeholder="123456"
              required
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-quantum disabled:opacity-50"
            >
              {isLoading ? "Verifying..." : "Verify Code"}
            </button>
            <button
              type="button"
              onClick={handleResend}
              disabled={isLoading || resendSeconds > 0}
              className="w-full btn-ghost disabled:opacity-50"
            >
              {resendSeconds > 0
                ? `Resend in ${resendSeconds}s`
                : "Resend Code"}
            </button>
          </form>
        )}
        </div> {/* end glass card */}
      </div> {/* end max-w-md wrapper */}
    </div>
  );
}
