import { z } from "zod";

// Zod schema for runtime validation of dashboard data
export const RecentPrepSchema = z.object({
    id: z.string(),
    company_name: z.string(),
    meeting_objective: z.string(),
    meeting_date: z.string().nullable(),
    created_at: z.string(),
    overall_confidence: z.number(),
    outcome_status: z.enum(["completed", "cancelled", "rescheduled"]).nullable(),
});

export type UpcomingPrep = z.infer<typeof RecentPrepSchema>;

const UpcomingMeetingSchema = z.object({
    id: z.string(),
    company_name: z.string(),
    meeting_objective: z.string(),
    meeting_date: z.string(),
});

export type UpcomingMeeting = z.infer<typeof UpcomingMeetingSchema>;

export const DashboardDataSchema = z.object({
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
export type DashboardData = z.infer<typeof DashboardDataSchema>;
