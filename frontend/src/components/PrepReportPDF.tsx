import React from "react";
import { Document, Page, Text, View, StyleSheet } from "@react-pdf/renderer";

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

interface PrepReportPDFProps {
  prepData: PrepData;
  companyName: string;
}

// Styles for the PDF
const styles = StyleSheet.create({
  page: {
    paddingTop: 40,
    paddingLeft: 40,
    paddingRight: 40,
    paddingBottom: 60,
    fontSize: 11,
    lineHeight: 1.5,
  },
  header: {
    marginBottom: 20,
    borderBottom: "2px solid #3b82f6",
    paddingBottom: 15,
    paddingTop: 5,
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  pageNumberHeader: {
    fontSize: 9,
    color: "#64748b",
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    color: "#1e293b",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 12,
    color: "#64748b",
    marginBottom: 5,
  },
  overallConfidence: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    marginTop: 8,
  },
  confidenceBadge: {
    fontSize: 10,
    padding: 4,
    borderRadius: 4,
    fontWeight: 600,
  },
  section: {
    marginBottom: 20,
    pageBreakInside: "avoid",
  },
  sectionHeader: {
    fontSize: 16,
    fontWeight: 700,
    color: "#1e293b",
    marginBottom: 10,
    borderBottom: "1px solid #e2e8f0",
    paddingBottom: 5,
  },
  subsectionTitle: {
    fontSize: 12,
    fontWeight: 600,
    color: "#475569",
    marginTop: 10,
    marginBottom: 5,
  },
  subsectionContent: {
    fontSize: 11,
    color: "#334155",
    marginBottom: 8,
    textAlign: "justify",
  },
  listItem: {
    fontSize: 11,
    color: "#334155",
    marginLeft: 10,
    marginBottom: 4,
  },
  listItemWithBullet: {
    flexDirection: "row",
    marginBottom: 4,
  },
  bullet: {
    width: 10,
    fontSize: 11,
    color: "#334155",
  },
  listItemText: {
    flex: 1,
    fontSize: 11,
    color: "#334155",
    textAlign: "justify",
  },
  divider: {
    height: 1,
    backgroundColor: "#e2e8f0",
    marginVertical: 15,
  },
  projectCard: {
    backgroundColor: "#f8fafc",
    padding: 10,
    marginBottom: 8,
    borderRadius: 4,
    borderLeft: "3px solid #3b82f6",
  },
  projectName: {
    fontSize: 11,
    fontWeight: 600,
    color: "#1e293b",
    marginBottom: 3,
  },
  projectRelevance: {
    fontSize: 10,
    color: "#475569",
  },
  painPoint: {
    backgroundColor: "#fef3c7",
    padding: 8,
    marginBottom: 6,
    borderRadius: 4,
    borderLeft: "3px solid #f59e0b",
  },
  painTitle: {
    fontSize: 11,
    fontWeight: 600,
    color: "#78350f",
    marginBottom: 3,
  },
  painMetrics: {
    fontSize: 9,
    color: "#92400e",
    fontStyle: "italic",
  },
  decisionMakerCard: {
    backgroundColor: "#f0fdf4",
    padding: 10,
    marginBottom: 8,
    borderRadius: 4,
    borderLeft: "3px solid #22c55e",
  },
  name: {
    fontSize: 11,
    fontWeight: 700,
    color: "#14532d",
    marginBottom: 2,
  },
  personTitle: {
    fontSize: 10,
    color: "#166534",
    marginBottom: 4,
  },
  limitationWarning: {
    backgroundColor: "#fef2f2",
    padding: 10,
    borderRadius: 4,
    borderLeft: "3px solid #ef4444",
  },
  limitationText: {
    fontSize: 10,
    color: "#991b1b",
  },
  newsItem: {
    marginBottom: 8,
    paddingLeft: 10,
    borderLeft: "2px solid #e2e8f0",
  },
  newsHeadline: {
    fontSize: 11,
    fontWeight: 600,
    color: "#1e293b",
    marginBottom: 2,
  },
  newsDate: {
    fontSize: 9,
    color: "#64748b",
    marginBottom: 3,
  },
  footer: {
    position: "absolute",
    bottom: 20,
    left: 40,
    right: 40,
    fontSize: 9,
    color: "#94a3b8",
    textAlign: "center",
    borderTop: "1px solid #e2e8f0",
    paddingTop: 8,
  },
});

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "#22c55e"; // green
  if (confidence >= 0.6) return "#f59e0b"; // yellow
  return "#ef4444"; // red
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return "High";
  if (confidence >= 0.6) return "Medium";
  return "Low";
}

export const PrepReportPDF: React.FC<PrepReportPDFProps> = ({
  prepData,
  companyName,
}) => {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerRow}>
            <Text style={styles.title}>Sales Prep Report</Text>
            <Text style={styles.pageNumberHeader}>
              Page <Text render={({ pageNumber }) => `${pageNumber}`} fixed />
            </Text>
          </View>
          <Text style={styles.subtitle}>Company: {companyName}</Text>
          <View style={styles.overallConfidence}>
            <Text style={styles.subtitle}>Overall Confidence: </Text>
            <Text
              style={[
                styles.confidenceBadge,
                { backgroundColor: getConfidenceColor(prepData.overall_confidence), color: "white" },
              ]}
            >
              {getConfidenceLabel(prepData.overall_confidence)} (
              {prepData.overall_confidence.toFixed(2)})
            </Text>
          </View>
        </View>

        {/* Section 1: Executive Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionHeader}>1. Executive Summary</Text>
          <Text style={styles.subsectionTitle}>The Client</Text>
          <Text style={styles.subsectionContent}>
            {prepData.executive_summary.the_client}
          </Text>

          <Text style={styles.subsectionTitle}>Our Angle</Text>
          <Text style={styles.subsectionContent}>
            {prepData.executive_summary.our_angle}
          </Text>

          <Text style={styles.subsectionTitle}>The Goal of This Call</Text>
          <Text style={styles.subsectionContent}>
            {prepData.executive_summary.call_goal}
          </Text>
        </View>

        <View style={styles.divider} />

        {/* Section 2: Strategic Narrative */}
        <View style={styles.section}>
          <Text style={styles.sectionHeader}>2. Strategic Narrative</Text>

          <Text style={styles.subsectionTitle}>Dream Outcome</Text>
          <Text style={styles.subsectionContent}>
            {prepData.strategic_narrative.dream_outcome}
          </Text>

          {prepData.strategic_narrative.proof_of_achievement.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Proof of Achievement</Text>
              {prepData.strategic_narrative.proof_of_achievement.map((project, idx) => (
                <View key={idx} style={styles.projectCard}>
                  <Text style={styles.projectName}>{project.project_name}</Text>
                  <Text style={styles.projectRelevance}>{project.relevance}</Text>
                </View>
              ))}
            </>
          )}

          {prepData.strategic_narrative.pain_points.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Pain Points We're Solving</Text>
              {prepData.strategic_narrative.pain_points.map((pain, idx) => (
                <View key={idx} style={styles.painPoint}>
                  <Text style={styles.painTitle}>{pain.pain}</Text>
                  <Text style={styles.painMetrics}>
                    Urgency: {pain.urgency}/5, Impact: {pain.impact}/5
                  </Text>
                </View>
              ))}
            </>
          )}
        </View>

        <View style={styles.divider} />

        {/* Section 3: Talking Points */}
        <View style={styles.section}>
          <Text style={styles.sectionHeader}>3. Talking Points & Pitch Angles</Text>

          <Text style={styles.subsectionTitle}>Opening Hook</Text>
          <Text style={styles.subsectionContent}>
            {prepData.talking_points.opening_hook}
          </Text>

          <Text style={styles.subsectionTitle}>Core Talking Points</Text>
          {prepData.talking_points.key_points.map((point, idx) => (
            <View key={idx} style={styles.listItemWithBullet}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.listItemText}>{point}</Text>
            </View>
          ))}

          <Text style={styles.subsectionTitle}>Leverage Their Context</Text>
          <Text style={styles.subsectionContent}>
            {prepData.talking_points.competitive_context}
          </Text>
        </View>

        <View style={styles.divider} />

        {/* Section 4: Questions to Ask */}
        <View style={styles.section}>
          <Text style={styles.sectionHeader}>4. Insightful Questions to Ask</Text>

          {prepData.questions_to_ask.strategic.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Strategic</Text>
              {prepData.questions_to_ask.strategic.map((q, idx) => (
                <View key={idx} style={styles.listItemWithBullet}>
                  <Text style={styles.bullet}>•</Text>
                  <Text style={styles.listItemText}>{q}</Text>
                </View>
              ))}
            </>
          )}

          {prepData.questions_to_ask.technical.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Technical</Text>
              {prepData.questions_to_ask.technical.map((q, idx) => (
                <View key={idx} style={styles.listItemWithBullet}>
                  <Text style={styles.bullet}>•</Text>
                  <Text style={styles.listItemText}>{q}</Text>
                </View>
              ))}
            </>
          )}

          {prepData.questions_to_ask.business_impact.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Business Impact</Text>
              {prepData.questions_to_ask.business_impact.map((q, idx) => (
                <View key={idx} style={styles.listItemWithBullet}>
                  <Text style={styles.bullet}>•</Text>
                  <Text style={styles.listItemText}>{q}</Text>
                </View>
              ))}
            </>
          )}

          {prepData.questions_to_ask.qualification.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Qualification</Text>
              {prepData.questions_to_ask.qualification.map((q, idx) => (
                <View key={idx} style={styles.listItemWithBullet}>
                  <Text style={styles.bullet}>•</Text>
                  <Text style={styles.listItemText}>{q}</Text>
                </View>
              ))}
            </>
          )}
        </View>

        <View style={styles.divider} />

        {/* Section 5: Decision Makers */}
        {prepData.decision_makers.profiles && prepData.decision_makers.profiles.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionHeader}>5. Key Decision Makers</Text>
            {prepData.decision_makers.profiles.map((person, idx) => (
              <View key={idx} style={styles.decisionMakerCard}>
                <Text style={styles.name}>{person.name}</Text>
                <Text style={styles.personTitle}>{person.title}</Text>
                {person.linkedin_url && (
                  <Text style={styles.subsectionContent}>LinkedIn: {person.linkedin_url}</Text>
                )}
                {person.background_points.map((point, pIdx) => (
                  <View key={pIdx} style={styles.listItemWithBullet}>
                    <Text style={styles.bullet}>•</Text>
                    <Text style={styles.listItemText}>{point}</Text>
                  </View>
                ))}
              </View>
            ))}
          </View>
        )}

        {prepData.decision_makers.profiles && prepData.decision_makers.profiles.length > 0 && (
          <View style={styles.divider} />
        )}

        {/* Section 6: Company Intelligence */}
        <View style={styles.section}>
          <Text style={styles.sectionHeader}>6. Company Intelligence</Text>

          <Text style={styles.subsectionTitle}>Industry</Text>
          <Text style={styles.subsectionContent}>
            {prepData.company_intelligence.industry}
          </Text>

          <Text style={styles.subsectionTitle}>Company Size</Text>
          <Text style={styles.subsectionContent}>
            {prepData.company_intelligence.company_size}
          </Text>

          {prepData.company_intelligence.recent_news.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Recent News & Signals</Text>
              {prepData.company_intelligence.recent_news.map((news, idx) => (
                <View key={idx} style={styles.newsItem}>
                  <Text style={styles.newsHeadline}>{news.headline}</Text>
                  <Text style={styles.newsDate}>{news.date}</Text>
                  <Text style={styles.subsectionContent}>{news.significance}</Text>
                </View>
              ))}
            </>
          )}

          {prepData.company_intelligence.strategic_initiatives.length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>Strategic Initiatives</Text>
              {prepData.company_intelligence.strategic_initiatives.map((initiative, idx) => (
                <View key={idx} style={styles.listItemWithBullet}>
                  <Text style={styles.bullet}>•</Text>
                  <Text style={styles.listItemText}>{initiative}</Text>
                </View>
              ))}
            </>
          )}
        </View>

        {/* Research Limitations */}
        {prepData.research_limitations.length > 0 && (
          <>
            <View style={styles.divider} />
            <View style={styles.section}>
              <Text style={styles.sectionHeader}>⚠️ Research Limitations & Red Flags</Text>
              {prepData.research_limitations.map((limitation, idx) => (
                <View key={idx} style={styles.limitationWarning}>
                  <Text style={styles.limitationText}>{limitation}</Text>
                </View>
              ))}
            </View>
          </>
        )}

        {/* Footer */}
        <View style={styles.footer}>
          <Text
            render={({ pageNumber, totalPages }) =>
              `Page ${pageNumber} of ${totalPages} | Generated on ${new Date().toLocaleDateString()}`
            }
            fixed
          />
        </View>
      </Page>
    </Document>
  );
};
