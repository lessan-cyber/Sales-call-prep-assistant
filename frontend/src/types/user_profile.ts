export interface PortfolioItem {
  name: string;
  client_industry: string;
  description: string;
  key_outcomes: string;
}

export interface UserProfile {
  company_name: string;
  company_description: string;
  industries_served: string[];
  portfolio: PortfolioItem[];
}
