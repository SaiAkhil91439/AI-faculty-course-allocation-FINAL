from typing import List, Dict, Any, Optional
import pandas as pd

DEFAULT_PROMPT_COURSES = [
    {
        "course_title": "Advanced Linear Algebra and Optimization",
        "l": 2, "t": 2, "p": 2, "c": 4, "ltpc": "2-2-2-4"
    },
    {
        "course_title": "Full Stack AI Application Development",
        "l": 0, "t": 2, "p": 2, "c": 3, "ltpc": "0-2-2-3"
    },
    {
        "course_title": "Open Elective - 1",
        "l": 2, "t": 2, "p": 0, "c": 3, "ltpc": "2-2-0-3"
    },
    {
        "course_title": "Algorithm Design and Analysis",
        "l": 2, "t": 2, "p": 2, "c": 4, "ltpc": "2-2-2-4"
    },
    {
        "course_title": "Machine Learning",
        "l": 3, "t": 0, "p": 2, "c": 4, "ltpc": "3-0-2-4"
    },
    {
        "course_title": "Operating Systems",
        "l": 2, "t": 0, "p": 2, "c": 3, "ltpc": "2-0-2-3"
    },
    {
        "course_title": "Digital Logic and Computer Organization",
        "l": 2, "t": 0, "p": 2, "c": 3, "ltpc": "2-0-2-3"
    }
]

def get_section_label(index: int) -> str:
    """Generates standard letter section names: A, B, C... Z, AA, AB..."""
    label = ""
    while index >= 0:
        label = chr(65 + (index % 26)) + label
        index = (index // 26) - 1
    return label

def calculate_ltpc_workload(
    courses: Optional[List[Dict[str, Any]]] = None,
    num_sections: int = 12,
    l_faculty_multiplier: int = 1,
    t_faculty_multiplier: int = 3,
    p_faculty_multiplier: int = 3,
    avg_faculty_capacity_hours: float = 15.0,
    num_available_faculty: int = 34
) -> Dict[str, Any]:
    """
    Calculates faculty workload based on LTPC structure according to institutional formulas:
    
    1 section workload:
    (Total L hours * L faculty) + (Total T hours * T faculty) + (Total P hours * P faculty)
    e.g.: 13*1 + 8*3 + 12*3 = 73 hours
    
    Department workload for N sections:
    (Total L hours * L faculty * N) + (Total T hours * T faculty * N) + (Total P hours * P faculty * N)
    e.g.: 13*1*12 + 8*3*12 + 12*3*12 = 156 + 288 + 432 = 876 hours
    
    Includes comprehensive Workload Efficiency and Capacity Optimization metrics.
    """
    if not courses:
        courses = [dict(c) for c in DEFAULT_PROMPT_COURSES]

    num_sections = max(1, int(num_sections))
    l_faculty_multiplier = max(1, int(l_faculty_multiplier))
    t_faculty_multiplier = max(1, int(t_faculty_multiplier))
    p_faculty_multiplier = max(1, int(p_faculty_multiplier))
    num_available_faculty = max(1, int(num_available_faculty or 34))

    courses_processed = []
    total_l = 0
    total_t = 0
    total_p = 0
    total_c = 0

    for idx, c in enumerate(courses, 1):
        title = str(c.get("course_title") or c.get("Course") or c.get("Subject") or c.get("Courses") or f"Course {idx}").strip()
        l = int(c.get("l") if c.get("l") is not None else c.get("L", 0))
        t = int(c.get("t") if c.get("t") is not None else c.get("T", 0))
        p = int(c.get("p") if c.get("p") is not None else c.get("P", 0))
        credits = int(c.get("c") if c.get("c") is not None else c.get("C", 0))

        ltpc_str = c.get("ltpc") or c.get("L-T-P-C") or f"{l}-{t}-{p}-{credits}"

        sec_l_load = l * l_faculty_multiplier
        sec_t_load = t * t_faculty_multiplier
        sec_p_load = p * p_faculty_multiplier
        sec_total = sec_l_load + sec_t_load + sec_p_load

        dept_l_load = sec_l_load * num_sections
        dept_t_load = sec_t_load * num_sections
        dept_p_load = sec_p_load * num_sections
        dept_total = sec_total * num_sections

        total_l += l
        total_t += t
        total_p += p
        total_c += credits

        courses_processed.append({
            "sl_no": idx,
            "course_title": title,
            "l": l,
            "t": t,
            "p": p,
            "c": credits,
            "ltpc": ltpc_str,
            "contact_hours": l + t + p,
            "l_faculty": l_faculty_multiplier,
            "t_faculty": t_faculty_multiplier,
            "p_faculty": p_faculty_multiplier,
            "sec_l_load": sec_l_load,
            "sec_t_load": sec_t_load,
            "sec_p_load": sec_p_load,
            "sec_total_workload": sec_total,
            "dept_l_load": dept_l_load,
            "dept_t_load": dept_t_load,
            "dept_p_load": dept_p_load,
            "dept_total_workload": dept_total
        })

    # Summary calculations
    section_l_load = total_l * l_faculty_multiplier
    section_t_load = total_t * t_faculty_multiplier
    section_p_load = total_p * p_faculty_multiplier
    section_total_workload = section_l_load + section_t_load + section_p_load

    dept_l_load = section_l_load * num_sections
    dept_t_load = section_t_load * num_sections
    dept_p_load = section_p_load * num_sections
    dept_total_workload = section_total_workload * num_sections

    # Calculate percent shares of department workload
    for c in courses_processed:
        c["dept_share_pct"] = round((c["dept_total_workload"] / dept_total_workload * 100), 1) if dept_total_workload > 0 else 0.0

    # Share of L, T, P in department workload
    l_share_pct = round((dept_l_load / dept_total_workload * 100), 1) if dept_total_workload > 0 else 0.0
    t_share_pct = round((dept_t_load / dept_total_workload * 100), 1) if dept_total_workload > 0 else 0.0
    p_share_pct = round((dept_p_load / dept_total_workload * 100), 1) if dept_total_workload > 0 else 0.0

    # Section-by-section breakdown list
    sections_breakdown = []
    cumulative = 0
    for s_idx in range(num_sections):
        sec_name = f"Section {get_section_label(s_idx)}"
        cumulative += section_total_workload
        sections_breakdown.append({
            "section_name": sec_name,
            "num_courses": len(courses_processed),
            "l_hours": section_l_load,
            "t_hours": section_t_load,
            "p_hours": section_p_load,
            "section_total_workload": section_total_workload,
            "cumulative_dept_workload": cumulative
        })

    # Formula breakdown representations
    formula_section_expr = (
        f"{total_l}*{l_faculty_multiplier}(L hours *{l_faculty_multiplier} faculty) + "
        f"{total_t}*{t_faculty_multiplier}(T hours *{t_faculty_multiplier} faculty) + "
        f"{total_p}*{p_faculty_multiplier}(P hours *{p_faculty_multiplier} faculty) = {section_total_workload} hours"
    )

    formula_dept_expr = (
        f"{total_l}*{l_faculty_multiplier}*{num_sections}(L hours *{l_faculty_multiplier} faculty*{num_sections} sections) + "
        f"{total_t}*{t_faculty_multiplier}*{num_sections}(T hours *{t_faculty_multiplier} faculty*{num_sections} sections) + "
        f"{total_p}*{p_faculty_multiplier}*{num_sections}(P hours *{p_faculty_multiplier} faculty*{num_sections} sections) = {dept_total_workload} hours"
    )

    # Faculty requirement estimate (assuming standard ~15 teaching hours per faculty per week)
    cap = max(1.0, float(avg_faculty_capacity_hours))
    est_total_faculty = round(dept_total_workload / cap, 1)
    est_l_faculty = round(dept_l_load / cap, 1)
    est_t_faculty = round(dept_t_load / cap, 1)
    est_p_faculty = round(dept_p_load / cap, 1)

    # Workload Efficiency & Capacity Optimization Metrics
    available_capacity_hours = round(num_available_faculty * cap, 1)
    capacity_utilization_pct = round((dept_total_workload / available_capacity_hours) * 100, 1) if available_capacity_hours > 0 else 0.0

    # Workload Efficiency Score (100% is perfectly balanced; deductions for extreme overload or severe underutilization)
    if capacity_utilization_pct <= 100:
        eff_score = max(30.0, 100.0 - (100.0 - capacity_utilization_pct) * 0.35)
    else:
        eff_score = max(25.0, 100.0 - (capacity_utilization_pct - 100.0) * 0.40)
    workload_efficiency_score = round(eff_score, 1)

    if capacity_utilization_pct <= 80:
        efficiency_status = "Underutilized (Surplus Faculty)"
        efficiency_status_badge = "info"
    elif capacity_utilization_pct <= 105:
        efficiency_status = "Optimal Workload Balance"
        efficiency_status_badge = "success"
    elif capacity_utilization_pct <= 130:
        efficiency_status = "High Contact Demand"
        efficiency_status_badge = "warning"
    else:
        efficiency_status = "Critical Overload (Faculty Deficit)"
        efficiency_status_badge = "danger"

    faculty_deficit = max(0.0, round(est_total_faculty - num_available_faculty, 1))
    faculty_surplus = max(0.0, round(num_available_faculty - est_total_faculty, 1))

    # Contact hours distribution efficiency (Theory vs Practical/Tutorial)
    contact_ratio = round(total_l / max(1, (total_t + total_p)), 2)

    # Comparative Staffing Efficiency Models (Scenarios)
    scenario_defs = [
        {
            "name": "Institutional Model (1-3-3)",
            "code": "1-3-3",
            "desc": "Baseline institutional standard: 1 L, 3 T, 3 P faculty per section",
            "l_fac": 1, "t_fac": 3, "p_fac": 3
        },
        {
            "name": "Dual-Batch Optimized (1-2-2)",
            "code": "1-2-2",
            "desc": "Dual-batch lab & tutorial coverage: 1 L, 2 T, 2 P faculty per section",
            "l_fac": 1, "t_fac": 2, "p_fac": 2
        },
        {
            "name": "Blended Core (1-1-2)",
            "code": "1-1-2",
            "desc": "Combined tutorial + dual-batch lab: 1 L, 1 T, 2 P faculty per section",
            "l_fac": 1, "t_fac": 1, "p_fac": 2
        },
        {
            "name": "Compact AICTE Norm (1-1-1)",
            "code": "1-1-1",
            "desc": "Single faculty AICTE norm baseline: 1 L, 1 T, 1 P faculty per section",
            "l_fac": 1, "t_fac": 1, "p_fac": 1
        }
    ]

    scenarios = []
    for sc in scenario_defs:
        s_sec = (total_l * sc["l_fac"]) + (total_t * sc["t_fac"]) + (total_p * sc["p_fac"])
        s_dept = s_sec * num_sections
        s_fac = round(s_dept / cap, 1)
        s_saved = max(0, dept_total_workload - s_dept)
        s_saved_pct = round((s_saved / dept_total_workload * 100), 1) if dept_total_workload > 0 else 0.0
        s_util = round((s_dept / available_capacity_hours) * 100, 1) if available_capacity_hours > 0 else 0.0
        is_active = (sc["l_fac"] == l_faculty_multiplier and sc["t_fac"] == t_faculty_multiplier and sc["p_fac"] == p_faculty_multiplier)

        scenarios.append({
            "name": sc["name"],
            "code": sc["code"],
            "description": sc["desc"],
            "l_faculty": sc["l_fac"],
            "t_faculty": sc["t_fac"],
            "p_faculty": sc["p_fac"],
            "section_workload": s_sec,
            "dept_workload": s_dept,
            "faculty_required": s_fac,
            "hours_saved": s_saved,
            "savings_percent": s_saved_pct,
            "capacity_utilization": s_util,
            "is_active": is_active
        })

    # Designation-based workload distribution recommendation
    prof_count = max(1, round(est_total_faculty * 0.15))
    assoc_count = max(2, round(est_total_faculty * 0.25))
    asst_count = max(3, round(est_total_faculty - prof_count - assoc_count))
    designation_mix = [
        {"designation": "Professor", "weekly_target_load": 12, "recommended_count": prof_count, "capacity_hours": prof_count * 12},
        {"designation": "Associate Professor", "weekly_target_load": 14, "recommended_count": assoc_count, "capacity_hours": assoc_count * 14},
        {"designation": "Assistant Professor", "weekly_target_load": 16, "recommended_count": asst_count, "capacity_hours": asst_count * 16}
    ]

    return {
        "num_sections": num_sections,
        "l_faculty_multiplier": l_faculty_multiplier,
        "t_faculty_multiplier": t_faculty_multiplier,
        "p_faculty_multiplier": p_faculty_multiplier,
        "total_courses": len(courses_processed),
        "total_l_hours": total_l,
        "total_t_hours": total_t,
        "total_p_hours": total_p,
        "total_credits": total_c,
        "total_contact_hours": total_l + total_t + total_p,
        "section_l_load": section_l_load,
        "section_t_load": section_t_load,
        "section_p_load": section_p_load,
        "section_total_workload": section_total_workload,
        "dept_l_load": dept_l_load,
        "dept_t_load": dept_t_load,
        "dept_p_load": dept_p_load,
        "dept_total_workload": dept_total_workload,
        "l_share_pct": l_share_pct,
        "t_share_pct": t_share_pct,
        "p_share_pct": p_share_pct,
        "formula_section": formula_section_expr,
        "formula_dept": formula_dept_expr,
        "estimated_faculty_required": est_total_faculty,
        "estimated_l_faculty": est_l_faculty,
        "estimated_t_faculty": est_t_faculty,
        "estimated_p_faculty": est_p_faculty,
        "avg_faculty_capacity_hours": cap,
        "num_available_faculty": num_available_faculty,
        "available_capacity_hours": available_capacity_hours,
        "capacity_utilization_pct": capacity_utilization_pct,
        "workload_efficiency_score": workload_efficiency_score,
        "efficiency_status": efficiency_status,
        "efficiency_status_badge": efficiency_status_badge,
        "faculty_deficit": faculty_deficit,
        "faculty_surplus": faculty_surplus,
        "theory_to_practical_ratio": contact_ratio,
        "efficiency_scenarios": scenarios,
        "designation_mix": designation_mix,
        "courses": courses_processed,
        "sections": sections_breakdown
    }

def convert_course_df_to_workload_input(course_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Converts a loaded course_df from read_course_details into workload input list."""
    if course_df is None or course_df.empty:
        return [dict(c) for c in DEFAULT_PROMPT_COURSES]

    out = []
    for _, row in course_df.iterrows():
        out.append({
            "course_title": str(row.get("Subject") or row.get("Course") or row.get("Courses") or "Course").strip(),
            "l": int(row.get("L", 0)),
            "t": int(row.get("T", 0)),
            "p": int(row.get("P", 0)),
            "c": int(row.get("C", 0)),
            "ltpc": str(row.get("L-T-P-C", ""))
        })
    return out
