import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

export type StatusType = "success" | "error" | "info";

interface StatusBarProps {
  message?: string;
  type?: StatusType;
  isVisible?: boolean;
  onClose?: () => void;
  autoHideDuration?: number;
  className?: string;
}

export function StatusBar({
  message,
  type = "success",
  isVisible = false,
  onClose,
  autoHideDuration = 3000,
  className,
}: StatusBarProps) {
  const [shouldShow, setShouldShow] = useState(isVisible);

  useEffect(() => {
    setShouldShow(isVisible);
  }, [isVisible]);

  useEffect(() => {
    if (shouldShow && autoHideDuration > 0) {
      const timer = setTimeout(() => {
        setShouldShow(false);
        onClose?.();
      }, autoHideDuration);

      return () => clearTimeout(timer);
    }
  }, [shouldShow, autoHideDuration, onClose]);

  if (!shouldShow || !message) {
    return null;
  }

  const getStatusClasses = () => {
    switch (type) {
      case "success":
        return "bg-green-500";
      case "error":
        return "bg-red-500";
      case "info":
        return "bg-blue-500";
      default:
        return "bg-green-500";
    }
  };

  return (
    <div
      className={cn(
        "text-white px-4 py-2 text-center text-sm font-medium",
        getStatusClasses(),
        className,
      )}
    >
      {message}
    </div>
  );
}
