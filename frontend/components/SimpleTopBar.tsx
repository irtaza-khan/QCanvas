"use client";

import Link from "next/link";
import Image from "next/image";
import { Moon, Sun } from "lucide-react";
import { useFileStore } from "@/lib/store";
import { useAuthStore } from "@/lib/authStore";
import ProfileDropdown from "./ProfileDropdown";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

export default function SimpleTopBar() {
    const { theme, toggleTheme } = useFileStore();
    const { clearAuth, user } = useAuthStore();
    const router = useRouter();

    const handleLogout = () => {
        const isDemoUser = user?.role === 'demo';

        // Clear auth (includes demo data cleanup if demo user)
        clearAuth();

        // Show appropriate toast message
        if (isDemoUser) {
            toast.success("Demo session ended. All data cleared.");
        } else {
            toast.success("Logged out successfully");
        }

        router.push("/login");
    };

    return (
        <div className="h-14 border-b border-white/10 bg-editor-bg flex items-center justify-between px-4 fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-opacity-90">
            {/* Left: Logo */}
            <div className="flex items-center">
                <Link href="/app" className="flex items-center space-x-3 group">
                    <div className="relative w-8 h-8">
                        <Image
                            src="/QCanvas-logo-Black.svg"
                            alt="QCanvas Logo"
                            fill
                            className="object-contain block dark:hidden transition-transform group-hover:scale-110"
                            priority
                        />
                        <Image
                            src="/QCanvas-logo-White.svg"
                            alt="QCanvas Logo"
                            fill
                            className="object-contain hidden dark:block transition-transform group-hover:scale-110"
                            priority
                        />
                    </div>
                    <span className="font-bold text-xl tracking-tight hidden md:block">
                        <span className="text-white">Q</span>
                        <span className="text-quantum-blue-light">Canvas</span>
                    </span>
                </Link>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center space-x-3">
                {/* Theme Toggle */}
                <button
                    onClick={toggleTheme}
                    className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                    title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                >
                    {theme === 'dark' ? (
                        <Sun className="w-5 h-5" />
                    ) : (
                        <Moon className="w-5 h-5" />
                    )}
                </button>

                <div className="h-6 w-px bg-white/10 mx-1"></div>

                {/* Profile Dropdown */}
                <ProfileDropdown onLogout={handleLogout} />
            </div>
        </div>
    );
}
