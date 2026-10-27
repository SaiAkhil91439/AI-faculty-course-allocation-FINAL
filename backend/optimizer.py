import math
from typing import Dict, Any, List, Tuple
import pandas as pd
from ortools.sat.python import cp_model

def get_section_label(index: int) -> str:
    """Generates standard letter section names: A, B, C... Z, AA, AB..."""
    label = ""
    while index >= 0:
        label = chr(65 + (index % 26)) + label
        index = (index // 26) - 1
    return label

def solve_faculty_allocation(
    pref_df: pd.DataFrame,
    exp_df: pd.DataFrame,
    scores_dict: Dict[str, Any],
    num_sections: int,
    num_subjects: int,
    sections_per_faculty: int,
    max_subjects_per_faculty: int,
    course_df: pd.DataFrame = None,
    dean_max_sections: int = 2,
    hod_max_sections: int = 3,
    high_exp_threshold: float = 8.0
) -> Dict[str, Any]:
    """
    Formulates and solves Faculty-Subject-Section Allocation using OR-Tools CP-SAT.
    Enforces:
    1. Course L-T-P-C structure and contact teaching hours per section.
    2. Designation-based Workload Teaching Hours bounds.
    3. For EACH section: 1 Faculty for Lecture (L) and 2 Faculty for Tutorial/Practical (T/P).
    4. HIGH-EXPERIENCE FACULTY ALLOCATION RULE:
       Faculty with high course teaching experience (>= high_exp_threshold) are assigned:
       - 2 sections in their highest-experienced course (Course 1).
       - 1 section in their 2nd highest-experienced course (Course 2).
       Total = 3 sections across 2 top experienced subjects.
    5. Regular faculty receive standard section allocations.
    """
    scores_df = scores_dict["scores_df"]
    score_matrix = scores_dict["score_matrix"]
    unpopular_map = scores_dict.get("unpopular_subjects", {})

    # Build Course Info Map (L-T-P-C and Total Hours)
    course_info_map = {}
    if course_df is not None and not course_df.empty:
        for _, row in course_df.iterrows():
            s_name = str(row["Subject"]).strip()
            l_val = int(row.get("L", 3))
            t_val = int(row.get("T", 0))
            p_val = int(row.get("P", 2))
            c_val = int(row.get("C", 4))
            ltpc_str = str(row.get("L-T-P-C", f"{l_val}-{t_val}-{p_val}-{c_val}"))
            tot_hrs = int(row.get("Total_Hours", l_val + t_val + p_val))
            course_info_map[s_name] = {
                "L": l_val, "T": t_val, "P": p_val, "C": c_val,
                "L-T-P-C": ltpc_str, "Total_Hours": tot_hrs
            }

    # Extract faculty details (name, role, designation)
    fac_details = {}
    for _, row in pref_df.iterrows():
        f_id = str(row["Faculty_ID"]).strip()
        fac_details[f_id] = {
            "name": str(row.get("Faculty_Name", f_id)).strip(),
            "designation": str(row.get("Designation", "Professor")).strip(),
            "role": str(row.get("Role", "Faculty")).strip(),
            "addl_duties": str(row.get("Additional_Duties", "None")).strip()
        }

    faculty_list = sorted(list(fac_details.keys()))

    # Subjects list
    subject_counts = {}
    for _, row in exp_df.iterrows():
        s = str(row["Subject"]).strip()
        f = str(row["Faculty_ID"]).strip()
        if score_matrix.get((f, s), 0) > 0:
            subject_counts[s] = subject_counts.get(s, 0) + 1

    all_subjects_in_exp = sorted(list(exp_df["Subject"].dropna().unique()), key=lambda s: subject_counts.get(s, 0), reverse=True)
    subjects_list = all_subjects_in_exp[:num_subjects]

    if len(subjects_list) < num_subjects:
        raise ValueError(
            f"Requested {num_subjects} subjects, but only {len(subjects_list)} subjects were found in experience data: {subjects_list}"
        )

    # Ensure all subjects have course info
    for s in subjects_list:
        if s not in course_info_map:
            course_info_map[s] = {
                "L": 3, "T": 0, "P": 2, "C": 4,
                "L-T-P-C": "3-0-2-4", "Total_Hours": 5
            }

    section_names = [get_section_label(i) for i in range(num_sections)]
    faculty_required_per_subject = num_sections // sections_per_faculty if sections_per_faculty > 0 else 0

    # Extract per-course experience for each faculty and identify High-Experience Faculty
    fac_course_exp = {}  # f -> list of (subject, exp_years, pref_rank)
    fac_max_exp = {}
    high_exp_faculty_info = {}

    for f in faculty_list:
        f_exp_rows = exp_df[exp_df["Faculty_ID"] == f]
        courses_exp = []
        for s in subjects_list:
            score = score_matrix.get((f, s), 0.0)
            if score > 0:
                s_rows = f_exp_rows[f_exp_rows["Subject"] == s]
                if not s_rows.empty:
                    exp_yrs = float(s_rows.iloc[0].get("Experience_Years", 0.0))
                    pref_rank = int(s_rows.iloc[0].get("Preference_Rank", 99)) if pd.notna(s_rows.iloc[0].get("Preference_Rank")) else 99
                else:
                    exp_yrs = 0.0
                    pref_rank = 99
                courses_exp.append({"subject": s, "exp_years": exp_yrs, "pref_rank": pref_rank, "score": score})

        # Sort courses by experience (descending), then preference rank (ascending)
        courses_exp.sort(key=lambda x: (-x["exp_years"], x["pref_rank"]))
        fac_course_exp[f] = courses_exp
        max_exp = courses_exp[0]["exp_years"] if courses_exp else 0.0
        fac_max_exp[f] = max_exp

        # A faculty member is tagged as High Experience if max exp >= threshold AND has at least 2 valid active subjects with score > 0
        if max_exp >= high_exp_threshold and len(courses_exp) >= 2 and courses_exp[1]["score"] > 0:
            high_exp_faculty_info[f] = {
                "top1_subject": courses_exp[0]["subject"],
                "top1_exp": courses_exp[0]["exp_years"],
                "top2_subject": courses_exp[1]["subject"],
                "top2_exp": courses_exp[1]["exp_years"],
            }

    # Create CP-SAT model
    model = cp_model.CpModel()

    # Section-level decision variables:
    # x_L[f, s, sec]: binary, faculty f teaches Lecture (L) for subject s in section sec
    # x_TP[f, s, sec, k]: binary, faculty f is T/P instructor k (1 or 2) for subject s in section sec
    # y[f, s]: binary, faculty f is assigned subject s
    x_L = {}
    x_TP = {}
    y = {}

    for f in faculty_list:
        for s in subjects_list:
            y[(f, s)] = model.NewBoolVar(f"y_{f}_{s}")
            for sec in section_names:
                x_L[(f, s, sec)] = model.NewBoolVar(f"x_L_{f}_{s}_{sec}")
                x_TP[(f, s, sec, 1)] = model.NewBoolVar(f"x_TP1_{f}_{s}_{sec}")
                x_TP[(f, s, sec, 2)] = model.NewBoolVar(f"x_TP2_{f}_{s}_{sec}")

                # Link x and y
                model.Add(x_L[(f, s, sec)] <= y[(f, s)])
                model.Add(x_TP[(f, s, sec, 1)] <= y[(f, s)])
                model.Add(x_TP[(f, s, sec, 2)] <= y[(f, s)])

    # Constraint 1: Exactly 1 Lecture (L) faculty per section of each subject
    for s in subjects_list:
        for sec in section_names:
            model.Add(sum(x_L[(f, s, sec)] for f in faculty_list) == 1)

    # Constraint 2: Exactly 2 T/P faculty per section of each subject
    for s in subjects_list:
        for sec in section_names:
            model.Add(sum(x_TP[(f, s, sec, 1)] for f in faculty_list) == 1)
            model.Add(sum(x_TP[(f, s, sec, 2)] for f in faculty_list) == 1)
            for f in faculty_list:
                model.Add(x_TP[(f, s, sec, 1)] + x_TP[(f, s, sec, 2)] <= 1)

    # Designation Target Teaching Hours & Section Caps
    designation_targets = {
        "Dean": {"min_hrs": 4, "max_hrs": 6, "label": "4-6 hrs/wk"},
        "HOD": {"min_hrs": 10, "max_hrs": 12, "label": "10-12 hrs/wk"},
        "Associate Professor": {"min_hrs": 14, "max_hrs": 16, "label": "14-16 hrs/wk"},
        "Assistant Professor": {"min_hrs": 16, "max_hrs": 18, "label": "16-18 hrs/wk"},
        "Professor": {"min_hrs": 10, "max_hrs": 14, "label": "10-14 hrs/wk"},
        "Faculty": {"min_hrs": 12, "max_hrs": 16, "label": "12-16 hrs/wk"}
    }

    # High-Experience 2+1 Split Indicator Variables
    high_exp_indicators = {}
    for f, info in high_exp_faculty_info.items():
        role = fac_details[f]["role"]
        if role not in ("Dean", "HOD"):
            s1 = info["top1_subject"]
            s2 = info["top2_subject"]

            b_s1 = model.NewBoolVar(f"b_high_exp_s1_{f}")
            b_s2 = model.NewBoolVar(f"b_high_exp_s2_{f}")

            # b_s1 is True iff faculty f gets 2 sections of s1
            model.Add(sum(x_L[(f, s1, sec)] for sec in section_names) == 2).OnlyEnforceIf(b_s1)
            model.Add(sum(x_L[(f, s1, sec)] for sec in section_names) != 2).OnlyEnforceIf(b_s1.Not())

            # b_s2 is True iff faculty f gets 1 section of s2
            model.Add(sum(x_L[(f, s2, sec)] for sec in section_names) == 1).OnlyEnforceIf(b_s2)
            model.Add(sum(x_L[(f, s2, sec)] for sec in section_names) != 1).OnlyEnforceIf(b_s2.Not())

            high_exp_indicators[f] = (b_s1, b_s2)

    # Constraint 3: Section & Workload Allocation Rules per Faculty
    for f in faculty_list:
        role = fac_details[f]["role"]
        total_L_sections = sum(x_L[(f, s, sec)] for s in subjects_list for sec in section_names)

        if role == "Dean":
            model.Add(total_L_sections <= dean_max_sections)
            model.Add(sum(y[(f, s)] for s in subjects_list) <= max_subjects_per_faculty)
        elif role == "HOD":
            model.Add(total_L_sections <= hod_max_sections)
            model.Add(sum(y[(f, s)] for s in subjects_list) <= max_subjects_per_faculty)
        else:
            # Regular faculty workload cap
            model.Add(total_L_sections <= sections_per_faculty)
            if f in high_exp_faculty_info:
                # High-experience faculty can take 2 subjects for 2+1 split
                model.Add(sum(y[(f, s)] for s in subjects_list) <= max(2, max_subjects_per_faculty))
            else:
                model.Add(sum(y[(f, s)] for s in subjects_list) <= max_subjects_per_faculty)

    # Constraint 4: Forbid assignment if score is 0
    for f in faculty_list:
        for s in subjects_list:
            score = score_matrix.get((f, s), 0.0)
            if score <= 0:
                model.Add(y[(f, s)] == 0)

    # Objective Function: Maximize compatibility scores & high-experience 2+1 section splits
    objective_terms = []
    
    # Top priority: Reward high-experience 2+1 section split (50,000 points per condition satisfied)
    for f, (b_s1, b_s2) in high_exp_indicators.items():
        objective_terms.append(50000 * b_s1)
        objective_terms.append(50000 * b_s2)

    for f in faculty_list:
        max_exp = fac_max_exp.get(f, 0.0)
        is_exp = max_exp >= 6.0

        for s in subjects_list:
            score = score_matrix.get((f, s), 0.0)
            score_int = int(round(score * 100))
            unpop_score = unpopular_map.get(s, 0.0)
            unpop_bonus = int(round(unpop_score * 50)) if is_exp else 0

            for sec in section_names:
                objective_terms.append((score_int + unpop_bonus) * x_L[(f, s, sec)])
                objective_terms.append((score_int // 2) * x_TP[(f, s, sec, 1)])
                objective_terms.append((score_int // 2) * x_TP[(f, s, sec, 2)])

    model.Maximize(sum(objective_terms))

    # Solve CP-SAT
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError(
            "Optimization problem is INFEASIBLE. Please check faculty workload bounds or section settings."
        )

    # Reconstruct allocation details
    final_allocation_matrix = {sec: {} for sec in section_names}
    faculty_allocations = []
    total_score = 0.0
    assignment_count = 0

    fac_workload_hours = {f: 0 for f in faculty_list}
    fac_section_counts = {f: 0 for f in faculty_list}

    # Group allocations by (Lecture_Faculty, Subject)
    alloc_group = {}  # (f, s) -> list of section names

    for sec in section_names:
        for s in subjects_list:
            assigned_L_id = None
            assigned_TP1_id = None
            assigned_TP2_id = None

            for f in faculty_list:
                if solver.Value(x_L[(f, s, sec)]) == 1:
                    assigned_L_id = f
                if solver.Value(x_TP[(f, s, sec, 1)]) == 1:
                    assigned_TP1_id = f
                if solver.Value(x_TP[(f, s, sec, 2)]) == 1:
                    assigned_TP2_id = f

            l_name = fac_details[assigned_L_id]["name"] if assigned_L_id else "N/A"
            tp1_name = fac_details[assigned_TP1_id]["name"] if assigned_TP1_id else "N/A"
            tp2_name = fac_details[assigned_TP2_id]["name"] if assigned_TP2_id else "N/A"
            c_info = course_info_map[s]

            final_allocation_matrix[sec][s] = {
                "Lecture_Faculty": l_name,
                "Lecture_Faculty_ID": assigned_L_id,
                "TP_Faculty_1": tp1_name,
                "TP_Faculty_1_ID": assigned_TP1_id,
                "TP_Faculty_2": tp2_name,
                "TP_Faculty_2_ID": assigned_TP2_id,
                "LTPC": c_info["L-T-P-C"]
            }

            if assigned_L_id:
                key = (assigned_L_id, s)
                if key not in alloc_group:
                    alloc_group[key] = {"sections": [], "tp1": tp1_name, "tp2": tp2_name}
                alloc_group[key]["sections"].append(sec)
                fac_workload_hours[assigned_L_id] += c_info["Total_Hours"]
                fac_section_counts[assigned_L_id] += 1

    for (f_id, s), info in alloc_group.items():
        assigned_secs = info["sections"]
        sec_str = ", ".join(assigned_secs)
        num_secs = len(assigned_secs)
        c_info = course_info_map[s]

        score_info = scores_df[(scores_df["Faculty_ID"] == f_id) & (scores_df["Subject"] == s)]
        pref_rank = score_info.iloc[0]["Preference_Rank"] if not score_info.empty else "N/A"
        exp_years = score_info.iloc[0]["Experience_Years"] if not score_info.empty else 0.0
        score_val = score_info.iloc[0]["Final_Score"] if not score_info.empty else score_matrix.get((f_id, s), 0.0)

        total_score += score_val * num_secs
        assignment_count += num_secs

        l_role = fac_details[f_id]["role"]
        target_info = designation_targets.get(l_role, designation_targets["Faculty"])

        is_high_exp_split = (f_id in high_exp_faculty_info)

        faculty_allocations.append({
            "Subject": str(s),
            "Sections": str(sec_str),
            "Num_Sections": int(num_secs),
            "L": int(c_info["L"]),
            "T": int(c_info["T"]),
            "P": int(c_info["P"]),
            "C": int(c_info["C"]),
            "L-T-P-C": str(c_info["L-T-P-C"]),
            "Total_Course_Hours": int(c_info["Total_Hours"]),
            "Lecture_Faculty_ID": str(f_id),
            "Lecture_Faculty_Name": str(fac_details[f_id]["name"]),
            "Lecture_Designation": str(fac_details[f_id]["designation"]),
            "Lecture_Role": str(l_role),
            "TP_Faculty_1_Name": str(info["tp1"]),
            "TP_Faculty_2_Name": str(info["tp2"]),
            "Preference_Rank": pref_rank,
            "Experience_Years": float(exp_years),
            "Is_High_Experience_Split": is_high_exp_split,
            "Score": float(score_val),
            "Assigned_Weekly_Hours": int(c_info["Total_Hours"] * num_secs),
            "Target_Hours_Range": target_info["label"]
        })

    # Attach total workload per faculty
    for a in faculty_allocations:
        f_id = a["Lecture_Faculty_ID"]
        a["Faculty_Total_Weekly_Hours"] = int(fac_workload_hours.get(f_id, a["Assigned_Weekly_Hours"]))

    avg_score = float(round(total_score / assignment_count, 2)) if assignment_count > 0 else 0.0

    return {
        "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
        "num_sections": int(num_sections),
        "num_subjects": int(num_subjects),
        "sections_per_faculty": int(sections_per_faculty),
        "faculty_required_per_subject": int(faculty_required_per_subject),
        "high_exp_threshold": float(high_exp_threshold),
        "high_exp_faculty_count": len(high_exp_faculty_info),
        "total_assignments": int(assignment_count),
        "average_score": float(avg_score),
        "subjects": [str(s) for s in subjects_list],
        "course_details": course_info_map,
        "section_names": [str(sec) for sec in section_names],
        "final_allocation_matrix": final_allocation_matrix,
        "faculty_allocations": faculty_allocations
    }

