"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface DialogProps {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children: React.ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50"
                onClick={() => onOpenChange?.(false)}
            />
            {/* Dialog content */}
            <div className="relative z-50">
                {children}
            </div>
        </div>
    );
}

interface DialogContentProps {
    className?: string;
    children: React.ReactNode;
}

export function DialogContent({ className, children }: DialogContentProps) {
    return (
        <div
            className={cn(
                "bg-white dark:bg-zinc-900 rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto",
                className
            )}
        >
            {children}
        </div>
    );
}

interface DialogHeaderProps {
    className?: string;
    children: React.ReactNode;
}

export function DialogHeader({ className, children }: DialogHeaderProps) {
    return (
        <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left p-6 pb-4", className)}>
            {children}
        </div>
    );
}

interface DialogTitleProps {
    className?: string;
    children: React.ReactNode;
}

export function DialogTitle({ className, children }: DialogTitleProps) {
    return (
        <h2 className={cn("text-lg font-semibold leading-none tracking-tight", className)}>
            {children}
        </h2>
    );
}

interface DialogDescriptionProps {
    className?: string;
    children: React.ReactNode;
}

export function DialogDescription({ className, children }: DialogDescriptionProps) {
    return (
        <p className={cn("text-sm text-zinc-500 dark:text-zinc-400", className)}>
            {children}
        </p>
    );
}

interface DialogFooterProps {
    className?: string;
    children: React.ReactNode;
}

export function DialogFooter({ className, children }: DialogFooterProps) {
    return (
        <div className={cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 p-6 pt-4", className)}>
            {children}
        </div>
    );
}

interface DialogCloseProps {
    onClick?: () => void;
    className?: string;
    children?: React.ReactNode;
}

export function DialogClose({ onClick, className, children }: DialogCloseProps) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-zinc-950 focus:ring-offset-2 disabled:pointer-events-none",
                className
            )}
        >
            {children || <X className="h-4 w-4" />}
            <span className="sr-only">Close</span>
        </button>
    );
}
