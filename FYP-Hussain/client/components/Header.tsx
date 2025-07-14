import React from "react";
import { cn } from "@/lib/utils";

interface HeaderProps {
  className?: string;
}

export function Header({ className }: HeaderProps) {
  return (
    <header
      className={cn(
        "quantum-glass border-b border-white/20 p-4 md:px-8 shadow-[0_2px_20px_rgba(0,0,0,0.1)]",
        className,
      )}
    >
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="quantum-logo-text text-3xl font-bold">QSIM</div>
        <nav>
          <ul className="flex gap-4 md:gap-8 list-none">
            <li>
              <a
                href="#home"
                className="text-gray-600 font-medium transition-colors duration-300 hover:text-quantum-purple-start no-underline"
              >
                Home
              </a>
            </li>
            <li>
              <a
                href="#docs"
                className="text-gray-600 font-medium transition-colors duration-300 hover:text-quantum-purple-start no-underline"
              >
                Documentation
              </a>
            </li>
            <li>
              <a
                href="#examples"
                className="text-gray-600 font-medium transition-colors duration-300 hover:text-quantum-purple-start no-underline"
              >
                Examples
              </a>
            </li>
            <li>
              <a
                href="#about"
                className="text-gray-600 font-medium transition-colors duration-300 hover:text-quantum-purple-start no-underline"
              >
                About
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
