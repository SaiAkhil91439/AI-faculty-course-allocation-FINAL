import os
import json
import re
from typing import Dict, Any, Optional
import pandas as pd
from backend.excel_reader import load_all_excel_files
from backend.validator import validate_inputs
from backend.scoring import calculate_compatibility_scores
from backend.optimizer import solve_faculty_allocation
from backend.excel_generator import generate_allocation_excel
from backend.workload_calculator import calculate_ltpc_workload, convert_course_df_to_workload_input

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class FacultyAllocationAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.latest_allocation_res = None
        self.latest_scores_df = None
        self.latest_pref_df = None
        self.latest_exp_df = None
        self.latest_course_df = None
        self.scenario_history = []
        if HAS_GENAI and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Gemini client initialization warning: {e}")

    def run_pipeline(
        self,
        pref_file_source: Any,
        exp_file_source: Optional[Any] = None,
        num_sections: int = 12,
        num_subjects: int = 6,
        sections_per_faculty: int = 3,
        max_subjects_per_faculty: int = 1,
        course_file_source: Optional[Any] = None,
        dean_max_sections: int = 2,
        hod_max_sections: int = 3,
        high_exp_threshold: float = 8.0,
        weights: Optional[Dict[str, float]] = None,
        output_excel_path: str = "output/faculty_allocation.xlsx"
    ) -> Dict[str, Any]:
        """
        Full Agent Orchestration Workflow:
        1. Read Excel files & Course L-T-P-C Structure
        2. Validate Data & Designation Hours Constraints
        3. Score Compatibility (Strict 1st preference priority & least-preferred subject indexing)
        4. Optimize with OR-Tools CP-SAT (Designation bounds, High-Experience 2+1 split & 1 L + 2 T/P per section)
        5. Generate Output Excel
        6. Synthesize AI Explanation
        """
        agent_steps = []

        # Step 1: Read Files
        agent_steps.append({"step": 1, "action": "Read Excel Files, Course L-T-P-C & Extract Roles", "status": "In Progress"})
        pref_df, exp_df, course_df = load_all_excel_files(pref_file_source, exp_file_source, course_file_source)
        agent_steps[-1]["status"] = "Completed"
        agent_steps[-1]["details"] = f"Loaded {len(pref_df)} faculty preferences, {len(exp_df)} experience records, and {len(course_df)} course L-T-P-C details."

        # Step 2: Validate Data
        agent_steps.append({"step": 2, "action": "Validate Data & Designation Workload Limits", "status": "In Progress"})
        val_info = validate_inputs(
            pref_df=pref_df,
            exp_df=exp_df,
            num_sections=num_sections,
            num_subjects=num_subjects,
            sections_per_faculty=sections_per_faculty,
            max_subjects_per_faculty=max_subjects_per_faculty,
            course_df=course_df,
            dean_max_sections=dean_max_sections,
            hod_max_sections=hod_max_sections,
            high_exp_threshold=high_exp_threshold
        )
        agent_steps[-1]["status"] = "Completed"
        agent_steps[-1]["details"] = (
            f"Validation passed! Identified {val_info['deans_count']} Dean(s), {val_info['hods_count']} HOD(s), "
            f"and {val_info['high_exp_count']} High-Experience Faculty (course teaching exp >= {high_exp_threshold} yrs)."
        )

        # Step 3: Calculate Scores
        agent_steps.append({"step": 3, "action": "Calculate Compatibility & Least-Preferred Subject Index", "status": "In Progress"})
        scores_res = calculate_compatibility_scores(pref_df, exp_df, weights=weights)
        agent_steps[-1]["status"] = "Completed"
        agent_steps[-1]["details"] = (
            f"Computed compatibility scores for {len(scores_res['scores_df'])} faculty-subject pairs. "
            f"Prioritized 1st preference ranks and indexed least-preferred subjects for experienced faculty allocation."
        )

        # Step 4: Call Optimization Engine
        agent_steps.append({"step": 4, "action": "Solve Allocation with Google OR-Tools CP-SAT", "status": "In Progress"})
        allocation_res = solve_faculty_allocation(
            pref_df=pref_df,
            exp_df=exp_df,
            scores_dict=scores_res,
            num_sections=num_sections,
            num_subjects=num_subjects,
            sections_per_faculty=sections_per_faculty,
            max_subjects_per_faculty=max_subjects_per_faculty,
            course_df=course_df,
            dean_max_sections=dean_max_sections,
            hod_max_sections=hod_max_sections,
            high_exp_threshold=high_exp_threshold
        )
        agent_steps[-1]["status"] = "Completed"
        agent_steps[-1]["details"] = (
            f"OR-Tools solver status: {allocation_res['status']}. "
            f"Average score: {allocation_res['average_score']}/100. Applied 2+1 section split rule to {allocation_res.get('high_exp_faculty_count', 0)} high-experience faculty."
        )

        # Step 4.5: Calculate LTPC Faculty Workload & Department Demand
        courses_input = convert_course_df_to_workload_input(course_df)
        num_available_faculty = len(pref_df) if pref_df is not None and not pref_df.empty else 34
        workload_analysis = calculate_ltpc_workload(
            courses=courses_input,
            num_sections=num_sections,
            l_faculty_multiplier=1,
            t_faculty_multiplier=3,
            p_faculty_multiplier=3,
            num_available_faculty=num_available_faculty
        )
        allocation_res["workload_analysis"] = workload_analysis

        # Step 5: Generate Excel
        agent_steps.append({"step": 5, "action": "Generate Workload Excel Workbook", "status": "In Progress"})
        excel_path = generate_allocation_excel(allocation_res, output_excel_path)
        agent_steps[-1]["status"] = "Completed"
        agent_steps[-1]["details"] = f"Excel report matching target workload table saved to {excel_path} (includes LTPC Workload Calculation tab)."

        # Step 6: AI Explanation
        agent_steps.append({"step": 6, "action": "Generate Allocation Executive Summary", "status": "In Progress"})
        ai_explanation = self._generate_explanation(allocation_res, scores_res["scores_df"])
        agent_steps[-1]["status"] = "Completed"
        agent_steps[-1]["details"] = "Executive summary synthesized successfully."

        # Save active run state for live chatbot & scenario comparisons
        self.latest_allocation_res = allocation_res
        self.latest_scores_df = scores_res["scores_df"]
        self.latest_pref_df = pref_df
        self.latest_exp_df = exp_df
        self.latest_course_df = course_df

        scenario_entry = {
            "id": f"Scenario {len(self.scenario_history) + 1}",
            "weights": weights or {"preference": 0.4, "experience": 0.3, "skill": 0.2, "qualification": 0.1},
            "num_sections": allocation_res["num_sections"],
            "num_subjects": allocation_res["num_subjects"],
            "average_score": allocation_res["average_score"],
            "total_assignments": allocation_res["total_assignments"],
            "high_exp_faculty_count": allocation_res.get("high_exp_faculty_count", 0),
            "status": allocation_res["status"]
        }
        self.scenario_history.append(scenario_entry)

        return {
            "success": True,
            "agent_steps": agent_steps,
            "summary": {
                "num_sections": allocation_res["num_sections"],
                "num_subjects": allocation_res["num_subjects"],
                "sections_per_faculty": allocation_res["sections_per_faculty"],
                "faculty_required_per_subject": allocation_res["faculty_required_per_subject"],
                "high_exp_threshold": allocation_res.get("high_exp_threshold", high_exp_threshold),
                "high_exp_faculty_count": allocation_res.get("high_exp_faculty_count", 0),
                "total_assignments": allocation_res["total_assignments"],
                "average_score": allocation_res["average_score"],
                "status": allocation_res["status"],
                "excel_file": excel_path,
                "scenario_id": scenario_entry["id"]
            },
            "allocation_data": allocation_res,
            "ai_explanation": ai_explanation
        }

    def _generate_explanation(self, allocation_res: Dict[str, Any], scores_df: pd.DataFrame) -> str:
        """Generates natural language executive summary explaining L-T-P-C, high-experience 2+1 split, and designation hour bounds."""
        fac_allocs = allocation_res["faculty_allocations"]
        avg_score = allocation_res["average_score"]
        subjects = allocation_res["subjects"]
        c_details = allocation_res.get("course_details", {})
        high_exp_count = allocation_res.get("high_exp_faculty_count", 0)

        summary_text = (
            f"### Executive Allocation Summary\n"
            f"- **Optimization Status**: {allocation_res['status']}\n"
            f"- **Average Compatibility Score**: **{avg_score} / 100**\n"
            f"- **Sections**: {allocation_res['num_sections']} | **Subjects**: {allocation_res['num_subjects']}\n"
            f"- **High-Experience Rule Applied**: **{high_exp_count} faculty** with course teaching exp >= {allocation_res.get('high_exp_threshold', 8.0)} yrs received **2 sections in their highest-experienced course + 1 section in their 2nd highest-experienced course**.\n"
            f"- **Designation Workload Hours Applied**:\n"
            f"  - **Deans**: 4–6 hrs/wk\n"
            f"  - **HODs**: 10–12 hrs/wk\n"
            f"  - **Associate Professors**: 14–16 hrs/wk\n"
            f"  - **Assistant Professors**: 16–18 hrs/wk\n"
            f"- **Component Ratio**: Each section has 1 Main Lecture (L) faculty and 2 Tutorial/Practical (T/P) faculty.\n\n"
            f"### Subject L-T-P-C & Assignment Breakdown\n"
        )

        highlights = []
        for subj in subjects:
            ltpc = c_details.get(subj, {}).get("L-T-P-C", "N/A")
            tot_h = c_details.get(subj, {}).get("Total_Hours", 5)
            subj_allocs = [a for a in fac_allocs if a["Subject"] == subj]
            assigned_str = ", ".join([
                f"**{a['Lecture_Faculty_Name']}** ({a['Lecture_Designation']} - {a['Sections']} [{a['Num_Sections']} Secs, {a['Experience_Years']} yrs exp] - {a['Assigned_Weekly_Hours']} hrs/wk)"
                for a in subj_allocs
            ])
            highlights.append(f"- **{subj}** `[{ltpc}]` ({tot_h} hrs/sec): Assigned -> {assigned_str}")

        details_body = "\n".join(highlights)
        fallback_explanation = summary_text + details_body

        if self.client:
            try:
                prompt = (
                    "You are an AI Faculty Allocation Agent. Analyze the following optimal allocation result "
                    "produced by Google OR-Tools and write a professional executive summary explaining how L-T-P-C course structures "
                    "and designation workload hours (Deans: 4-6 hrs, HODs: 10-12 hrs, Associate Profs: 14-16 hrs, Assistant Profs: 16-18 hrs) "
                    "were satisfied.\n\n"
                    f"Data JSON:\n{json.dumps(fac_allocs, indent=2)}\n\n"
                    "Provide a clear, formatted markdown summary."
                )
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini generation call failed, using fallback: {e}")

        return fallback_explanation

    def handle_chat_query(self, user_question: str) -> Dict[str, Any]:
        """
        Processes natural language questions from Deans & HODs about active allocation results,
        workload distribution, non-assignments, and scenario comparisons.
        Capable of detailed queries on:
        - Particular faculty allocation (e.g. "tell details of Dr. Rajesh Kumar")
        - Particular course allocation (e.g. "details of Machine Learning allocation")
        - Particular section timetable (e.g. "allocation for Section A")
        - Department-wide and designation-wise workload patterns
        """
        q_clean = user_question.strip()
        q_lower = q_clean.lower()

        # If allocation has not been executed yet
        if not self.latest_allocation_res:
            from backend.excel_reader import load_all_excel_files
            from backend.workload_calculator import calculate_ltpc_workload, DEFAULT_PROMPT_COURSES
            try:
                comb_path = "input/faculty_sample_combined.xlsx"
                course_path = "input/course_details.xlsx"
                p_df, _, c_df = load_all_excel_files(comb_path if os.path.exists(comb_path) else "input/faculty_preferences.xlsx", None, course_path if os.path.exists(course_path) else None)
                fac_count = len(p_df) if p_df is not None else 34
                courses_count = len(c_df) if c_df is not None else len(DEFAULT_PROMPT_COURSES)
                wl = calculate_ltpc_workload(num_sections=12)
            except Exception:
                fac_count = 34
                courses_count = 7
                wl = {"section_total_workload": 73, "dept_total_workload": 876, "estimated_faculty_required": 58.4}

            msg = (
                "### 🤖 Allocation AI Assistant (Standby Mode)\n\n"
                "The optimization engine has not been run yet for this session. Here is the current curriculum baseline:\n\n"
                f"- **Available Faculty Roster**: {fac_count} faculty members loaded\n"
                f"- **Curriculum Courses**: {courses_count} courses configured with L-T-P-C contact hours\n"
                f"- **Baseline Workload Pattern**: **{wl.get('section_total_workload', 73)} hrs/week per section** (~**{wl.get('dept_total_workload', 876)} faculty-hours/week** for 12 sections)\n"
                f"- **Staffing Requirement**: ~**{wl.get('estimated_faculty_required', 58.4)} faculty** at standard 15 hrs capacity\n\n"
                "👉 Click **'GENERATE ALLOCATION'** on the left to compute optimal section assignments using OR-Tools, or click **'VIEW DATA'** to inspect faculty preferences and course contact hours!"
            )
            return {
                "success": True,
                "answer": msg,
                "suggested_questions": [
                    "What courses are loaded in the curriculum?",
                    "What is the theoretical workload pattern?",
                    "How does the High-Experience 2+1 split work?"
                ]
            }

        alloc_data = self.latest_allocation_res
        fac_allocs = alloc_data.get("faculty_allocations", [])
        subjects = alloc_data.get("subjects", [])
        section_names = alloc_data.get("section_names", [])
        matrix = alloc_data.get("final_allocation_matrix", {})
        c_details = alloc_data.get("course_details", {})
        scenarios = self.scenario_history
        wl_analysis = alloc_data.get("workload_analysis", {})

        # 1. Ask Gemini LLM if client is available
        if self.client:
            try:
                prompt = (
                    "You are the Conversational AI Assistant for an Academic Faculty-Subject-Section Allocation Agent.\n"
                    "Help the Dean/HOD by answering their question accurately based on the allocation data provided below.\n\n"
                    f"ACTIVE ALLOCATION METRICS:\n"
                    f"- Status: {alloc_data['status']}\n"
                    f"- Average Compatibility Score: {alloc_data['average_score']}/100\n"
                    f"- Sections: {alloc_data['num_sections']} | Subjects: {alloc_data['num_subjects']}\n"
                    f"- High Exp Faculty Count (>= {alloc_data.get('high_exp_threshold', 8.0)} yrs): {alloc_data.get('high_exp_faculty_count', 0)}\n\n"
                    f"FACULTY ASSIGNMENTS LIST:\n"
                    f"{json.dumps(fac_allocs, indent=2)}\n\n"
                    f"SCENARIO HISTORY FOR A/B TESTING:\n"
                    f"{json.dumps(scenarios, indent=2)}\n\n"
                    f"USER QUESTION: {user_question}\n\n"
                    "Respond concisely with professional markdown formatting (use bullet points or tables where appropriate)."
                )
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    return {
                        "success": True,
                        "answer": response.text,
                        "suggested_questions": [
                            "What is the workload pattern across designations?",
                            "Show faculty teaching > 15 hours/week",
                            "Tell details of a particular faculty member"
                        ]
                    }
            except Exception as e:
                print(f"Gemini chat generation failed: {e}")

        # 2. Rule-based Analytical Engine
        # -------------------------------------------------------------
        # QUERY MATCH 1: Specific Faculty Member Details
        # -------------------------------------------------------------
        matched_faculty_allocs = []
        for a in fac_allocs:
            fac_name = a.get("Lecture_Faculty_Name", "")
            fac_id = a.get("Lecture_Faculty_ID", "")
            tp1 = a.get("TP_Faculty_1_Name", "")
            tp2 = a.get("TP_Faculty_2_Name", "")

            # Check if name or ID appears in question
            name_parts = [p.lower() for p in fac_name.replace("Dr.", "").replace("Prof.", "").replace("Mr.", "").replace("Mrs.", "").replace("Ms.", "").split() if len(p) > 2]
            
            is_match = False
            if fac_id and fac_id.lower() in q_lower:
                is_match = True
            elif fac_name.lower() in q_lower:
                is_match = True
            elif any(part in q_lower for part in name_parts):
                is_match = True

            if is_match and a not in matched_faculty_allocs:
                matched_faculty_allocs.append(a)

        if matched_faculty_allocs:
            primary = matched_faculty_allocs[0]
            fac_name = primary.get("Lecture_Faculty_Name", "Faculty")
            role = primary.get("Lecture_Role", "Faculty")
            desig = primary.get("Lecture_Designation", "Faculty")
            subj = primary.get("Subject", "N/A")
            secs = primary.get("Sections", "N/A")
            num_secs = primary.get("Num_Sections", 0)
            hours = primary.get("Assigned_Weekly_Hours", 0)
            target = primary.get("Target_Hours_Range", "14-16 hrs")
            rank = primary.get("Preference_Rank", 1)
            score = primary.get("Score", 90.0)
            exp_yrs = primary.get("Experience_Years", 0.0)
            is_high_exp = primary.get("Is_High_Experience_Split", False)
            tp1_name = primary.get("TP_Faculty_1_Name", "Assigned Faculty")
            tp2_name = primary.get("TP_Faculty_2_Name", "Assigned Faculty")

            lines = [
                f"### 👤 Faculty Allocation Profile: **{fac_name}**",
                f"- **Designation & Role**: `{desig}` ({role})",
                f"- **Assigned Lecture Subject**: **{subj}** `[{primary.get('L-T-P-C', 'N/A')}]`",
                f"- **Assigned Sections**: **{secs}** ({num_secs} sections total)",
                f"- **Weekly Teaching Workload**: **{hours} hrs/week** (Institutional Target: `{target}`)",
                f"- **Preference Rank**: **Rank {rank} Choice** ({'1st Choice' if rank == 1 else f'Preference #{rank}'}) | Compatibility Score: **{score}/100**",
                f"- **Subject Teaching Experience**: **{exp_yrs} years**"
            ]

            if is_high_exp:
                lines.append(f"- ⭐ **High-Experience 2+1 Mentorship Split**: Enforced! Faculty with teaching experience $\\ge$ {alloc_data.get('high_exp_threshold', 8.0)} yrs received **2 sections** in primary course + **1 section** in secondary course.")

            lines.append(f"- **Paired Tutorial / Lab Assistants**: {tp1_name} & {tp2_name}")

            # Check if this faculty is also assisting as T/P in any other subject
            assisting = []
            for other_a in fac_allocs:
                if fac_name in (other_a.get("TP_Faculty_1_Name"), other_a.get("TP_Faculty_2_Name")):
                    assisting.append(f"{other_a.get('Subject')} ({other_a.get('Sections')})")

            if assisting:
                lines.append(f"- **Also Assisting as T/P Faculty in**: {', '.join(assisting)}")

            # Check other preferences if pref_df available
            if self.latest_pref_df is not None:
                p_match = self.latest_pref_df[self.latest_pref_df["Faculty_Name"].str.lower() == fac_name.lower()]
                if not p_match.empty:
                    row_p = p_match.iloc[0]
                    other_prefs = []
                    for r in range(1, 6):
                        c_val = row_p.get(f"Preference_{r}")
                        if pd.notna(c_val) and str(c_val).strip() and str(c_val).lower() != "nan":
                            other_prefs.append(f"{r}. {c_val}")
                    if other_prefs:
                        lines.append(f"\n**All Submitted Subject Preferences**:\n" + ", ".join(other_prefs))

            answer = "\n".join(lines)
            return {
                "success": True,
                "answer": answer,
                "suggested_questions": [
                    f"What is the workload pattern for {role}s?",
                    f"Show details of {subj} course allocation",
                    "What is the overall department workload pattern?"
                ]
            }

        # -------------------------------------------------------------
        # QUERY MATCH 2: Specific Subject / Course Allocation Details
        # -------------------------------------------------------------
        matched_subj = None
        for s in subjects:
            s_clean = s.lower().replace("-", " ")
            if s.lower() in q_lower or s_clean in q_lower:
                matched_subj = s
                break
            # Check keywords like "machine learning", "deep learning", "operating systems", "vision", "web"
            words = [w for w in s_clean.split() if len(w) > 3 and w not in ("with", "and", "de-2", "open")]
            if words and all(w in q_lower for w in words):
                matched_subj = s
                break

        if matched_subj:
            subj_allocs = [a for a in fac_allocs if a.get("Subject") == matched_subj]
            c_info = c_details.get(matched_subj, {})
            ltpc = c_info.get("L-T-P-C", "3-0-2-4")
            tot_h = c_info.get("Total_Hours", 5)
            cred = c_info.get("C", 4)
            num_sec = alloc_data.get("num_sections", 12)
            dept_contact = tot_h * num_sec

            lines = [
                f"### 📚 Course Allocation Details: **{matched_subj}**",
                f"- **L-T-P-C Structure**: `{ltpc}` | **Contact Hours**: {tot_h} hrs/section | **Credits**: {cred}",
                f"- **Department Contact Demand**: **{dept_contact} student contact hours/week** across all {num_sec} sections",
                f"- **Allocated Faculty Teams**:\n"
            ]

            lines.append("| Lecture Faculty (L) | Designation | Sections | Weekly Hours | Exp (Yrs) | Pref Rank |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for sa in subj_allocs:
                exp_str = f"{sa.get('Experience_Years', 0)}y"
                rank_str = f"Rank {sa.get('Preference_Rank', 1)}"
                lines.append(f"| **{sa.get('Lecture_Faculty_Name')}** | {sa.get('Lecture_Designation')} | `{sa.get('Sections')}` | **{sa.get('Assigned_Weekly_Hours')} hrs** | {exp_str} | {rank_str} |")

            lines.append("\n**Tutorial & Practical Support Faculty Pairs**:")
            for sa in subj_allocs:
                lines.append(f"- **{sa.get('Sections')}**: T/P 1: `{sa.get('TP_Faculty_1_Name')}` | T/P 2: `{sa.get('TP_Faculty_2_Name')}`")

            answer = "\n".join(lines)
            first_fac = subj_allocs[0].get('Lecture_Faculty_Name') if subj_allocs else "the faculty"
            return {
                "success": True,
                "answer": answer,
                "suggested_questions": [
                    f"Tell details of {first_fac}",
                    "What is the workload pattern across courses?",
                    "Show timetable for Section A"
                ]
            }

        # -------------------------------------------------------------
        # QUERY MATCH 3: Specific Section Timetable Details
        # -------------------------------------------------------------
        matched_sec = None
        for s_idx, sec in enumerate(section_names):
            clean_sec = sec.replace("Section ", "").strip().lower()
            pattern = rf"\b(?:section|sec)\s*[\-:]?\s*(?:{re.escape(clean_sec)}|{s_idx + 1})\b"
            if re.search(pattern, q_lower):
                matched_sec = sec
                break
            if re.search(rf"\b(?:timetable|schedule|roster)\s+(?:for\s+)?{re.escape(clean_sec)}\b", q_lower):
                matched_sec = sec
                break

        if matched_sec and matched_sec in matrix:
            sec_matrix = matrix[matched_sec]
            lines = [
                f"### 🏛️ Section Timetable Allocation: **{matched_sec}**",
                f"Full faculty staffing roster for **{matched_sec}** across all active courses:\n",
                "| Course Title | L-T-P-C | Main Lecture Faculty (L) | Tutorial / Lab Faculty 1 | Tutorial / Lab Faculty 2 | Hours/Wk |",
                "| :--- | :--- | :--- | :--- | :--- | :--- |"
            ]
            sec_total_hrs = 0
            for s in subjects:
                cell = sec_matrix.get(s, {})
                c_inf = c_details.get(s, {})
                ltpc = c_inf.get("L-T-P-C", "3-0-2-4")
                hrs = c_inf.get("Total_Hours", 5)
                sec_total_hrs += hrs
                if isinstance(cell, dict):
                    lines.append(f"| **{s}** | `{ltpc}` | **{cell.get('Lecture_Faculty')}** | {cell.get('TP_Faculty_1')} | {cell.get('TP_Faculty_2')} | {hrs} hrs |")
                else:
                    lines.append(f"| **{s}** | `{ltpc}` | {cell} | - | - | {hrs} hrs |")

            lines.append(f"\n> **Weekly Section Contact Hours Delivered**: **{sec_total_hrs} hours/week** across all subjects.")
            answer = "\n".join(lines)
            return {
                "success": True,
                "answer": answer,
                "suggested_questions": [
                    "What is the workload pattern across all sections?",
                    "Show faculty teaching > 15 hours/week",
                    "Details of Machine Learning allocation"
                ]
            }

        # -------------------------------------------------------------
        # QUERY MATCH 4: Workload Pattern / Distribution Analysis
        # -------------------------------------------------------------
        if any(kw in q_lower for kw in ["workload pattern", "workload", "pattern", "distribution", "teaching load", "load pattern", "hours pattern", "teaching hours", "capacity", "workload breakdown"]):
            # Calculate designation statistics
            role_stats = {
                "Dean": {"target": "4–6 hrs/wk", "faculty": [], "total_hrs": 0},
                "HOD": {"target": "10–12 hrs/wk", "faculty": [], "total_hrs": 0},
                "Associate Professor": {"target": "14–16 hrs/wk", "faculty": [], "total_hrs": 0},
                "Assistant Professor": {"target": "16–18 hrs/wk", "faculty": [], "total_hrs": 0},
                "Professor": {"target": "14–16 hrs/wk", "faculty": [], "total_hrs": 0}
            }

            all_hours = []
            for a in fac_allocs:
                r = a.get("Lecture_Role", "Faculty")
                h = a.get("Assigned_Weekly_Hours", 0)
                all_hours.append(h)
                matched_role = None
                for k in role_stats:
                    if k.lower() in r.lower():
                        matched_role = k
                        break
                if not matched_role:
                    matched_role = "Professor"
                role_stats[matched_role]["faculty"].append(a)
                role_stats[matched_role]["total_hrs"] += h

            avg_overall = round(sum(all_hours) / len(all_hours), 1) if all_hours else 14.0
            min_hrs = min(all_hours) if all_hours else 4
            max_hrs = max(all_hours) if all_hours else 18

            lines = [
                "### 📊 Institutional Workload Pattern & Staffing Distribution Analysis",
                f"- **Overall Faculty Workload**: Average **{avg_overall} hrs/week** (Range: {min_hrs} – {max_hrs} hrs/week)",
                f"- **Department Contact Demand**: **{wl_analysis.get('dept_total_workload', 876)} faculty-hours/week** delivered across **{alloc_data.get('num_sections', 12)} sections**",
                f"- **Section Workload Pattern**: **{wl_analysis.get('section_total_workload', 73)} hrs/week** per academic section\n",
                "#### 1. Workload Pattern by Faculty Designation",
                "| Designation | Faculty Count | Policy Workload Target | Actual Average | Actual Range | Compliance Status |",
                "| :--- | :--- | :--- | :--- | :--- | :--- |"
            ]

            for r_name, r_data in role_stats.items():
                cnt = len(r_data["faculty"])
                if cnt == 0:
                    continue
                avg_h = round(r_data["total_hrs"] / cnt, 1)
                r_hrs = [fa.get("Assigned_Weekly_Hours", 0) for fa in r_data["faculty"]]
                min_h = min(r_hrs)
                max_h = max(r_hrs)
                compliance = "✓ Compliant with Policy" if min_h >= 4 and max_h <= 18 else "Balanced"
                lines.append(f"| **{r_name}** | {cnt} | `{r_data['target']}` | **{avg_h} hrs/wk** | {min_h}–{max_h} hrs | {compliance} |")

            lines.append("\n#### 2. Curriculum L-T-P Component Workload Split")
            dept_l = wl_analysis.get('dept_l_load', 156)
            dept_t = wl_analysis.get('dept_t_load', 288)
            dept_p = wl_analysis.get('dept_p_load', 432)
            dept_tot = wl_analysis.get('dept_total_workload', 876) or 876
            pct_l = round((dept_l / dept_tot) * 100, 1)
            pct_t = round((dept_t / dept_tot) * 100, 1)
            pct_p = round((dept_p / dept_tot) * 100, 1)

            lines.append(f"- **Lecture (L) Share**: **{dept_l} hrs** ({pct_l}%) – Assigned at 1 faculty per section")
            lines.append(f"- **Tutorial (T) Share**: **{dept_t} hrs** ({pct_t}%) – Assigned at 3 faculty per section for personalized small groups")
            lines.append(f"- **Practical (P) Share**: **{dept_p} hrs** ({pct_p}%) – Assigned at 3 faculty per section for dual laboratory supervision")
            lines.append(f"- **Theory-to-Practical Ratio**: **{wl_analysis.get('theory_to_practical_ratio', 0.65)} : 1** (Healthy practical-oriented curriculum)")

            lines.append("\n#### 3. High-Experience Mentorship Workload Rule")
            high_count = alloc_data.get('high_exp_faculty_count', 0)
            threshold = alloc_data.get('high_exp_threshold', 8.0)
            lines.append(f"- Applied to **{high_count} senior faculty** with teaching experience $\\ge$ {threshold} years:")
            lines.append("  - **2 sections** in primary highest-experienced course")
            lines.append("  - **1 section** in secondary experienced course")
            lines.append("  - Ensures senior subject leadership while distributing expertise across multiple cohorts.")

            answer = "\n".join(lines)
            return {
                "success": True,
                "answer": answer,
                "suggested_questions": [
                    "Show faculty teaching > 15 hours/week",
                    "Details of Machine Learning allocation",
                    "Compare current run with previous scenario"
                ]
            }

        # -------------------------------------------------------------
        # QUERY MATCH 5: Specific Designation Workload (Dean, HOD, etc.)
        # -------------------------------------------------------------
        for role_key, role_label in [("dean", "Dean"), ("hod", "HOD"), ("assistant", "Assistant Professor"), ("associate", "Associate Professor")]:
            if role_key in q_lower:
                role_facs = [a for a in fac_allocs if role_key in a.get("Lecture_Role", "").lower() or role_key in a.get("Lecture_Designation", "").lower()]
                if role_facs:
                    lines = [
                        f"### 📋 {role_label} Workload Details",
                        f"Found **{len(role_facs)} faculty member(s)** in the {role_label} designation:\n",
                        "| Faculty Name | Designation | Assigned Course | Sections | Assigned Hours | Target Policy |",
                        "| :--- | :--- | :--- | :--- | :--- | :--- |"
                    ]
                    for a in role_facs:
                        lines.append(f"| **{a.get('Lecture_Faculty_Name')}** | {a.get('Lecture_Designation')} | {a.get('Subject')} | `{a.get('Sections')}` | **{a.get('Assigned_Weekly_Hours')} hrs** | `{a.get('Target_Hours_Range')}` |")
                    answer = "\n".join(lines)
                    return {
                        "success": True,
                        "answer": answer,
                        "suggested_questions": [
                            "What is the workload pattern across all designations?",
                            "Show faculty teaching > 15 hours/week",
                            "Compare current run with previous scenario"
                        ]
                    }

        # -------------------------------------------------------------
        # QUERY MATCH 6: Scenario Comparison / A/B Testing
        # -------------------------------------------------------------
        if any(kw in q_lower for kw in ["compare", "scenario", "previous", "a/b", "weight", "run"]):
            if len(scenarios) <= 1:
                answer = (
                    "### 🔄 Scenario Comparison (A/B Testing)\n"
                    "You currently have **1 allocation run** recorded in this session.\n\n"
                    "💡 **How to Test Scenarios:**\n"
                    "1. Adjust the scoring weight sliders (Preference, Experience, Skill, Qualification) in the left panel.\n"
                    "2. Click **'GENERATE ALLOCATION'** again.\n"
                    "3. Return to the chat to compare average satisfaction scores and section distribution side-by-side!"
                )
            else:
                lines = [
                    "### 🔄 Scenario Comparison (A/B Testing Results)",
                    "| Scenario ID | Weights (Pref/Exp/Skill/Qual) | Avg Score | Total Assignments | High Exp Faculty | Status |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- |"
                ]
                for s in scenarios:
                    w = s.get("weights", {})
                    w_str = f"P:{int(w.get('preference',0)*100)}% E:{int(w.get('experience',0)*100)}% S:{int(w.get('skill',0)*100)}% Q:{int(w.get('qualification',0)*100)}%"
                    lines.append(f"| **{s['id']}** | {w_str} | **{s['average_score']}/100** | {s['total_assignments']} | {s['high_exp_faculty_count']} | `{s['status']}` |")
                
                s_first = scenarios[0]
                s_last = scenarios[-1]
                diff = round(s_last['average_score'] - s_first['average_score'], 2)
                diff_str = f"+{diff}" if diff > 0 else f"{diff}"
                lines.append(f"\n📈 **Score Impact:** From {s_first['id']} to {s_last['id']}, average compatibility score changed by **{diff_str} points**.")
                answer = "\n".join(lines)

            return {
                "success": True,
                "answer": answer,
                "suggested_questions": [
                    "What is the workload pattern across designations?",
                    "Show faculty teaching > 15 hours/week",
                    "Details of Machine Learning allocation"
                ]
            }

        # -------------------------------------------------------------
        # QUERY MATCH 7: Why / Rationale queries
        # -------------------------------------------------------------
        if any(kw in q_lower for kw in ["why", "not assigned", "assign", "smith", "reason", "rationale"]):
            answer = (
                "### 🔍 Assignment Rationale Analysis\n"
                "The Google OR-Tools CP-SAT solver maximizes the global compatibility score subject to strict institutional constraints:\n\n"
                "1. **Preference Priority:** 1st preference ranks carry 100 points, while 5th preference carries only 10 points.\n"
                "2. **Experience & Qualification Filtering:** Non-qualified faculty are strictly excluded from subjects.\n"
                "3. **High-Experience 2+1 Rule:** Faculty with $\\ge$ 8 years experience get 2 sections in top-1 course + 1 section in top-2 course.\n"
                "4. **Workload Caps:** Deans (max 2 sections / 4-6 hrs), HODs (max 3 sections / 10-12 hrs), preventing over-allocation.\n"
                "5. **Equal Component Ratio:** Each section receives 1 Main Lecture (L) faculty and 2 Tutorial/Practical (T/P) faculty for comprehensive classroom delivery.\n\n"
                "To inspect exact scores for any faculty-subject pair, open the **'Detailed Breakdown'** sheet in the exported Excel workbook."
            )
            return {
                "success": True,
                "answer": answer,
                "suggested_questions": [
                    "What is the workload pattern across designations?",
                    "Show faculty teaching > 15 hours/week",
                    "Details of Machine Learning allocation"
                ]
            }

        # -------------------------------------------------------------
        # DEFAULT / GENERAL OVERVIEW
        # -------------------------------------------------------------
        first_fac_name = fac_allocs[0].get('Lecture_Faculty_Name') if fac_allocs else "Dr. Rajesh Kumar"
        first_subj_name = subjects[0] if subjects else "Machine Learning"
        lines = [
            "### 🤖 Allocation AI Assistant Overview",
            f"- **Optimization Status**: `{alloc_data['status']}`",
            f"- **Average Compatibility Score**: **{alloc_data['average_score']} / 100**",
            f"- **Total Course Assignments**: **{alloc_data['total_assignments']}** across **{alloc_data['num_sections']} sections**",
            f"- **High-Experience Mentorship Splits**: **{alloc_data.get('high_exp_faculty_count', 0)} faculty** with teaching exp $\\ge$ {alloc_data.get('high_exp_threshold', 8.0)} yrs",
            f"- **Department Workload**: **{wl_analysis.get('dept_total_workload', 876)} faculty-hours/week**",
            "\n💡 **You can ask me questions like:**",
            f"- *\"Tell details of {first_fac_name} allocation\"*",
            f"- *\"What is the allocation for {first_subj_name}?\"*",
            "- *\"What is the workload pattern across designations?\"*",
            "- *\"Show timetable for Section A\"*",
            "- *\"Show faculty teaching > 15 hours/week\"*"
        ]
        return {
            "success": True,
            "answer": "\n".join(lines),
            "suggested_questions": [
                f"Tell details of {first_fac_name}",
                f"Details of {first_subj_name} allocation",
                "What is the workload pattern across designations?",
                "Show timetable for Section A"
            ]
        }

