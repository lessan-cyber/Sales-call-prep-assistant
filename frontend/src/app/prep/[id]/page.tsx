"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/components/providers/auth-provider";

interface PrepReport {
  executive_summary: {
    summary: string;
    confidence_score: number;
  };
  strategic_narrative: {
    narrative: string;
    confidence_score: number;
  };
  key_talking_points: Array<{
    point: string;
    relevance_score: number;
  }>;
  insightful_questions: Array<{
    question: string;
    category: string;
  }>;
  key_decision_makers: Array<{
    name: string;
    title: string;
    linkedin_profile?: string;
    key_interests?: string[];
  }>;
  company_intelligence: {
    overview: string;
    recent_news?: string[];
    industry_trends?: string[];
    competitors?: string[];
  };
  overall_confidence: number;
}

export default function PrepReportPage() {
  const { id } = useParams();
  const { session } = useAuth();
  const [report, setReport] = useState<PrepReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchReport() {
      console.log("fetchReport called.");
      console.log("id:", id);
      console.log("session:", session);

      if (!id || !session) {
        console.log("Missing id or session. Not fetching.");
        setLoading(false);
        return;
      }

      try {
        console.log(`Fetching report from /api/preps/${id}`);
        const response = await fetch(`/api/preps/${id}`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });

        console.log("Response status:", response.status);
        if (!response.ok) {
          const errorData = await response.json();
          console.error("Error fetching report:", errorData);
          throw new Error(errorData.detail || "Failed to fetch report");
        }

        const data: PrepReport = await response.json();
        console.log("Fetched report data:", data);
        setReport(data);
      } catch (err: any) {
        console.error("Catch block error:", err);
        setError(err.message);
      } finally {
        console.log("fetchReport finished. Loading set to false.");
        setLoading(false);
      }
    }

    fetchReport();
  }, [id, session]);

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading report...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center min-h-screen text-red-500">Error: {error}</div>;
  }

  if (!report) {
    return <div className="flex justify-center items-center min-h-screen">No report found.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-3xl">Sales Prep Report</CardTitle>
          <CardDescription>Generated for {report.company_intelligence.overview.split('.')[0]} - Overall Confidence: {(report.overall_confidence * 100).toFixed(2)}%</CardDescription>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Executive Summary</CardTitle>
            <CardDescription>Confidence: {(report.executive_summary.confidence_score * 100).toFixed(2)}%</CardDescription>
          </CardHeader>
          <CardContent>
            <p>{report.executive_summary.summary}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Strategic Narrative</CardTitle>
            <CardDescription>Confidence: {(report.strategic_narrative.confidence_score * 100).toFixed(2)}%</CardDescription>
          </CardHeader>
          <CardContent>
            <p>{report.strategic_narrative.narrative}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Key Talking Points</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-5 space-y-2">
            {report.key_talking_points.map((item, index) => (
              <li key={index}>{item.point} (Relevance: {(item.relevance_score * 100).toFixed(2)}%)</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Insightful Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-5 space-y-2">
            {report.insightful_questions.map((item, index) => (
              <li key={index}><strong>{item.category}:</strong> {item.question}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Key Decision Makers</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-5 space-y-2">
            {report.key_decision_makers.map((item, index) => (
              <li key={index}>
                <strong>{item.name}</strong> - {item.title}
                {item.linkedin_profile && (
                  <a href={item.linkedin_profile} target="_blank" rel="noopener noreferrer" className="ml-2 text-blue-500 hover:underline">
                    LinkedIn
                  </a>
                )}
                {item.key_interests && item.key_interests.length > 0 && (
                  <p className="text-sm text-gray-600">Interests: {item.key_interests.join(", ")}</p>
                )}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Company Intelligence</CardTitle>
        </CardHeader>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">Overview</h3>
          <p className="mb-4">{report.company_intelligence.overview}</p>

          {report.company_intelligence.recent_news && report.company_intelligence.recent_news.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold mb-2">Recent News</h3>
              <ul className="list-disc pl-5 space-y-1">
                {report.company_intelligence.recent_news.map((news, index) => (
                  <li key={index}>{news}</li>
                ))}
              </ul>
            </div>
          )}

          {report.company_intelligence.industry_trends && report.company_intelligence.industry_trends.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold mb-2">Industry Trends</h3>
              <ul className="list-disc pl-5 space-y-1">
                {report.company_intelligence.industry_trends.map((trend, index) => (
                  <li key={index}>{trend}</li>
                ))}
              </ul>
            </div>
          )}

          {report.company_intelligence.competitors && report.company_intelligence.competitors.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Competitors</h3>
              <ul className="list-disc pl-5 space-y-1">
                {report.company_intelligence.competitors.map((competitor, index) => (
                  <li key={index}>{competitor}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
