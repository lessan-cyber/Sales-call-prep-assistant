"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface RecordOutcomeProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    prepId: string;
    onSuccess?: () => void;
}

type MeetingStatus = "completed" | "cancelled" | "rescheduled";
type MeetingOutcome = "successful" | "needs_improvement" | "lost_opportunity";
type PrepSection = "executive_summary" | "talking_points" | "questions" | "decision_makers" | "company_intelligence";

export function RecordOutcome({ open, onOpenChange, prepId, onSuccess }: RecordOutcomeProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Form state
    const [meetingStatus, setMeetingStatus] = useState<MeetingStatus>("completed");
    const [outcome, setOutcome] = useState<MeetingOutcome | "">("");
    const [prepAccuracy, setPrepAccuracy] = useState<number>(3);
    const [mostUsefulSection, setMostUsefulSection] = useState<PrepSection | "">("");
    const [whatWasMissing, setWhatWasMissing] = useState("");
    const [generalNotes, setGeneralNotes] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/preps/${prepId}/outcome`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    meeting_status: meetingStatus,
                    outcome: outcome || undefined,
                    prep_accuracy: prepAccuracy || undefined,
                    most_useful_section: mostUsefulSection || undefined,
                    what_was_missing: whatWasMissing || undefined,
                    general_notes: generalNotes || undefined,
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Failed to record outcome");
            }

            // Reset form
            setMeetingStatus("completed");
            setOutcome("");
            setPrepAccuracy(3);
            setMostUsefulSection("");
            setWhatWasMissing("");
            setGeneralNotes("");

            onOpenChange(false);
            onSuccess?.();
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        if (!loading) {
            onOpenChange(false);
            setError(null);
        }
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>Record Meeting Outcome</DialogTitle>
                    <DialogDescription>
                        Help us improve by sharing how this meeting went. This information is used to calculate your success rate.
                    </DialogDescription>
                    <DialogClose onClick={handleClose} />
                </DialogHeader>

                <form onSubmit={handleSubmit}>
                    <div className="grid gap-6 py-4">
                        {/* Meeting Status */}
                        <div className="grid gap-2">
                            <Label htmlFor="meeting-status">Meeting Status *</Label>
                            <select
                                id="meeting-status"
                                className="flex h-10 w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:bg-zinc-950 dark:ring-offset-zinc-950 dark:placeholder:text-zinc-400 dark:focus-visible:ring-zinc-300"
                                value={meetingStatus}
                                onChange={(e) => setMeetingStatus(e.target.value as MeetingStatus)}
                                required
                            >
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                                <option value="rescheduled">Rescheduled</option>
                            </select>
                        </div>

                        {/* Outcome - only show if meeting was completed */}
                        {meetingStatus === "completed" && (
                            <div className="grid gap-2">
                                <Label htmlFor="outcome">Overall Outcome</Label>
                                <select
                                    id="outcome"
                                    className="flex h-10 w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:bg-zinc-950 dark:ring-offset-zinc-950 dark:placeholder:text-zinc-400 dark:focus-visible:ring-zinc-300"
                                    value={outcome}
                                    onChange={(e) => setOutcome(e.target.value as MeetingOutcome | "")}
                                >
                                    <option value="">Select outcome...</option>
                                    <option value="successful">Successful 🎉</option>
                                    <option value="needs_improvement">Needs Improvement 🔄</option>
                                    <option value="lost_opportunity">Lost Opportunity ❌</option>
                                </select>
                                <p className="text-xs text-zinc-500">
                                    This helps calculate your success rate
                                </p>
                            </div>
                        )}

                        {/* Prep Accuracy - only show if outcome is selected */}
                        {meetingStatus === "completed" && outcome && (
                            <div className="grid gap-2">
                                <Label htmlFor="prep-accuracy">
                                    How accurate was the prep? (1-5 scale)
                                </Label>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-zinc-500">1</span>
                                    <input
                                        type="range"
                                        id="prep-accuracy"
                                        min="1"
                                        max="5"
                                        value={prepAccuracy}
                                        onChange={(e) => setPrepAccuracy(parseInt(e.target.value))}
                                        className="flex-1"
                                    />
                                    <span className="text-sm text-zinc-500">5</span>
                                </div>
                                <div className="text-center">
                                    <span className="text-sm font-medium">{prepAccuracy}</span>
                                    <span className="text-xs text-zinc-500 ml-1">
                                        {prepAccuracy <= 2 ? "Not very accurate" :
                                         prepAccuracy <= 3 ? "Somewhat accurate" :
                                         prepAccuracy <= 4 ? "Quite accurate" : "Very accurate"}
                                    </span>
                                </div>
                            </div>
                        )}

                        {/* Most Useful Section - only show if outcome is selected */}
                        {meetingStatus === "completed" && outcome && (
                            <div className="grid gap-2">
                                <Label htmlFor="most-useful-section">
                                    Most Useful Section
                                </Label>
                                <select
                                    id="most-useful-section"
                                    className="flex h-10 w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:bg-zinc-950 dark:ring-offset-zinc-950 dark:placeholder:text-zinc-400 dark:focus-visible:ring-zinc-300"
                                    value={mostUsefulSection}
                                    onChange={(e) => setMostUsefulSection(e.target.value as PrepSection | "")}
                                >
                                    <option value="">Select section...</option>
                                    <option value="executive_summary">Executive Summary</option>
                                    <option value="talking_points">Talking Points</option>
                                    <option value="questions">Questions to Ask</option>
                                    <option value="decision_makers">Decision Makers</option>
                                    <option value="company_intelligence">Company Intelligence</option>
                                </select>
                            </div>
                        )}

                        {/* What Was Missing */}
                        {meetingStatus === "completed" && outcome && (
                            <div className="grid gap-2">
                                <Label htmlFor="what-missing">
                                    What was missing from the prep?
                                </Label>
                                <Textarea
                                    id="what-missing"
                                    placeholder="e.g., More information about their pricing, competitor analysis, etc."
                                    value={whatWasMissing}
                                    onChange={(e) => setWhatWasMissing(e.target.value)}
                                    rows={3}
                                />
                            </div>
                        )}

                        {/* General Notes */}
                        {meetingStatus === "completed" && outcome && (
                            <div className="grid gap-2">
                                <Label htmlFor="general-notes">
                                    General Notes
                                </Label>
                                <Textarea
                                    id="general-notes"
                                    placeholder="Any additional thoughts about the meeting..."
                                    value={generalNotes}
                                    onChange={(e) => setGeneralNotes(e.target.value)}
                                    rows={4}
                                />
                            </div>
                        )}

                        {/* Error Message */}
                        {error && (
                            <div className="rounded-md bg-red-50 p-3">
                                <p className="text-sm text-red-800">{error}</p>
                            </div>
                        )}
                    </div>

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={handleClose}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? "Recording..." : "Record Outcome"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
