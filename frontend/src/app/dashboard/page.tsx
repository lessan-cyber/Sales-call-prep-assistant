"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { createClient } from "@/lib/supabase/client";
import { error as loggerError } from "@/lib/logger";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// Zod schema for runtime validation of dashboard data
const RecentPrepSchema = z.object({
    id: z.string(),
    company_name: z.string(),
    meeting_objective: z.string(),
    meeting_date: z.string().nullable(),
    created_at: z.string(),
    overall_confidence: z.number(),
    outcome_status: z.enum(["completed", "cancelled", "rescheduled"]).nullable(),
});

const UpcomingMeetingSchema = z.object({
    id: z.string(),
    company_name: z.string(),
    meeting_objective: z.string(),
    meeting_date: z.string(),
});

const DashboardDataSchema = z.object({
    total_preps: z.number(),
    success_rate: z.number(),
    total_successful: z.number(),
    total_completed: z.number(),
    avg_confidence: z.number(),
    time_saved_hours: z.number(),
    time_saved_minutes: z.number(),
    recent_preps: z.array(RecentPrepSchema),
    upcoming_meetings: z.array(UpcomingMeetingSchema),
});

// TypeScript type inferred from Zod schema for type safety
type DashboardData = z.infer<typeof DashboardDataSchema>;

// Confidence score thresholds for UI classification
const CONFIDENCE_HIGH = 0.8;
const CONFIDENCE_MEDIUM = 0.6;

function getConfidenceColor(confidence: number): string {
    if (confidence >= CONFIDENCE_HIGH) return "bg-green-100 text-green-800";
    if (confidence >= CONFIDENCE_MEDIUM) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
}

function getConfidenceLabel(confidence: number): string {
    if (confidence >= CONFIDENCE_HIGH) return "High";
    if (confidence >= CONFIDENCE_MEDIUM) return "Medium";
    return "Low";
}

function getOutcomeBadgeVariant(outcomeStatus: string | null) {
    switch (outcomeStatus) {
        case "completed":
            return "default";
        case "cancelled":
            return "destructive";
        case "rescheduled":
            return "secondary";
        default:
            return "outline";
    }
}

function getOutcomeBadgeLabel(outcomeStatus: string | null) {
    switch (outcomeStatus) {
        case "completed":
            return "Completed";
        case "cancelled":
            return "Cancelled";
        case "rescheduled":
            return "Rescheduled";
        default:
            return "Pending";
    }
}

function formatDate(dateString: string): string {
    const date = new Date(dateString);

    // Validate that the date is valid
    if (isNaN(date.getTime())) {
        console.warn("Invalid date string:", dateString);
        return "Invalid date";
    }

    return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
    });
}

function formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);

    // Validate that the date is valid
    if (isNaN(date.getTime())) {
        console.warn("Invalid date string for relative time:", dateString);
        return "Invalid date";
    }

    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    // Guard against future dates or invalid time differences
    if (diffInSeconds < 0) {
        // Date is in the future, fall back to formatted date
        return formatDate(dateString);
    }

    if (diffInSeconds < 60) return "Just now";
    if (diffInSeconds < 3600)
        return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400)
        return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 2592000)
        return `${Math.floor(diffInSeconds / 86400)} days ago`;
    return formatDate(dateString);
}

export default function DashboardPage() {
    const router = useRouter();
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(
        null,
    );
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        // Create AbortController for cleanup on unmount
        const abortController = new AbortController();

        fetchDashboardData(abortController.signal);

        // Cleanup function: abort the request if component unmounts
        return () => {
            abortController.abort();
        };
    }, []);

    const fetchDashboardData = async (signal?: AbortSignal) => {
        try {
            setLoading(true);
            const supabase = createClient();

            // Get session
            const {
                data: { session },
            } = await supabase.auth.getSession();
            if (!session) {
                router.push("/login");
                return;
            }

            // Fetch dashboard data
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/dashboard`,
                {
                    headers: {
                        Authorization: `Bearer ${session?.access_token}`,
                    },
                    signal, // Pass the abort signal
                },
            );

            if (!response.ok) {
                throw new Error("Failed to fetch dashboard data");
            }

            const rawData = await response.json();

            // Validate the response data using Zod
            const validationResult = DashboardDataSchema.safeParse(rawData);

            if (!validationResult.success) {
                // Log the validation errors
                loggerError(
                    "Dashboard data validation failed",
                    { validationErrors: validationResult.error.format() }
                );
                throw new Error(
                    "Invalid dashboard data received from server",
                );
            }

            // Validation successful, use the validated data
            const validatedData = validationResult.data;

            // Convert string dates to Date objects if needed for runtime processing
            // Note: We keep them as strings since the UI components expect strings
            // but the schema ensures they are valid date strings
            setDashboardData(validatedData);
        } catch (err) {
            // Check if the request was aborted
            if (err instanceof Error && err.name === "AbortError") {
                // Request was aborted due to component unmount, silently return
                return;
            }

            loggerError("Error fetching dashboard", { error: err });
            setError(
                err instanceof Error ? err.message : "Failed to load dashboard",
            );
        } finally {
            setLoading(false);
        }
    };

    const handleCreateNewPrep = () => {
        router.push("/new-prep");
    };

    const handleRetry = () => {
        fetchDashboardData();
    };

    const handleViewPrep = (prepId: string) => {
        router.push(`/prep/${prepId}`);
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex items-center justify-center min-h-[400px]">
                    <p className="text-lg">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto px-4 py-8">
                <Card>
                    <CardContent className="pt-6">
                        <p className="text-red-600">{error}</p>
                        <Button onClick={handleRetry} className="mt-4">
                            Retry
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (!dashboardData) {
        return null;
    }

    // Empty state - no preps yet
    if (dashboardData.total_preps === 0) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="max-w-2xl mx-auto text-center py-16">
                    <h1 className="text-4xl font-bold mb-4">
                        Welcome to Your Dashboard
                    </h1>
                    <p className="text-xl text-zinc-600 mb-8">
                        Create your first sales prep to get started and see
                        insights here.
                    </p>
                    <Button size="lg" onClick={handleCreateNewPrep}>
                        Create Your First Prep
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-7xl">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
                <p className="text-zinc-600">
                    Track your sales prep performance and upcoming meetings.
                </p>
            </div>

            {/* Stats Overview - 4 Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-600">
                            Total Preps
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {dashboardData.total_preps}
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                            All time preps created
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-600">
                            Success Rate
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {dashboardData.success_rate}%
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                            {dashboardData.total_successful} of{" "}
                            {dashboardData.total_completed} meetings
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-600">
                            Avg Confidence
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2">
                            <div className="text-3xl font-bold">
                                {dashboardData.avg_confidence.toFixed(2)}
                            </div>
                            <Badge
                                className={getConfidenceColor(
                                    dashboardData.avg_confidence,
                                )}
                            >
                                {getConfidenceLabel(
                                    dashboardData.avg_confidence,
                                )}
                            </Badge>
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                            Overall prep quality
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-600">
                            Est. Time Saved
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {dashboardData.time_saved_hours}h
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                            ~{dashboardData.time_saved_minutes} minutes saved
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Upcoming Meetings Section */}
            {dashboardData.upcoming_meetings.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-xl font-bold mb-4">
                        Upcoming Meetings (Next 7 Days)
                    </h2>
                    <div className="grid gap-4">
                        {dashboardData.upcoming_meetings.map((meeting) => (
                            <Card
                                key={meeting.id}
                                className="hover:shadow-md transition-shadow"
                            >
                                <CardContent className="pt-6">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-lg">
                                                {meeting.company_name}
                                            </h3>
                                            <p className="text-zinc-600 mt-1 line-clamp-2">
                                                {meeting.meeting_objective}
                                            </p>
                                            <div className="mt-3 flex items-center gap-4 text-sm text-zinc-500">
                                                <span>
                                                    📅{" "}
                                                    {formatDate(
                                                        meeting.meeting_date,
                                                    )}
                                                </span>
                                            </div>
                                        </div>
                                        <Button
                                            variant="outline"
                                            onClick={() =>
                                                handleViewPrep(meeting.id)
                                            }
                                        >
                                            View Prep
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            )}

            {/* Recent Preps Table */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold">Recent Preps</h2>
                    <Button onClick={handleCreateNewPrep}>
                        Create New Prep
                    </Button>
                </div>

                <Card>
                    <CardContent className="p-0">
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="border-b">
                                    <tr>
                                        <th className="text-left p-4 font-medium text-zinc-500">
                                            Company
                                        </th>
                                        <th className="text-left p-4 font-medium text-zinc-500">
                                            Objective
                                        </th>
                                        <th className="text-left p-4 font-medium text-zinc-500">
                                            Created
                                        </th>
                                        <th className="text-left p-4 font-medium text-zinc-500">
                                            Confidence
                                        </th>
                                        <th className="text-left p-4 font-medium text-zinc-500">
                                            Status
                                        </th>
                                        <th className="text-left p-4 font-medium text-zinc-500">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {dashboardData.recent_preps.map((prep) => (
                                        <tr
                                            key={prep.id}
                                            className="border-b hover:bg-neutral-800 transition-colors"
                                        >
                                            <td className="p-4 font-medium text-zinc-200">
                                                {prep.company_name}
                                            </td>
                                            <td className="p-4">
                                                <p className="max-w-md truncate text-zinc-200">
                                                    {prep.meeting_objective}
                                                </p>
                                            </td>
                                            <td className="p-4 text-zinc-500">
                                                {formatRelativeTime(
                                                    prep.created_at,
                                                )}
                                            </td>
                                            <td className="p-4">
                                                <Badge
                                                    className={getConfidenceColor(
                                                        prep.overall_confidence,
                                                    )}
                                                >
                                                    {getConfidenceLabel(
                                                        prep.overall_confidence,
                                                    )}{" "}
                                                    (
                                                    {prep.overall_confidence.toFixed(
                                                        2,
                                                    )}
                                                    )
                                                </Badge>
                                            </td>
                                            <td className="p-4">
                                                <Badge variant={getOutcomeBadgeVariant(prep.outcome_status)}>
                                                    {getOutcomeBadgeLabel(prep.outcome_status)}
                                                </Badge>
                                            </td>
                                            <td className="p-4">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() =>
                                                        handleViewPrep(prep.id)
                                                    }
                                                    aria-label={`View prep for ${prep.company_name}`}
                                                >
                                                    View
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
