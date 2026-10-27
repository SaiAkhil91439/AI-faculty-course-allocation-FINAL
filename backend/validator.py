from typing import Dict, Any, List, Tuple
import pandas as pd

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
    high_exp_threshold: float = 8.0
) -> Dict[str, Any]:
    """
    Validates user configurations, roles (Dean/HOD), course L-T-P-C data, and loaded DataFrames.
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

    # Count high-experience faculty (max teaching experience in any course >= high_exp_threshold)
    high_exp_count = 0
    if not exp_df.empty and "Experience_Years" in exp_df.columns:
        fac_max_exps = exp_df.groupby("Faculty_ID")["Experience_Years"].max()
        high_exp_count = int((fac_max_exps >= high_exp_threshold).sum())

    # 5. Extract available subjects
    exp_subjects = set(exp_df["Subject"].dropna().unique())
    pref_cols = [c for c in pref_df.columns if c.startswith("Preference_")]
    pref_subjects = set()
    for col in pref_cols:
        pref_subjects.update(pref_df[col].dropna().unique())
    
    all_known_subjects = sorted(list(exp_subjects.union(pref_subjects)))

    if len(all_known_subjects) < num_subjects:
        errors.append(
            f"Configured number of subjects ({num_subjects}) exceeds total unique subjects found in files ({len(all_known_subjects)}: {', '.join(all_known_subjects)})."
        )

    # 6. Check qualified faculty count per subject
    subject_faculty_counts = {}
    for subj in exp_subjects:
        subj_exp = exp_df[exp_df["Subject"] == subj]
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
    if course_df is not None and not course_df.empty:
        courses_loaded = len(course_df)

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
        "subject_faculty_counts": subject_faculty_counts
    }

