import type { Domain } from "./types";

export const TRACK_PATH: Record<Domain, string> = {
  agriculture: "/agriculture",
  finance_poverty: "/finance-poverty",
  employment: "/open-innovation/employment",
  health: "/open-innovation/health",
  education: "/open-innovation/education",
  transport: "/open-innovation/transport",
};

export const HEADLINES: Record<Domain, string[]> = {
  agriculture: ["ag_improved_seeds", "ag_irrigated_land"],
  finance_poverty: ["poverty_rate", "fin_banked"],
  employment: ["emp_unemployment", "emp_youth_neet"],
  health: ["health_stunting", "health_insurance"],
  education: ["edu_secondary_attendance", "edu_computer_literacy"],
  transport: ["tr_stage_access", "tr_road_access"],
};

