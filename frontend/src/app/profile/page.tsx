"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { UserProfile, PortfolioItem } from "@/types/user_profile";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Trash2, Edit2, Mail, Building2, Tag, X } from "lucide-react";
import { useAuth } from "@/components/providers/auth-provider";
import { LogOut } from "lucide-react";

const MIN_PORTFOLIO_ITEMS = 5;
const MAX_PORTFOLIO_ITEMS = 20;

export default function ProfilePage() {
    const router = useRouter();
    const { user, loading, profileLoading, session, logout } = useAuth();
    const [isEditMode, setIsEditMode] = useState(false);
    const [formState, setFormState] = useState<UserProfile>({
        company_name: "",
        company_description: "",
        industries_served: [],
        portfolio: Array(MIN_PORTFOLIO_ITEMS)
            .fill(null)
            .map(() => ({
                name: "",
                client_industry: "",
                description: "",
                key_outcomes: "",
            })),
    });
    const [error, setError] = useState<string | null>(null);
    const isFormInitialized = useRef(false);

    useEffect(() => {
        // Wait for both auth loading and profile loading to complete
        if (!loading && !profileLoading) {
            if (!session) {
                router.push("/login");
            } else if (user) {
                // If form is not initialized, populate with user data
                if (!isFormInitialized.current) {
                    setFormState(user);
                    isFormInitialized.current = true;
                    // Existing user with profile starts in view mode
                    setIsEditMode(false);
                }
            } else {
                // User is logged in but has no profile, initialize form for creation
                // Only if not already initialized to prevent resetting user input
                if (!isFormInitialized.current) {
                    setFormState({
                        company_name: "",
                        company_description: "",
                        industries_served: [],
                        portfolio: Array(MIN_PORTFOLIO_ITEMS)
                            .fill(null)
                            .map(() => ({
                                name: "",
                                client_industry: "",
                                description: "",
                                key_outcomes: "",
                            })),
                    });
                    isFormInitialized.current = true;
                    // New user without profile starts in edit mode
                    setIsEditMode(true);
                }
            }
        }
    }, [loading, profileLoading, session, user]);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
    ) => {
        const { id, value } = e.target;
        setFormState((prev) => ({ ...prev, [id]: value }));
    };

    const handleIndustriesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { value } = e.target;
        setFormState((prev) => ({
            ...prev,
            industries_served: value.split(",").map((s) => s.trim()),
        }));
    };

    const handlePortfolioChange = (
        index: number,
        field: keyof PortfolioItem,
        value: string,
    ) => {
        const updatedPortfolio = [...formState.portfolio];
        updatedPortfolio[index] = {
            ...updatedPortfolio[index],
            [field]: value,
        };
        setFormState((prev) => ({ ...prev, portfolio: updatedPortfolio }));
    };

    const addProject = () => {
        setFormState((prev) => {
            // Prevent adding more than MAX_PORTFOLIO_ITEMS items
            if (prev.portfolio.length >= MAX_PORTFOLIO_ITEMS) {
                return prev;
            }
            return {
                ...prev,
                portfolio: [
                    ...prev.portfolio,
                    {
                        name: "",
                        client_industry: "",
                        description: "",
                        key_outcomes: "",
                    },
                ],
            };
        });
    };

    const removeProject = (index: number) => {
        if (formState.portfolio.length > MIN_PORTFOLIO_ITEMS) {
            const updatedPortfolio = formState.portfolio.filter(
                (_, i) => i !== index,
            );
            setFormState((prev) => ({ ...prev, portfolio: updatedPortfolio }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        // setLoading(true); // AuthProvider handles global loading

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/auth/profile`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${session?.access_token}`,
                    },
                    body: JSON.stringify(formState),
                },
            );

            if (!response.ok) {
                let errorMessage = "Failed to save profile";
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    // If response is not JSON, use a generic error message
                    errorMessage = `Server error: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            alert("Profile saved successfully!");
            // Redirect to dashboard after successful save
            router.push("/dashboard");
        } catch (err: any) {
            setError(err.message);
        } finally {
            // setLoading(false); // AuthProvider handles global loading
        }
    };

    const handleCancel = () => {
        // Reset form state to current user data and exit edit mode
        if (user) {
            setFormState(user);
        }
        setIsEditMode(false);
        setError(null);
    };

    if (loading || profileLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <p>Loading profile...</p>
            </div>
        );
    }

    // View Mode: Show settings-style layout for users with existing profiles
    if (!isEditMode && user) {
        return (
            <div className="container mx-auto p-4 sm:p-6 md:p-8 max-w-4xl">
                {/* Header */}
                <div className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Profile Settings</h1>
                        <p className="text-muted-foreground">
                            Manage your account and portfolio information
                        </p>
                    </div>
                    <Button
                        onClick={() => setIsEditMode(true)}
                        className="flex items-center gap-2 cursor-pointer"
                    >
                        <Edit2 className="h-4 w-4" />
                        Edit Profile
                    </Button>
                </div>

                <div className="space-y-6">
                    {/* Account Information */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Mail className="h-5 w-5" />
                                Account Information
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <Label className="text-sm font-medium text-muted-foreground">
                                    Email
                                </Label>
                                <p className="mt-1">
                                    {session?.user?.email || "Not available"}
                                </p>
                            </div>
                            <div className="pt-4">
                                <Button
                                    variant="destructive"
                                    onClick={logout}
                                    className="flex items-center gap-2 cursor-pointer"
                                >
                                    <LogOut className="h-4 w-4" />
                                    Log Out
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Company Information */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Building2 className="h-5 w-5" />
                                Company Information
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <Label className="text-sm font-medium text-muted-foreground">
                                    Company Name
                                </Label>
                                <p className="mt-1 font-medium">
                                    {user.company_name || "Not set"}
                                </p>
                            </div>
                            <div>
                                <Label className="text-sm font-medium text-muted-foreground">
                                    Company Description
                                </Label>
                                <p className="mt-1">
                                    {user.company_description ||
                                        "No description"}
                                </p>
                            </div>
                            <div>
                                <Label className="text-sm font-medium text-muted-foreground">
                                    Industries Served
                                </Label>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {user.industries_served &&
                                    user.industries_served.length > 0 ? (
                                        user.industries_served.map(
                                            (industry, idx) => (
                                                <div
                                                    key={idx}
                                                    className="flex items-center gap-1 bg-primary/10 text-primary px-3 py-1 rounded-full text-sm"
                                                >
                                                    <Tag className="h-3 w-3" />
                                                    {industry}
                                                </div>
                                            ),
                                        )
                                    ) : (
                                        <p className="text-sm text-muted-foreground">
                                            No industries specified
                                        </p>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Portfolio */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Portfolio Projects</CardTitle>
                            <CardDescription>
                                {user.portfolio?.length || 0} project
                                {user.portfolio?.length !== 1 ? "s" : ""} in
                                your portfolio
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4">
                                {user.portfolio && user.portfolio.length > 0 ? (
                                    user.portfolio.map((project, index) => (
                                        <div
                                            key={index}
                                            className="p-4 border rounded-lg bg-muted/30"
                                        >
                                            <div className="flex items-start justify-between mb-2">
                                                <h4 className="font-semibold text-lg">
                                                    {project.name ||
                                                        `Project ${index + 1}`}
                                                </h4>
                                                {project.client_industry && (
                                                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                                                        {
                                                            project.client_industry
                                                        }
                                                    </span>
                                                )}
                                            </div>
                                            {project.description && (
                                                <p className="text-sm text-muted-foreground mb-2">
                                                    {project.description}
                                                </p>
                                            )}
                                            {project.key_outcomes && (
                                                <div className="mt-2">
                                                    <Label className="text-xs font-medium text-muted-foreground">
                                                        Key Outcomes
                                                    </Label>
                                                    <p className="text-sm mt-1">
                                                        {project.key_outcomes}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-sm text-muted-foreground text-center py-4">
                                        No projects in portfolio
                                    </p>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-4 sm:p-6 md:p-8">
            <Card className="w-full max-w-4xl mx-auto">
                <CardHeader>
                    <CardTitle className="text-2xl">
                        {user ? "Edit Your Profile" : "Create Your Profile"}
                    </CardTitle>
                    <CardDescription>
                        {user
                            ? "Update your company and portfolio information."
                            : "Provide your company and portfolio details to help the AI personalize your sales preps."}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-4">
                            <div className="grid w-full items-center gap-1.5">
                                <Label htmlFor="company_name">
                                    Company Name
                                </Label>
                                <Input
                                    type="text"
                                    id="company_name"
                                    placeholder="Your Company Name"
                                    value={formState.company_name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="grid w-full items-center gap-1.5">
                                <Label htmlFor="company_description">
                                    Company Description
                                </Label>
                                <Textarea
                                    id="company_description"
                                    placeholder="Describe what your company does and your typical value proposition (max 500 chars)"
                                    value={formState.company_description}
                                    onChange={handleChange}
                                    maxLength={500}
                                    required
                                />
                            </div>
                            <div className="grid w-full items-center gap-1.5">
                                <Label htmlFor="industries_served">
                                    Industries Served (comma-separated)
                                </Label>
                                <Input
                                    type="text"
                                    id="industries_served"
                                    placeholder="e.g., SaaS, E-commerce, Healthcare"
                                    value={formState.industries_served.join(
                                        ", ",
                                    )}
                                    onChange={handleIndustriesChange}
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <h3 className="text-lg font-medium">Portfolio</h3>
                            <p className="text-sm text-muted-foreground">
                                Add at least {MIN_PORTFOLIO_ITEMS} projects
                                (maximum {MAX_PORTFOLIO_ITEMS}). This will be
                                used by the AI to find relevant experience.
                            </p>
                        </div>

                        <div className="space-y-4">
                            {formState.portfolio.map((project, index) => (
                                <Card key={index} className="relative">
                                    <CardHeader className="flex flex-row items-center justify-between">
                                        <div className="flex flex-col">
                                            <CardTitle className="text-lg">
                                                Project {index + 1}
                                            </CardTitle>
                                            {formState.portfolio.length ===
                                                MIN_PORTFOLIO_ITEMS && (
                                                <span className="text-xs text-muted-foreground mt-1">
                                                    A minimum of{" "}
                                                    {MIN_PORTFOLIO_ITEMS}{" "}
                                                    projects is required
                                                </span>
                                            )}
                                        </div>
                                        {formState.portfolio.length >
                                            MIN_PORTFOLIO_ITEMS && (
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="icon"
                                                className="absolute top-2 right-2"
                                                onClick={() =>
                                                    removeProject(index)
                                                }
                                            >
                                                <Trash2 className="h-4 w-4" />
                                                <span className="sr-only">
                                                    Remove project
                                                </span>
                                            </Button>
                                        )}
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="grid w-full items-center gap-1.5">
                                            <Label
                                                htmlFor={`project-name-${index}`}
                                            >
                                                Project Name
                                            </Label>
                                            <Input
                                                type="text"
                                                id={`project-name-${index}`}
                                                placeholder="e.g., AI Route Optimizer"
                                                value={project.name}
                                                onChange={(e) =>
                                                    handlePortfolioChange(
                                                        index,
                                                        "name",
                                                        e.target.value,
                                                    )
                                                }
                                            />
                                        </div>
                                        <div className="grid w-full items-center gap-1.5">
                                            <Label
                                                htmlFor={`client-industry-${index}`}
                                            >
                                                Client Industry
                                            </Label>
                                            <Input
                                                type="text"
                                                id={`client-industry-${index}`}
                                                placeholder="e.g., Logistics"
                                                value={project.client_industry}
                                                onChange={(e) =>
                                                    handlePortfolioChange(
                                                        index,
                                                        "client_industry",
                                                        e.target.value,
                                                    )
                                                }
                                            />
                                        </div>
                                        <div className="grid w-full items-center gap-1.5">
                                            <Label
                                                htmlFor={`description-${index}`}
                                            >
                                                Description
                                            </Label>
                                            <Textarea
                                                id={`description-${index}`}
                                                placeholder="Briefly describe the project (max 500 chars)"
                                                value={project.description}
                                                onChange={(e) =>
                                                    handlePortfolioChange(
                                                        index,
                                                        "description",
                                                        e.target.value,
                                                    )
                                                }
                                                maxLength={500}
                                            />
                                        </div>
                                        <div className="grid w-full items-center gap-1.5">
                                            <Label
                                                htmlFor={`key-outcomes-${index}`}
                                            >
                                                Key Outcomes
                                            </Label>
                                            <Textarea
                                                id={`key-outcomes-${index}`}
                                                placeholder="What were the key results? (e.g., Improved delivery time by 15%)"
                                                value={project.key_outcomes}
                                                onChange={(e) =>
                                                    handlePortfolioChange(
                                                        index,
                                                        "key_outcomes",
                                                        e.target.value,
                                                    )
                                                }
                                            />
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        {formState.portfolio.length < MAX_PORTFOLIO_ITEMS && (
                            <Button
                                type="button"
                                variant="outline"
                                onClick={addProject}
                            >
                                Add New Project
                            </Button>
                        )}

                        <div className="pt-4 flex gap-4">
                            <Button
                                type="submit"
                                className="flex-1"
                                disabled={loading}
                            >
                                {loading ? "Saving..." : "Save Profile"}
                            </Button>
                            {user && (
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={handleCancel}
                                    className="flex-1"
                                    disabled={loading}
                                >
                                    Cancel
                                </Button>
                            )}
                        </div>
                        {error && (
                            <p className="text-red-500 text-sm mt-2">{error}</p>
                        )}
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
