export type MatchStrength = "strong_match" | "moderate_match" | "weak_match" | "missing";

export interface TextFragment {
  id: string;
  section_name: string;
  order_index: number;
  text: string;
  source_type: "pdf" | "docx" | "txt";
  page_number?: number | null;
  block_index?: number | null;
  char_start?: number | null;
  char_end?: number | null;
}

export interface ResumeProfile {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  linkedin?: string | null;
  github?: string | null;
  portfolio?: string | null;
  summary?: string | null;
  education: Array<{
    school: string;
    degree: string;
    field?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    gpa?: string | null;
    honors?: string | null;
    evidence_fragment_ids: string[];
  }>;
  experience: Array<{
    company: string;
    title: string;
    location?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    bullets: string[];
    technologies: string[];
    evidence_fragment_ids: string[];
  }>;
  projects: Array<{
    name: string;
    description: string;
    bullets: string[];
    technologies: string[];
    evidence_fragment_ids: string[];
  }>;
  skills: Array<{
    name: string;
    category?: string | null;
    evidence_fragment_ids: string[];
  }>;
  certifications: string[];
  raw_sections: Array<{
    name: string;
    text: string;
    fragment_ids?: string[];
  }>;
  text_fragments: TextFragment[];
}

export interface RequirementItem {
  id: string;
  text: string;
  category: string;
  importance: string;
  normalized_terms: string[];
  numeric_requirement?: number | null;
}

export interface JobProfile {
  title?: string | null;
  company?: string | null;
  location?: string | null;
  job_summary: string;
  responsibilities: string[];
  required_skills: string[];
  preferred_skills: string[];
  tools: string[];
  domain_keywords: string[];
  years_experience_required?: number | null;
  education_requirements: string[];
  certifications: string[];
  seniority?: string | null;
  employment_type?: string | null;
  raw_requirement_items: RequirementItem[];
}

export interface SubscoreBucket {
  key: string;
  label: string;
  weight: number;
  earned_points: number;
  possible_points: number;
  normalized_score?: number | null;
  applicable: boolean;
  matched_requirements: number;
  total_requirements: number;
}

export interface AnalysisListItem {
  id: string;
  title: string;
  company?: string | null;
  filename: string;
  overall_score: number;
  created_at: string;
  top_strengths: string[];
  top_gaps: string[];
}

export interface RequirementMatch {
  id: string;
  requirement_id: string;
  requirement_text: string;
  bucket: string;
  category: string;
  importance: string;
  match_strength: MatchStrength;
  score_contribution: number;
  confidence_score: number;
  explanation: string;
  matched_terms: string[];
  missing_terms: string[];
  evidence_fragment_ids: string[];
}

export interface Suggestion {
  id: string;
  suggestion_type: string;
  title: string;
  body: string;
  grounded: boolean;
  supporting_fragment_ids: string[];
  created_at: string;
}

export interface AnalysisDetail {
  id: string;
  overall_score: number;
  created_at: string;
  updated_at: string;
  resume_document: {
    id: string;
    filename: string;
    file_type: string;
    raw_text: string;
    created_at: string;
  };
  fragments: Array<{
    id: string;
    section_name: string;
    order_index: number;
    text: string;
    page_number?: number | null;
    block_index?: number | null;
    metadata: Record<string, unknown>;
    created_at: string;
  }>;
  parsed_resume: ResumeProfile;
  job_posting: JobProfile;
  subscores: SubscoreBucket[];
  summary: {
    top_strengths?: string[];
    top_gaps?: string[];
    notes?: string[];
    tailored_summary?: string;
  };
  requirements: RequirementMatch[];
  suggestions: Suggestion[];
}

