"use client";

import useSWR from "swr";
import { useAuth } from "@/components/providers/auth-provider";

const fetcher = async (url: string, accessToken: string) => {
    const response = await fetch(url, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({
            detail: "Failed to fetch dashboard data",
        }));
        throw new Error(error.detail || "Failed to fetch dashboard data");
    }

    return response.json();
};

export function useDashboard() {
    const { session } = useAuth();

    const shouldFetch = !!session?.access_token;

    const { data, error, isLoading, isValidating, mutate } = useSWR(
        shouldFetch
            ? `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/dashboard`
            : null,
        shouldFetch
            ? (url: string) => fetcher(url, session.access_token)
            : null,
        {
            revalidateOnFocus: true,
            revalidateOnReconnect: true,
            refreshInterval: 0,
        }
    );

    return {
        data,
        error: error ? (error as Error).message : null,
        isLoading,
        isValidating,
        refresh: mutate,
    };
}
