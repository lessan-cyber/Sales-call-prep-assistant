"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { use } from "react";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface PrepData {
  executive_summary: {
    the_client: string;
    our_angle: string;
    call_goal: string;
    confidence: number;
  };
  strategic_narrative: {
    dream_outcome: string;
    proof_of_achievement: Array<{
      project_name: string;
      relevance: string;
      relevance_score: number;
    }>;
    pain_points: Array<{
      pain: string;
      urgency: number;
      impact: number;
      evidence: string[];
    }>;
    confidence: number;
  };
  talking_points: {
    opening_hook: string;
    key_points: string[];
    competitive_context: string;
    confidence: number;
  };
  questions_to_ask: {
    strategic: string[];
    technical: string[];
    business_impact: string[];
    qualification: string[];
    confidence: number;
  };
  decision_makers: {
    profiles: Array<{
      name: string;
      title: string;
      linkedin_url?: string;
      background_points: string[];
    }> | null;
    confidence: number;
  };
  company_intelligence: {
    industry: string;
    company_size: string;
    recent_news: Array<{
      headline: string;
      date: string;
      significance: string;
    }>;
    strategic_initiatives: string[];
    confidence: number;
  };
  research_limitations: string[];
  overall_confidence: number;
  sources: string[];
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "bg-green-100 text-green-800";
  if (confidence >= 0.6) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return "High";
  if (confidence >= 0.6) return "Medium";
  return "Low";
}

export default function PrepDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  const [prepData, setPrepData] = useState<PrepData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPrep = async () => {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();

        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/preps/${id}`, {
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch prep report");
        }

        const data = await response.json();
        setPrepData(data);
      } catch (err: any) {
        setError(err.message || "Failed to load prep report");
      } finally {
        setLoading(false);
      }
    };

    fetchPrep();
  }, [id]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <p className="text-lg">Loading prep report...</p>
        </div>
      </div>
    );
  }

  if (error || !prepData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-600">{error || "Prep report not found"}</p>
            <Button onClick={() => router.push("/")} className="mt-4">
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Sales Prep Report</h1>
        <div className="flex items-center gap-4">
          <Badge className={getConfidenceColor(prepData.overall_confidence)}>
            Overall Confidence: {getConfidenceLabel(prepData.overall_confidence)} ({prepData.overall_confidence.toFixed(2)})
          </Badge>
          <Button variant="outline" onClick={() => router.push("/")}>
            Back to Home
          </Button>
          <Button variant="outline">
            Export PDF
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        {/* 1. Executive Summary */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>1. Executive Summary</CardTitle>
                <CardDescription>The TL;DR version</CardDescription>
              </div>
              <Badge className={getConfidenceColor(prepData.executive_summary.confidence)}>
                {getConfidenceLabel(prepData.executive_summary.confidence)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">The Client</h4>
              <p>{prepData.executive_summary.the_client}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Our Angle</h4>
              <p>{prepData.executive_summary.our_angle}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">The Goal of This Call</h4>
              <p>{prepData.executive_summary.call_goal}</p>
            </div>
          </CardContent>
        </Card>

        {/* 2. Strategic Narrative */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>2. Strategic Narrative</CardTitle>
                <CardDescription>Dream outcome and proof of achievement</CardDescription>
              </div>
              <Badge className={getConfidenceColor(prepData.strategic_narrative.confidence)}>
                {getConfidenceLabel(prepData.strategic_narrative.confidence)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">🎯 Dream Outcome</h4>
              <p>{prepData.strategic_narrative.dream_outcome}</p>
            </div>
            {prepData.strategic_narrative.proof_of_achievement.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">✅ Proof of Achievement</h4>
                <ul className="space-y-2">
                  {prepData.strategic_narrative.proof_of_achievement.map((project, idx) => (
                    <li key={idx} className="pl-4 border-l-2 border-gray-200">
                      <strong>{project.project_name}:</strong> {project.relevance}
                      <Badge className="ml-2" variant="outline">
                        {(project.relevance_score * 100).toFixed(0)}% match
                      </Badge>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {prepData.strategic_narrative.pain_points.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">⏳ Pain We're Solving</h4>
                <ul className="space-y-2">
                  {prepData.strategic_narrative.pain_points.map((pain, idx) => (
                    <li key={idx} className="pl-4 border-l-2 border-gray-200">
                      <p><strong>{pain.pain}</strong></p>
                      <p className="text-sm text-gray-600">
                        Urgency: {pain.urgency}/5, Impact: {pain.impact}/5
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 3. Talking Points */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>3. Talking Points & Pitch Angles</CardTitle>
                <CardDescription>Key messages for the conversation</CardDescription>
              </div>
              <Badge className={getConfidenceColor(prepData.talking_points.confidence)}>
                {getConfidenceLabel(prepData.talking_points.confidence)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Opening Hook</h4>
              <p>{prepData.talking_points.opening_hook}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Core Talking Points</h4>
              <ul className="list-disc pl-6 space-y-1">
                {prepData.talking_points.key_points.map((point, idx) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Leverage Their Context</h4>
              <p>{prepData.talking_points.competitive_context}</p>
            </div>
          </CardContent>
        </Card>

        {/* 4. Questions to Ask */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>4. Insightful Questions to Ask</CardTitle>
                <CardDescription>Strategic questions to uncover needs</CardDescription>
              </div>
              <Badge className={getConfidenceColor(prepData.questions_to_ask.confidence)}>
                {getConfidenceLabel(prepData.questions_to_ask.confidence)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {prepData.questions_to_ask.strategic.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Strategic</h4>
                <ul className="list-disc pl-6 space-y-1">
                  {prepData.questions_to_ask.strategic.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
            {prepData.questions_to_ask.technical.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Technical</h4>
                <ul className="list-disc pl-6 space-y-1">
                  {prepData.questions_to_ask.technical.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
            {prepData.questions_to_ask.business_impact.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Business Impact</h4>
                <ul className="list-disc pl-6 space-y-1">
                  {prepData.questions_to_ask.business_impact.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
            {prepData.questions_to_ask.qualification.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Qualification</h4>
                <ul className="list-disc pl-6 space-y-1">
                  {prepData.questions_to_ask.qualification.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 5. Decision Makers */}
        {prepData.decision_makers.profiles && (
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>5. Key Decision Makers</CardTitle>
                  <CardDescription>Profile of people you'll meet with</CardDescription>
                </div>
                <Badge className={getConfidenceColor(prepData.decision_makers.confidence)}>
                  {getConfidenceLabel(prepData.decision_makers.confidence)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {prepData.decision_makers.profiles.map((person, idx) => (
                <div key={idx} className="p-4 border rounded">
                  <h4 className="font-semibold">{person.name}</h4>
                  <p className="text-gray-600 mb-2">{person.title}</p>
                  {person.linkedin_url && (
                    <p className="text-sm">
                      <a href={person.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        LinkedIn Profile
                      </a>
                    </p>
                  )}
                  {person.background_points.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {person.background_points.map((point, pIdx) => (
                        <li key={pIdx} className="text-sm">• {point}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* 6. Company Intelligence */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>6. Company Intelligence</CardTitle>
                <CardDescription>Industry insights and recent activity</CardDescription>
              </div>
              <Badge className={getConfidenceColor(prepData.company_intelligence.confidence)}>
                {getConfidenceLabel(prepData.company_intelligence.confidence)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Industry</h4>
              <p>{prepData.company_intelligence.industry}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Company Size</h4>
              <p>{prepData.company_intelligence.company_size}</p>
            </div>
            {prepData.company_intelligence.recent_news.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Recent News & Signals</h4>
                <ul className="space-y-2">
                  {prepData.company_intelligence.recent_news.map((news, idx) => (
                    <li key={idx} className="pl-4 border-l-2 border-gray-200">
                      <p className="font-medium">{news.headline}</p>
                      <p className="text-sm text-gray-600">{news.date}</p>
                      <p className="text-sm">{news.significance}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {prepData.company_intelligence.strategic_initiatives.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Strategic Initiatives</h4>
                <ul className="list-disc pl-6 space-y-1">
                  {prepData.company_intelligence.strategic_initiatives.map((initiative, idx) => (
                    <li key={idx}>{initiative}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Research Limitations */}
        {prepData.research_limitations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-yellow-700">⚠️ Research Limitations & Red Flags</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-6 space-y-1">
                {prepData.research_limitations.map((limitation, idx) => (
                  <li key={idx} className="text-yellow-700">{limitation}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
