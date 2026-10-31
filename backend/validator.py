from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
from backend.excel_reader import clean_subject_name

class AllocationValidationError(Exception):
    def __init__(self, message: str, details: List[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details or []

def validate_inputs(
    pref_df: pd.DataFrame,
    exp_df: pd.DataFrame,
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
    Validates user configurations, roles (Dean/HOD), multi-year course L-T-P-C data,
    Teaching Assistants (TA) settings, and loaded DataFrames.
    """
    errors = []

    # 1. Section Division Check
    if sections_per_faculty <= 0:
        errors.append("Sections per Faculty must be greater than 0.")
    elif num_sections % sections_per_faculty != 0:
        errors.append(
            f"Number of sections ({num_sections}) must be cleanly divisible by Sections per Faculty ({sections_per_faculty}). "
            f"Remainder: {num_sections % sections_per_faculty}."
        )

    faculty_required_per_subject = num_sections // sections_per_faculty if sections_per_faculty > 0 else 0

    if num_sections <= 0:
        errors.append("Number of sections must be greater than 0.")
    if num_subjects <= 0:
        errors.append("Number of subjects must be greater than 0.")
    if max_subjects_per_faculty <= 0:
        errors.append("Maximum subjects per faculty must be at least 1.")
    if dean_max_sections <= 0:
        errors.append("Dean max sections must be at least 1.")
    if hod_max_sections <= 0:
        errors.append("HOD max sections must be at least 1.")
    if tas_per_section < 0:
        errors.append("Teaching Assistants per section cannot be negative.")

    # 2. Check Preferences DataFrame
    if pref_df.empty:
        errors.append("Faculty Preferences file is empty or contains no valid rows.")
    
    dup_ids = pref_df[pref_df.duplicated(subset=["Faculty_ID"], keep=False)]["Faculty_ID"].unique().tolist()
    if dup_ids:
        errors.append(f"Duplicate Faculty_ID(s) found in Preferences file: {', '.join(dup_ids)}")

    # 3. Check Experience DataFrame
    if exp_df.empty:
        errors.append("Faculty Experience file is empty or contains no valid rows.")

    # 4. Extract Roles & Count Deans/HODs/High-Experience Faculty
    pref_faculty = set(pref_df["Faculty_ID"].dropna().unique())

    deans_count = int((pref_df["Role"] == "Dean").sum()) if "Role" in pref_df.columns else 0
    hods_count = int((pref_df["Role"] == "HOD").sum()) if "Role" in pref_df.columns else 0

    high_exp_count = 0
    if not exp_df.empty and "Experience_Years" in exp_df.columns:
        fac_max_exps = exp_df.groupby("Faculty_ID")["Experience_Years"].max()
        high_exp_count = int((fac_max_exps >= high_exp_threshold).sum())

    # 5. Extract available subjects & Multi-Year Courses
    years_available = []
    if course_df is not None and not course_df.empty and "Year" in course_df.columns:
        years_available = [y for y in course_df["Year"].dropna().unique() if str(y).strip() != ""]

    target_course_df = course_df
    if year_filter and year_filter not in ("All", "all", "", None) and target_course_df is not None and not target_course_df.empty:
        filtered = target_course_df[target_course_df["Year"] == year_filter]
        if not filtered.empty:
            target_course_df = filtered

    exp_subjects = set(exp_df["Subject"].dropna().apply(clean_subject_name).unique())
    pref_cols = [c for c in pref_df.columns if c.startswith("Preference_")]
    pref_subjects = set()
    for col in pref_cols:
        for val in pref_df[col].dropna():
            pref_subjects.add(clean_subject_name(val))
    
    all_known_subjects = sorted(list(exp_subjects.union(pref_subjects)))

    if len(all_known_subjects) < num_subjects:
        errors.append(
            f"Configured number of subjects ({num_subjects}) exceeds total unique subjects found in files ({len(all_known_subjects)}: {', '.join(all_known_subjects)})."
        )

    # 6. Check qualified faculty count per subject
    subject_faculty_counts = {}
    exp_copy = exp_df.copy()
    exp_copy["Clean_Subj"] = exp_copy["Subject"].apply(clean_subject_name)

    for subj in exp_subjects:
        subj_exp = exp_copy[exp_copy["Clean_Subj"] == subj]
        qualified_fac = subj_exp["Faculty_ID"].nunique()
        subject_faculty_counts[subj] = qualified_fac

    sorted_subjects = sorted(list(exp_subjects), key=lambda s: subject_faculty_counts[s], reverse=True)
    active_subjects = sorted_subjects[:num_subjects]

    insufficient_faculty_subjects = []
    for subj in active_subjects:
        qualified_fac = subject_faculty_counts.get(subj, 0)
        if qualified_fac < faculty_required_per_subject:
            insufficient_faculty_subjects.append(
                f"Subject '{subj}' requires {faculty_required_per_subject} faculty, but only {qualified_fac} qualified faculty are listed in experience file."
            )

    if insufficient_faculty_subjects:
        errors.extend(insufficient_faculty_subjects)

    # 7. Check Course Details L-T-P-C Data
    courses_loaded = 0
    if target_course_df is not None and not target_course_df.empty:
        courses_loaded = len(target_course_df)

    # 8. Check Teaching Assistants Data
    ta_count = 0
    if ta_df is not None and not ta_df.empty:
        ta_count = len(ta_df)

    if errors:
        raise AllocationValidationError(
            message="Data Validation Failed. Please resolve the errors below before proceeding.",
            details=errors
        )

    return {
        "valid": True,
        "num_sections": num_sections,
        "num_subjects": num_subjects,
        "sections_per_faculty": sections_per_faculty,
        "max_subjects_per_faculty": max_subjects_per_faculty,
        "dean_max_sections": dean_max_sections,
        "hod_max_sections": hod_max_sections,
        "high_exp_threshold": high_exp_threshold,
        "high_exp_count": high_exp_count,
        "faculty_required_per_subject": faculty_required_per_subject,
        "total_faculty_count": len(pref_faculty),
        "deans_count": deans_count,
        "hods_count": hods_count,
        "courses_loaded": courses_loaded,
        "available_subjects": active_subjects,
        "subject_faculty_counts": subject_faculty_counts,
        "tas_per_section": tas_per_section,
        "ta_count": ta_count,
        "years_available": years_available,
        "year_filter": year_filter or "All"
    }
