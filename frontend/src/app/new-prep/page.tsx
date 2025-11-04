"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export default function NewPrepPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    company_name: "",
    meeting_objective: "",
    contact_person_name: "",
    contact_linkedin_url: "",
    meeting_date: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/preps`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create prep");
      }

      const data = await response.json();
      router.push(`/prep/${data.prep_id}`);
    } catch (err: any) {
      setError(err.message || "An error occurred");
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Create New Sales Prep</CardTitle>
          <CardDescription>
            Generate a comprehensive sales prep report to prepare for your call.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Required Fields */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="company_name">Company Name *</Label>
                <Input
                  id="company_name"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleChange}
                  required
                  placeholder="e.g., Acme Corporation"
                  disabled={loading}
                />
              </div>

              <div>
                <Label htmlFor="meeting_objective">Meeting Objective *</Label>
                <Textarea
                  id="meeting_objective"
                  name="meeting_objective"
                  value={formData.meeting_objective}
                  onChange={handleChange}
                  required
                  rows={4}
                  placeholder="Describe the purpose of this sales call..."
                  disabled={loading}
                />
              </div>
            </div>

            {/* Optional Fields - Expandable Section */}
            <div className="space-y-4 border-t pt-4">
              <h3 className="text-lg font-medium">Additional Details (Optional)</h3>
              <p className="text-sm text-gray-600">
                Providing contact information improves research quality
              </p>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="contact_person_name">Contact Person Name</Label>
                  <Input
                    id="contact_person_name"
                    name="contact_person_name"
                    value={formData.contact_person_name}
                    onChange={handleChange}
                    placeholder="e.g., Jane Smith"
                    disabled={loading}
                  />
                </div>

                <div>
                  <Label htmlFor="contact_linkedin_url">Contact LinkedIn URL</Label>
                  <Input
                    id="contact_linkedin_url"
                    name="contact_linkedin_url"
                    type="url"
                    value={formData.contact_linkedin_url}
                    onChange={handleChange}
                    placeholder="https://linkedin.com/in/jane-smith"
                    disabled={loading}
                  />
                </div>

                <div>
                  <Label htmlFor="meeting_date">Meeting Date</Label>
                  <Input
                    id="meeting_date"
                    name="meeting_date"
                    type="date"
                    value={formData.meeting_date}
                    onChange={handleChange}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

            {error && (
              <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
                {error}
              </div>
            )}

            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={loading}
                className="flex-1"
              >
                {loading ? "Generating..." : "Generate Prep Report"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/")}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
