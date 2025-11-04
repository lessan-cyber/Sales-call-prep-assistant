"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { UserProfile, PortfolioItem } from "@/types/user_profile";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Trash2 } from "lucide-react";
import { useAuth } from "@/components/providers/auth-provider";

const MAX_PORTFOLIO_ITEMS = 5;

export default function ProfilePage() {
  const router = useRouter();
  const { user, loading, session } = useAuth();
  const [formState, setFormState] = useState<UserProfile>({
    company_name: "",
    company_description: "",
    industries_served: [],
    portfolio: [],
  });
  const [error, setError] = useState<string | null>(null);
  const isFormInitialized = useRef(false);

  useEffect(() => {
    if (!loading) {
      if (!session) {
        router.push("/login");
      } else if (user) {
        // If form is not initialized, or if the user object has changed (e.g., a different user logged in)
        // and the current formState doesn't match the user's ID.
        if (!isFormInitialized.current || (user.id && formState.id !== user.id)) {
          setFormState(user);
          isFormInitialized.current = true;
        }
      } else {
        // User is logged in but has no profile, initialize form for creation
        // Only if not already initialized to prevent resetting user input
        if (!isFormInitialized.current) {
          setFormState({
            company_name: "",
            company_description: "",
            industries_served: [],
            portfolio: [],
          });
          isFormInitialized.current = true;
        }
      }
    }
  }, [loading, session, user, router]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormState((prev) => ({ ...prev, [id]: value }));
  };

  const handleIndustriesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setFormState((prev) => ({ ...prev, industries_served: value.split(",").map((s) => s.trim()) }));
  };

  const handlePortfolioChange = (index: number, field: keyof PortfolioItem, value: string) => {
    const updatedPortfolio = [...formState.portfolio];
    updatedPortfolio[index] = { ...updatedPortfolio[index], [field]: value };
    setFormState((prev) => ({ ...prev, portfolio: updatedPortfolio }));
  };

  const addProject = () => {
    if (formState.portfolio.length < MAX_PORTFOLIO_ITEMS) {
      setFormState((prev) => ({
        ...prev,
        portfolio: [
          ...prev.portfolio,
          { name: "", client_industry: "", description: "", key_outcomes: "" },
        ],
      }));
    }
  };

  const removeProject = (index: number) => {
    const updatedPortfolio = formState.portfolio.filter((_, i) => i !== index);
    setFormState((prev) => ({ ...prev, portfolio: updatedPortfolio }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    // setLoading(true); // AuthProvider handles global loading

    try {
      const response = await fetch("/api/auth/profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify(formState),
      });

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
      router.push("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      // setLoading(false); // AuthProvider handles global loading
    }
  };

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center"><p>Loading profile...</p></div>;
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 md:p-8">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">{user ? "Edit Your Profile" : "Create Your Profile"}</CardTitle>
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
                <Label htmlFor="company_name">Company Name</Label>
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
                <Label htmlFor="company_description">Company Description</Label>
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
                <Label htmlFor="industries_served">Industries Served (comma-separated)</Label>
                <Input
                  type="text"
                  id="industries_served"
                  placeholder="e.g., SaaS, E-commerce, Healthcare"
                  value={formState.industries_served.join(", ")}
                  onChange={handleIndustriesChange}
                  required
                />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium">Portfolio</h3>
              <p className="text-sm text-muted-foreground">
                Add up to {MAX_PORTFOLIO_ITEMS} projects. This will be used by the AI to find relevant experience.
              </p>
            </div>

            <div className="space-y-4">
              {formState.portfolio.map((project, index) => (
                <Card key={index} className="relative">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-lg">Project {index + 1}</CardTitle>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2"
                      onClick={() => removeProject(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                      <span className="sr-only">Remove project</span>
                    </Button>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor={`project-name-${index}`}>Project Name</Label>
                      <Input
                        type="text"
                        id={`project-name-${index}`}
                        placeholder="e.g., AI Route Optimizer"
                        value={project.name}
                        onChange={(e) => handlePortfolioChange(index, "name", e.target.value)}
                        required
                      />
                    </div>
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor={`client-industry-${index}`}>Client Industry</Label>
                      <Input
                        type="text"
                        id={`client-industry-${index}`}
                        placeholder="e.g., Logistics"
                        value={project.client_industry}
                        onChange={(e) => handlePortfolioChange(index, "client_industry", e.target.value)}
                        required
                      />
                    </div>
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor={`description-${index}`}>Description</Label>
                      <Textarea
                        id={`description-${index}`}
                        placeholder="Briefly describe the project (max 200 chars)"
                        value={project.description}
                        onChange={(e) => handlePortfolioChange(index, "description", e.target.value)}
                        maxLength={200}
                        required
                      />
                    </div>
                    <div className="grid w-full items-center gap-1.5">
                      <Label htmlFor={`key-outcomes-${index}`}>Key Outcomes</Label>
                      <Textarea
                        id={`key-outcomes-${index}`}
                        placeholder="What were the key results? (e.g., Improved delivery time by 15%)"
                        value={project.key_outcomes}
                        onChange={(e) => handlePortfolioChange(index, "key_outcomes", e.target.value)}
                        required
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {formState.portfolio.length < MAX_PORTFOLIO_ITEMS && (
              <Button type="button" variant="outline" onClick={addProject}>
                Add New Project
              </Button>
            )}

            <div className="pt-4">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Saving..." : "Save Profile"}
              </Button>
            </div>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}