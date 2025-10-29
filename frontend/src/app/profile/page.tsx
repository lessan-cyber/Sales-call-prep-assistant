"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { UserProfile } from "@/types/user_profile";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

export default function ProfilePage() {
  const supabase = createClient();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<UserProfile>({
    company_name: "",
    company_description: "",
    industries_served: [],
    portfolio: [],
  });

  useEffect(() => {
    const getUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }
      setUser(user);
      fetchProfile(user.id);
    };

    getUser();
  }, [router, supabase]);

  const fetchProfile = async (userId: string) => {
    try {
      const response = await fetch(`/api/auth/profile?userId=${userId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch profile");
      }
      const data = await response.json();
      if (data) {
        setProfile(data);
        setFormState(data);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormState((prev) => ({ ...prev, [id]: value }));
  };

  const handleIndustriesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setFormState((prev) => ({ ...prev, industries_served: value.split(",").map((s) => s.trim()) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const method = profile ? "PUT" : "POST";
      const response = await fetch("/api/auth/profile", {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formState),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save profile");
      }

      const data = await response.json();
      setProfile(data);
      alert("Profile saved successfully!");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <p>Loading profile...</p>;
  }

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <Card className="w-[450px]">
        <CardHeader>
          <CardTitle>{profile ? "Edit Your Profile" : "Create Your Profile"}</CardTitle>
          <CardDescription>
            {profile
              ? "Update your company and portfolio information."
              : "Provide your company and portfolio details to help the AI personalize your sales preps."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
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
                placeholder="Describe what your company does and your typical value proposition (max 200 chars)"
                value={formState.company_description}
                onChange={handleChange}
                maxLength={200}
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
            {/* Portfolio input - simplified for now, will need a more complex component later */}
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="portfolio">Portfolio (JSON format, max 5 projects)</Label>
              <Textarea
                id="portfolio"
                placeholder='[{"name": "Project A", "client_industry": "Tech", "description": "...", "key_outcomes": "..."}]'
                value={JSON.stringify(formState.portfolio, null, 2)}
                onChange={(e) => {
                  try {
                    setFormState((prev) => ({ ...prev, portfolio: JSON.parse(e.target.value) }));
                  } catch (jsonError) {
                    // Handle invalid JSON input
                    // Optionally set an error state for the user
                  }
                }}
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Saving..." : "Save Profile"}
            </Button>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
