"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDashboard } from "@/hooks/useDashboard";

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
    const [validationError, setValidationError] = useState(false);

    // Use SWR hook for data fetching and caching
    const { data: dashboardData, error, isLoading, isValidating, refresh } = useDashboard();

    // Validate the response data using Zod
    const validationResult = dashboardData
        ? DashboardDataSchema.safeParse(dashboardData)
        : null;

    // Set validation error in useEffect to avoid state update during render
    useEffect(() => {
        if (validationResult && !validationResult.success) {
            console.error(
                "Dashboard data validation failed",
                validationResult.error.format()
            );
            setValidationError(true);
        } else {
            setValidationError(false);
        }
    }, [validationResult]);

    // Use validated data if validation succeeds, otherwise use raw data
    const dataToRender = validationResult?.success ? validationResult.data : dashboardData;

    const handleCreateNewPrep = () => {
        router.push("/new-prep");
    };

    const handleRetry = () => {
        refresh();
    };

    const handleViewPrep = (prepId: string) => {
        router.push(`/prep/${prepId}`);
    };

    // Get local date in YYYY-MM-DD format (not UTC)
    const getLocalDateString = () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Filter meetings by date
    const today = getLocalDateString();
    const todayMeetings = (dataToRender?.upcoming_meetings || []).filter(
        (meeting: any) => meeting.meeting_date === today
    );
    const futureMeetings = (dataToRender?.upcoming_meetings || []).filter(
        (meeting: any) => meeting.meeting_date > today
    );

    // Filter preps for the table sections
    // Upcoming preps: meeting date is today or in the future
    const upcomingPreps = (dataToRender?.recent_preps || []).filter(
        (prep: any) => prep.meeting_date && prep.meeting_date >= today
    );

    // Old preps: meeting date has passed (yesterday or earlier)
    const oldPreps = (dataToRender?.recent_preps || []).filter(
        (prep: any) => prep.meeting_date && prep.meeting_date < today
    );

    if (isLoading) {
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
                        <Button onClick={handleRetry} className="mt-4 cursor-pointer">
                            Retry
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (!dataToRender) {
        return null;
    }

    // Empty state - no preps yet
    if (dataToRender.total_preps === 0) {
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
                    <Button size="lg" onClick={handleCreateNewPrep} className="cursor-pointer">
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
                <div className="flex items-center gap-2">
                    <p className="text-zinc-600">
                        Track your sales prep performance and upcoming meetings.
                    </p>
                    {isValidating && (
                        <div className="flex items-center gap-2 text-sm text-zinc-500">
                            <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
                            <span>Updating...</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Validation Warning Banner */}
            {validationError && (
                <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                    <div className="flex items-start">
                        <div className="flex-shrink-0">
                            <svg
                                className="h-5 w-5 text-yellow-400"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                    clipRule="evenodd"
                                />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-yellow-800">
                                Data validation warning
                            </h3>
                            <div className="mt-1 text-sm text-yellow-700">
                                <p>
                                    Some dashboard data may be incomplete or malformed. Displaying fallback
                                    data. Please refresh if you notice any issues.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

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
                            {dataToRender.total_preps}
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
                            {dataToRender.success_rate}%
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                            {dataToRender.total_successful} of{" "}
                            {dataToRender.total_completed} meetings
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
                                {dataToRender.avg_confidence.toFixed(2)}
                            </div>
                            <Badge
                                className={getConfidenceColor(
                                    dataToRender.avg_confidence,
                                )}
                            >
                                {getConfidenceLabel(
                                    dataToRender.avg_confidence,
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
                            {dataToRender.time_saved_hours}h
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                            ~{dataToRender.time_saved_minutes} minutes saved
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Today's Meetings Section */}
            {todayMeetings.length > 0 && (
                <div className="mb-8">
                    <div className="flex items-center gap-2 mb-4">
                        <h2 className="text-xl font-bold">Today</h2>
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            {todayMeetings.length} meeting{todayMeetings.length > 1 ? 's' : ''}
                        </span>
                    </div>
                    <div className="grid gap-4">
                        {todayMeetings.map((meeting: any) => (
                            <Card
                                key={meeting.id}
                                className="hover:shadow-md transition-shadow border-l-4 border-l-blue-500"
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
                                                    📅 {new Date(meeting.meeting_date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                                                </span>
                                            </div>
                                        </div>
                                        <Button
                                            variant="default"
                                            onClick={() =>
                                                handleViewPrep(meeting.id)
                                            }
                                            className="cursor-pointer"
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

            {/* Upcoming Meetings Section */}
            {futureMeetings.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-xl font-bold mb-4">
                        Upcoming
                    </h2>
                    <p className="text-sm text-zinc-500 mb-4">
                        Future meetings (next 7 days)
                    </p>
                    <div className="grid gap-4">
                        {futureMeetings.map((meeting: any) => (
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
                                            className="cursor-pointer"
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

            {/* Upcoming Preps Table */}
            {upcomingPreps.length > 0 && (
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold">Upcoming Preps</h2>
                        <Button onClick={handleCreateNewPrep} className="cursor-pointer">
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
                                                Meeting Date
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
                                        {upcomingPreps.map((prep: any) => (
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
                                                    {formatDate(prep.meeting_date)}
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
                                                        className="cursor-pointer"
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
            )}

            {/* Old Preps Table */}
            {oldPreps.length > 0 && (
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold">Old Preps</h2>
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
                                                Meeting Date
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
                                        {oldPreps.map((prep: any) => (
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
                                                    {formatDate(prep.meeting_date)}
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
                                                        className="cursor-pointer"
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
            )}
        </div>
    );
}
