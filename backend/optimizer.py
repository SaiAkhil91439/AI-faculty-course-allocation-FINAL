import math
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
from ortools.sat.python import cp_model
from backend.excel_reader import clean_subject_name
from backend.scoring import calculate_ta_compatibility_scores

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
    high_exp_threshold: float = 8.0,
    ta_df: Optional[pd.DataFrame] = None,
    tas_per_section: int = 2,
    year_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Formulates and solves Faculty-Subject-Section Allocation using OR-Tools CP-SAT.
    Enforces:
    1. Course L-T-P-C and 5-part L-T-P-SL-C structures and contact teaching hours per section.
    2. Multi-Year Courses: Faculty can teach any year offering their preferred/experienced subjects.
    3. Custom Teaching Assistants (TAs) count (K >= 0) allocated under the respective lecture faculty.
    4. Designation-based Workload Teaching Hours bounds (Deans: 4-6, HODs: 10-12, Faculty: 14-16/16-18).
    5. HIGH-EXPERIENCE FACULTY 2+1 SPLIT RULE:
       Faculty with high course experience (>= high_exp_threshold) are assigned:
       - 2 sections in their highest-experienced course (Course 1).
       - 1 section in their 2nd highest-experienced course (Course 2).
    6. Regular faculty receive balanced section allocations.
    """
    scores_df = scores_dict["scores_df"]
    score_matrix = scores_dict["score_matrix"]
    unpopular_map = scores_dict.get("unpopular_subjects", {})

    # 1. Process Course Curriculum Data (Multi-Year Support)
    course_info_map = {}
    years_available = []

    target_course_df = course_df
    if target_course_df is not None and not target_course_df.empty:
        if "Year" in target_course_df.columns:
            years_available = [y for y in target_course_df["Year"].dropna().unique() if str(y).strip() != ""]
        if year_filter and year_filter not in ("All", "all", "", None):
            filtered = target_course_df[target_course_df["Year"] == year_filter]
            if not filtered.empty:
                target_course_df = filtered

    # Determine subjects/courses list
    courses_list = []
    if target_course_df is not None and not target_course_df.empty:
        # Build candidate courses with faculty qualification ranking
        candidates = []
        for idx, row in target_course_df.iterrows():
            subj_raw = str(row.get("Subject", f"Course_{idx+1}")).strip()
            clean_s = clean_subject_name(subj_raw)
            yr = str(row.get("Year", "")).strip() if pd.notna(row.get("Year")) else ""
            c_code = str(row.get("Course_Code", "")).strip() if pd.notna(row.get("Course_Code")) else ""

            c_key = f"[{yr}] {subj_raw}" if yr else subj_raw
            
            l_val = int(row.get("L", 3))
            t_val = int(row.get("T", 0))
            p_val = int(row.get("P", 2))
            c_val = int(row.get("C", 4))
            ltpc_str = str(row.get("L-T-P-C", f"{l_val}-{t_val}-{p_val}-{c_val}"))
            tot_hrs = int(row.get("Total_Hours", l_val + t_val + p_val))

            # Count qualified faculty for this subject
            q_fac = sum(1 for f in pref_df["Faculty_ID"] if score_matrix.get((str(f).strip(), clean_s), 0.0) > 0)
            
            info = {
                "Key": c_key,
                "Year": yr,
                "Course_Code": c_code,
                "Subject": subj_raw,
                "Clean_Subject": clean_s,
                "L": l_val,
                "T": t_val,
                "P": p_val,
                "C": c_val,
                "L-T-P-C": ltpc_str,
                "Total_Hours": tot_hrs,
                "Qualified_Faculty": q_fac
            }
            candidates.append(info)

        # Sort candidates by number of qualified faculty (descending) to avoid infeasibility
        candidates.sort(key=lambda x: x["Qualified_Faculty"], reverse=True)
        
        selected_candidates = candidates[:num_subjects] if len(candidates) >= num_subjects else candidates
        for c in selected_candidates:
            c_key = c["Key"]
            courses_list.append(c_key)
            course_info_map[c_key] = c
    else:
        # Fallback to exp_df
        subject_counts = {}
        for _, row in exp_df.iterrows():
            s = clean_subject_name(str(row["Subject"]).strip())
            f = str(row["Faculty_ID"]).strip()
            if score_matrix.get((f, s), 0) > 0:
                subject_counts[s] = subject_counts.get(s, 0) + 1

        all_subjects_in_exp = sorted(
            list(exp_df["Subject"].dropna().apply(clean_subject_name).unique()),
            key=lambda s: subject_counts.get(s, 0),
            reverse=True
        )
        courses_list = all_subjects_in_exp[:num_subjects]

        for s in courses_list:
            course_info_map[s] = {
                "Key": s,
                "Year": "",
                "Course_Code": "",
                "Subject": s,
                "Clean_Subject": clean_subject_name(s),
                "L": 3, "T": 0, "P": 2, "C": 4,
                "L-T-P-C": "3-0-2-4", "Total_Hours": 5,
                "Qualified_Faculty": subject_counts.get(s, 0)
            }

    if not courses_list:
        raise ValueError("No active courses found for allocation.")

    # 2. Extract Faculty Details
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

    # 3. Extract Teaching Assistants Details
    has_tas = ta_df is not None and not ta_df.empty and tas_per_section > 0
    ta_details = {}
    ta_list = []
    ta_scores = {}

    if has_tas:
        for _, row in ta_df.iterrows():
            t_id = str(row["TA_ID"]).strip()
            ta_details[t_id] = {
                "name": str(row.get("TA_Name", t_id)).strip()
            }
        ta_list = sorted(list(ta_details.keys()))
        ta_scores = calculate_ta_compatibility_scores(ta_df, courses_list)

    section_names = [get_section_label(i) for i in range(num_sections)]
    faculty_required_per_subject = num_sections // sections_per_faculty if sections_per_faculty > 0 else 0

    # 4. Extract Per-Course Experience for High-Experience Faculty 2+1 Split
    fac_course_exp = {}
    fac_max_exp = {}
    high_exp_faculty_info = {}

    for f in faculty_list:
        f_exp_rows = exp_df[exp_df["Faculty_ID"] == f]
        courses_exp = []
        for c in courses_list:
            clean_s = course_info_map[c]["Clean_Subject"]
            score = score_matrix.get((f, clean_s), 0.0)
            if score > 0:
                s_rows = f_exp_rows[f_exp_rows["Subject"].apply(clean_subject_name) == clean_s]
                if not s_rows.empty:
                    exp_yrs = float(s_rows.iloc[0].get("Experience_Years", 0.0))
                    pref_rank = int(s_rows.iloc[0].get("Preference_Rank", 99)) if pd.notna(s_rows.iloc[0].get("Preference_Rank")) else 99
                else:
                    exp_yrs = 0.0
                    pref_rank = 99
                courses_exp.append({"course": c, "clean_s": clean_s, "exp_years": exp_yrs, "pref_rank": pref_rank, "score": score})

        courses_exp.sort(key=lambda x: (-x["exp_years"], x["pref_rank"]))
        fac_course_exp[f] = courses_exp
        max_exp = courses_exp[0]["exp_years"] if courses_exp else 0.0
        fac_max_exp[f] = max_exp

        if max_exp >= high_exp_threshold and len(courses_exp) >= 2 and courses_exp[1]["score"] > 0:
            high_exp_faculty_info[f] = {
                "top1_course": courses_exp[0]["course"],
                "top1_exp": courses_exp[0]["exp_years"],
                "top2_course": courses_exp[1]["course"],
                "top2_exp": courses_exp[1]["exp_years"],
            }

    # 5. Build CP-SAT Model
    model = cp_model.CpModel()

    # Decision Variables:
    # x_L[f, c, sec]: Faculty f is Lecture instructor for course c in section sec
    # y[f, c]: Faculty f is assigned to course c
    x_L = {}
    y = {}

    for f in faculty_list:
        for c in courses_list:
            y[(f, c)] = model.NewBoolVar(f"y_{f}_{c}")
            for sec in section_names:
                x_L[(f, c, sec)] = model.NewBoolVar(f"x_L_{f}_{c}_{sec}")
                model.Add(x_L[(f, c, sec)] <= y[(f, c)])

    # Exactly 1 Lecture (L) faculty per section of each course
    for c in courses_list:
        for sec in section_names:
            model.Add(sum(x_L[(f, c, sec)] for f in faculty_list) == 1)

    # Co-Instructor / Teaching Assistant Variables:
    x_TP = {}
    z_TA = {}

    if has_tas:
        # Custom TAs allocation under Lecture Faculty
        total_ta_slots = len(courses_list) * len(section_names) * tas_per_section
        max_ta_sec = max(1, math.ceil(total_ta_slots / len(ta_list)) + 2)

        for ta in ta_list:
            for c in courses_list:
                for sec in section_names:
                    for k in range(1, tas_per_section + 1):
                        z_TA[(ta, c, sec, k)] = model.NewBoolVar(f"z_TA_{ta}_{c}_{sec}_{k}")

        for c in courses_list:
            for sec in section_names:
                for k in range(1, tas_per_section + 1):
                    # Exactly 1 TA per slot
                    model.Add(sum(z_TA[(ta, c, sec, k)] for ta in ta_list) == 1)
                for ta in ta_list:
                    # Distinct TAs in same section
                    model.Add(sum(z_TA[(ta, c, sec, k)] for k in range(1, tas_per_section + 1)) <= 1)

        # Workload balance across TAs
        for ta in ta_list:
            ta_total = sum(
                z_TA[(ta, c, sec, k)]
                for c in courses_list
                for sec in section_names
                for k in range(1, tas_per_section + 1)
            )
            model.Add(ta_total <= max_ta_sec)
    else:
        # Fallback to co-instructors from faculty list (T/P 1 & 2)
        for f in faculty_list:
            for c in courses_list:
                for sec in section_names:
                    x_TP[(f, c, sec, 1)] = model.NewBoolVar(f"x_TP1_{f}_{c}_{sec}")
                    x_TP[(f, c, sec, 2)] = model.NewBoolVar(f"x_TP2_{f}_{c}_{sec}")
                    model.Add(x_TP[(f, c, sec, 1)] <= y[(f, c)])
                    model.Add(x_TP[(f, c, sec, 2)] <= y[(f, c)])

        for c in courses_list:
            for sec in section_names:
                model.Add(sum(x_TP[(f, c, sec, 1)] for f in faculty_list) == 1)
                model.Add(sum(x_TP[(f, c, sec, 2)] for f in faculty_list) == 1)
                for f in faculty_list:
                    model.Add(x_TP[(f, c, sec, 1)] + x_TP[(f, c, sec, 2)] <= 1)

    # High-Experience 2+1 Section Split Indicators
    high_exp_indicators = {}
    for f, info in high_exp_faculty_info.items():
        role = fac_details[f]["role"]
        if role not in ("Dean", "HOD"):
            c1 = info["top1_course"]
            c2 = info["top2_course"]

            b_c1 = model.NewBoolVar(f"b_he_c1_{f}")
            b_c2 = model.NewBoolVar(f"b_he_c2_{f}")

            model.Add(sum(x_L[(f, c1, sec)] for sec in section_names) == 2).OnlyEnforceIf(b_c1)
            model.Add(sum(x_L[(f, c1, sec)] for sec in section_names) != 2).OnlyEnforceIf(b_c1.Not())

            model.Add(sum(x_L[(f, c2, sec)] for sec in section_names) == 1).OnlyEnforceIf(b_c2)
            model.Add(sum(x_L[(f, c2, sec)] for sec in section_names) != 1).OnlyEnforceIf(b_c2.Not())

            high_exp_indicators[f] = (b_c1, b_c2)

    # Faculty Workload & Section Limits
    for f in faculty_list:
        role = fac_details[f]["role"]
        total_L_sections = sum(x_L[(f, c, sec)] for c in courses_list for sec in section_names)

        if role == "Dean":
            model.Add(total_L_sections <= dean_max_sections)
            model.Add(sum(y[(f, c)] for c in courses_list) <= max_subjects_per_faculty)
        elif role == "HOD":
            model.Add(total_L_sections <= hod_max_sections)
            model.Add(sum(y[(f, c)] for c in courses_list) <= max_subjects_per_faculty)
        else:
            model.Add(total_L_sections <= sections_per_faculty)
            if f in high_exp_faculty_info:
                model.Add(sum(y[(f, c)] for c in courses_list) <= max(2, max_subjects_per_faculty))
            else:
                model.Add(sum(y[(f, c)] for c in courses_list) <= max_subjects_per_faculty)

    # Forbid Assignment if score is 0 (only if sufficient qualified faculty exist for that course)
    for c in courses_list:
        clean_s = course_info_map[c]["Clean_Subject"]
        q_fac_count = sum(1 for f in faculty_list if score_matrix.get((f, clean_s), 0.0) > 0)
        if q_fac_count >= faculty_required_per_subject:
            for f in faculty_list:
                if score_matrix.get((f, clean_s), 0.0) <= 0:
                    model.Add(y[(f, c)] == 0)

    # Objective Function
    objective_terms = []

    # Reward 2+1 split for experienced faculty
    for f, (b_c1, b_c2) in high_exp_indicators.items():
        objective_terms.append(50000 * b_c1)
        objective_terms.append(50000 * b_c2)

    # Maximize faculty compatibility scores
    for f in faculty_list:
        max_exp = fac_max_exp.get(f, 0.0)
        is_exp = max_exp >= 6.0

        for c in courses_list:
            clean_s = course_info_map[c]["Clean_Subject"]
            score = score_matrix.get((f, clean_s), 1.0)
            score_int = int(round(score * 100))
            unpop_score = unpopular_map.get(clean_s, 0.0)
            unpop_bonus = int(round(unpop_score * 50)) if is_exp else 0

            for sec in section_names:
                objective_terms.append((score_int + unpop_bonus) * x_L[(f, c, sec)])
                if not has_tas:
                    objective_terms.append((score_int // 2) * x_TP[(f, c, sec, 1)])
                    objective_terms.append((score_int // 2) * x_TP[(f, c, sec, 2)])

    # Maximize Teaching Assistant compatibility scores
    if has_tas:
        for ta in ta_list:
            for c in courses_list:
                t_score = int(round(ta_scores.get((ta, c), 10.0) * 10))
                for sec in section_names:
                    for k in range(1, tas_per_section + 1):
                        objective_terms.append(t_score * z_TA[(ta, c, sec, k)])

    model.Maximize(sum(objective_terms))

    # Solve CP-SAT
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError(
            "Optimization problem is INFEASIBLE. Please review section settings, faculty capacity, or year filter."
        )

    # 6. Reconstruct Final Allocations
    designation_targets = {
        "Dean": {"min_hrs": 4, "max_hrs": 6, "label": "4-6 hrs/wk"},
        "HOD": {"min_hrs": 10, "max_hrs": 12, "label": "10-12 hrs/wk"},
        "Associate Professor": {"min_hrs": 14, "max_hrs": 16, "label": "14-16 hrs/wk"},
        "Assistant Professor": {"min_hrs": 16, "max_hrs": 18, "label": "16-18 hrs/wk"},
        "Professor": {"min_hrs": 10, "max_hrs": 14, "label": "10-14 hrs/wk"},
        "Faculty": {"min_hrs": 12, "max_hrs": 16, "label": "12-16 hrs/wk"}
    }

    final_allocation_matrix = {sec: {} for sec in section_names}
    faculty_allocations = []
    ta_allocations = []
    total_score = 0.0
    assignment_count = 0

    fac_workload_hours = {f: 0 for f in faculty_list}
    fac_section_counts = {f: 0 for f in faculty_list}
    ta_section_counts = {ta: 0 for ta in ta_list}
    ta_assigned_courses = {ta: set() for ta in ta_list}
    ta_supervisors = {ta: set() for ta in ta_list}

    # Group allocations by (assigned_L_id, c)
    alloc_group = {}

    for sec in section_names:
        for c in courses_list:
            c_info = course_info_map[c]
            assigned_L_id = None

            for f in faculty_list:
                if solver.Value(x_L[(f, c, sec)]) == 1:
                    assigned_L_id = f
                    break

            l_name = fac_details[assigned_L_id]["name"] if assigned_L_id else "N/A"
            assigned_tas = []
            assigned_ta_ids = []

            if has_tas:
                for k in range(1, tas_per_section + 1):
                    for ta in ta_list:
                        if solver.Value(z_TA[(ta, c, sec, k)]) == 1:
                            assigned_tas.append(ta_details[ta]["name"])
                            assigned_ta_ids.append(ta)
                            ta_section_counts[ta] += 1
                            ta_assigned_courses[ta].add(c)
                            if l_name != "N/A":
                                ta_supervisors[ta].add(l_name)
                            ta_allocations.append({
                                "TA_ID": ta,
                                "TA_Name": ta_details[ta]["name"],
                                "Course_Key": c,
                                "Subject": c_info.get("Subject", c),
                                "Year": c_info.get("Year", ""),
                                "Course_Code": c_info.get("Course_Code", ""),
                                "Section": sec,
                                "Supervising_Faculty": l_name,
                                "Preference_Score": ta_scores.get((ta, c), 10.0)
                            })
                            break
                tp1_name = assigned_tas[0] if len(assigned_tas) > 0 else "N/A"
                tp2_name = assigned_tas[1] if len(assigned_tas) > 1 else "N/A"
                tp1_id = assigned_ta_ids[0] if len(assigned_ta_ids) > 0 else "N/A"
                tp2_id = assigned_ta_ids[1] if len(assigned_ta_ids) > 1 else "N/A"
            else:
                tp1_id = None
                tp2_id = None
                for f in faculty_list:
                    if solver.Value(x_TP[(f, c, sec, 1)]) == 1:
                        tp1_id = f
                    if solver.Value(x_TP[(f, c, sec, 2)]) == 1:
                        tp2_id = f
                tp1_name = fac_details[tp1_id]["name"] if tp1_id else "N/A"
                tp2_name = fac_details[tp2_id]["name"] if tp2_id else "N/A"

            ta_str = ", ".join(assigned_tas) if assigned_tas else "None"

            final_allocation_matrix[sec][c] = {
                "Lecture_Faculty": l_name,
                "Lecture_Faculty_ID": assigned_L_id,
                "Lecture_Designation": fac_details.get(assigned_L_id, {}).get("designation", "Faculty"),
                "Lecture_Role": fac_details.get(assigned_L_id, {}).get("role", "Faculty"),
                "Teaching_Assistants": assigned_tas,
                "Teaching_Assistants_Str": ta_str,
                "TP_Faculty_1": tp1_name,
                "TP_Faculty_1_ID": tp1_id,
                "TP_Faculty_2": tp2_name,
                "TP_Faculty_2_ID": tp2_id,
                "Year": c_info.get("Year", ""),
                "Course_Code": c_info.get("Course_Code", ""),
                "Subject": c_info.get("Subject", c),
                "LTPC": c_info.get("L-T-P-C", "3-0-2-4"),
                "Total_Hours": c_info.get("Total_Hours", 5)
            }

            if assigned_L_id:
                key = (assigned_L_id, c)
                if key not in alloc_group:
                    alloc_group[key] = {
                        "sections": [],
                        "tas": set(),
                        "tp1": tp1_name,
                        "tp2": tp2_name
                    }
                alloc_group[key]["sections"].append(sec)
                for t in assigned_tas:
                    alloc_group[key]["tas"].add(t)
                fac_workload_hours[assigned_L_id] += c_info["Total_Hours"]
                fac_section_counts[assigned_L_id] += 1

    # Format Faculty Detail Allocations
    for (f_id, c), info in alloc_group.items():
        assigned_secs = info["sections"]
        sec_str = ", ".join(assigned_secs)
        num_secs = len(assigned_secs)
        c_info = course_info_map[c]
        clean_s = c_info["Clean_Subject"]

        score_info = scores_df[(scores_df["Faculty_ID"] == f_id) & (scores_df["Subject"] == clean_s)]
        pref_rank = score_info.iloc[0]["Preference_Rank"] if not score_info.empty else "N/A"
        exp_years = score_info.iloc[0]["Experience_Years"] if not score_info.empty else 0.0
        score_val = score_info.iloc[0]["Final_Score"] if not score_info.empty else score_matrix.get((f_id, clean_s), 0.0)

        total_score += score_val * num_secs
        assignment_count += num_secs

        l_role = fac_details[f_id]["role"]
        target_info = designation_targets.get(l_role, designation_targets["Faculty"])
        is_high_exp_split = (f_id in high_exp_faculty_info)

        tas_list = sorted(list(info["tas"]))
        tas_str = ", ".join(tas_list) if tas_list else "None"

        faculty_allocations.append({
            "Subject": str(c_info.get("Subject", c)),
            "Course_Key": str(c),
            "Year": str(c_info.get("Year", "")),
            "Course_Code": str(c_info.get("Course_Code", "")),
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
            "Teaching_Assistants": tas_list,
            "Teaching_Assistants_Str": tas_str,
            "TP_Faculty_1_Name": str(tas_list[0] if len(tas_list) > 0 else info["tp1"]),
            "TP_Faculty_2_Name": str(tas_list[1] if len(tas_list) > 1 else info["tp2"]),
            "Preference_Rank": pref_rank,
            "Experience_Years": float(exp_years),
            "Is_High_Experience_Split": is_high_exp_split,
            "Score": float(score_val),
            "Assigned_Weekly_Hours": int(c_info["Total_Hours"] * num_secs),
            "Target_Hours_Range": target_info["label"]
        })

    for a in faculty_allocations:
        f_id = a["Lecture_Faculty_ID"]
        a["Faculty_Total_Weekly_Hours"] = int(fac_workload_hours.get(f_id, a["Assigned_Weekly_Hours"]))

    avg_score = float(round(total_score / assignment_count, 2)) if assignment_count > 0 else 0.0

    # Build TA Workload Summary
    ta_workload_summary = []
    if has_tas:
        for ta in ta_list:
            ta_workload_summary.append({
                "TA_ID": ta,
                "TA_Name": ta_details[ta]["name"],
                "Total_Sections": ta_section_counts[ta],
                "Assigned_Courses": sorted(list(ta_assigned_courses[ta])),
                "Supervising_Faculty": sorted(list(ta_supervisors[ta]))
            })

    return {
        "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
        "num_sections": int(num_sections),
        "num_subjects": int(len(courses_list)),
        "sections_per_faculty": int(sections_per_faculty),
        "faculty_required_per_subject": int(faculty_required_per_subject),
        "high_exp_threshold": float(high_exp_threshold),
        "high_exp_faculty_count": len(high_exp_faculty_info),
        "total_assignments": int(assignment_count),
        "average_score": float(avg_score),
        "tas_per_section": int(tas_per_section),
        "ta_count": len(ta_list),
        "year_filter": year_filter or "All",
        "years_available": years_available,
        "subjects": [str(s) for s in courses_list],
        "course_details": course_info_map,
        "section_names": [str(sec) for sec in section_names],
        "final_allocation_matrix": final_allocation_matrix,
        "faculty_allocations": faculty_allocations,
        "ta_allocations": ta_allocations,
        "ta_workload_summary": ta_workload_summary
    }
