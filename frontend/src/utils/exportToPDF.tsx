import { pdf } from "@react-pdf/renderer";
import { PrepReportPDF } from "@/components/PrepReportPDF";

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

/**
 * Export a prep report to PDF
 * @param prepData - The prep report data
 * @param companyName - The company name for the PDF filename
 */
export async function exportPrepToPDF(
  prepData: PrepData,
  companyName: string
): Promise<void> {
  try {
    // Generate a clean filename
    const cleanCompanyName = companyName
      .replace(/[^a-z0-9]/gi, "_")
      .toLowerCase()
      .substring(0, 50);
    const timestamp = new Date().toISOString().split("T")[0];
    const filename = `prep_report_${cleanCompanyName}_${timestamp}.pdf`;

    // Create the PDF document
    const doc = <PrepReportPDF prepData={prepData} companyName={companyName} />;

    // Generate the PDF blob
    const pdfBlob = await pdf(doc).toBlob();

    // Create a download link
    const url = window.URL.createObjectURL(pdfBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;

    // Trigger download
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    console.log("PDF exported successfully:", filename);
  } catch (error) {
    console.error("Error exporting PDF:", error);
    throw new Error(
      `Failed to export PDF: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}
