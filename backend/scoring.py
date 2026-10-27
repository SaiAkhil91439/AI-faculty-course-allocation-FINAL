from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

DEFAULT_WEIGHTS = {
    "preference": 0.50,
    "experience": 0.30,
    "skill": 0.10,
    "qualification": 0.10
}

# Strict preference rank hierarchy (1st preference >> 2nd >> 3rd...)
PREFERENCE_SCORES = {
    1: 100.0,
    2: 60.0,
    3: 40.0,
    4: 20.0,
    5: 10.0
}

SKILL_SCORES = {
    "beginner": 25.0,
    "intermediate": 50.0,
    "advanced": 75.0,
    "expert": 100.0
}

def normalize_subject_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(str(name).replace('–', '-').replace('—', '-').replace('−', '-').split()).lower()

def get_preference_score(faculty_row: pd.Series, subject: str) -> Tuple[float, Optional[int]]:
    """Returns (score, preference_rank)."""
    norm_subject = normalize_subject_name(subject)
    for rank in range(1, 6):
        pref_col = f"Preference_{rank}"
        if pref_col in faculty_row and faculty_row[pref_col] is not None:
            if normalize_subject_name(str(faculty_row[pref_col])) == norm_subject:
                return PREFERENCE_SCORES[rank], rank
    return 0.0, None

def get_skill_score(skill_level: Optional[str]) -> float:
    if not skill_level:
        return 25.0
    normalized = str(skill_level).strip().lower()
    return SKILL_SCORES.get(normalized, 25.0)

def get_qualification_score(qualification: Optional[str]) -> float:
    if not qualification:
        return 40.0
    qual_lower = str(qualification).strip().lower()
    if any(keyword in qual_lower for keyword in ["phd", "ph.d", "doctorate", "post-doc"]):
        return 100.0
    elif any(keyword in qual_lower for keyword in ["m.tech", "m.e", "m.s", "master", "mtech", "ms"]):
        return 80.0
    elif any(keyword in qual_lower for keyword in ["b.tech", "b.e", "b.s", "bachelor", "btech", "bs"]):
        return 60.0
    return 40.0

def calculate_least_preferred_subjects(pref_df: pd.DataFrame) -> Dict[str, float]:
    """
    Computes an 'unpopularity index' (0 to 100) for each subject based on faculty preferences.
    Higher index = less preferred overall by faculty.
    """
    pref_counts = {} # subj -> total preference weight
    total_fac = len(pref_df)
    
    if total_fac == 0:
        return {}

    for _, row in pref_df.iterrows():
        for rank in range(1, 6):
            col = f"Preference_{rank}"
            if col in row and row[col]:
                s = str(row[col]).strip()
                # 1st pref gives 5 pts, 2nd 4 pts...
                weight = 6 - rank
                pref_counts[s] = pref_counts.get(s, 0) + weight

    max_possible = total_fac * 5.0
    unpopularity_map = {}
    for subj, total_pts in pref_counts.items():
        # Inverse score: less points = higher unpopularity
        pop_ratio = total_pts / max_possible if max_possible > 0 else 1.0
        unpop_index = round((1.0 - pop_ratio) * 100.0, 2)
        unpopularity_map[subj] = unpop_index

    return unpopularity_map

def normalize_experience_scores(exp_df: pd.DataFrame) -> Dict[Tuple[str, str], float]:
    """
    Normalizes experience years to 0-100 per subject.
    Returns mapping of (Faculty_ID, Subject) -> Normalized Experience Score (0-100).
    """
    exp_scores = {}
    if exp_df.empty:
        return exp_scores

    max_exp_per_subject = exp_df.groupby("Subject")["Experience_Years"].max().to_dict()

    for _, row in exp_df.iterrows():
        fac_id = str(row["Faculty_ID"]).strip()
        subj = str(row["Subject"]).strip()
        exp_years = float(row.get("Experience_Years", 0))

        max_exp = max_exp_per_subject.get(subj, 0)
        if max_exp > 0:
            norm_score = min(100.0, (exp_years / max_exp) * 100.0)
        else:
            norm_score = 100.0 if exp_years > 0 else 50.0

        exp_scores[(fac_id, subj)] = round(norm_score, 2)

    return exp_scores

def calculate_compatibility_scores(
    pref_df: pd.DataFrame,
    exp_df: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes compatibility score for every (Faculty_ID, Subject) pair.
    """
    w = weights if weights else DEFAULT_WEIGHTS.copy()

    total_w = sum(w.values())
    if total_w > 0:
        w = {k: v / total_w for k, v in w.items()}
    else:
        w = DEFAULT_WEIGHTS.copy()

    exp_normalized = normalize_experience_scores(exp_df)
    unpopular_map = calculate_least_preferred_subjects(pref_df)
    pref_map = {str(row["Faculty_ID"]).strip(): row for _, row in pref_df.iterrows()}

    score_records = []
    score_matrix = {} # (fac_id, subject) -> float score

    for _, exp_row in exp_df.iterrows():
        fac_id = str(exp_row["Faculty_ID"]).strip()
        subject = str(exp_row["Subject"]).strip()

        fac_pref_row = pref_map.get(fac_id)
        fac_name = fac_pref_row["Faculty_Name"] if (fac_pref_row is not None and "Faculty_Name" in fac_pref_row) else fac_id
        designation = fac_pref_row.get("Designation", "Professor") if fac_pref_row is not None else "Professor"
        role = fac_pref_row.get("Role", "Faculty") if fac_pref_row is not None else "Faculty"

        # 1. Preference score
        if fac_pref_row is not None:
            pref_score, pref_rank = get_preference_score(fac_pref_row, subject)
        else:
            pref_score, pref_rank = 0.0, None

        # 2. Experience score
        exp_score = exp_normalized.get((fac_id, subject), 0.0)
        raw_exp_years = float(exp_row.get("Experience_Years", 0))

        # 3. Skill score
        skill_str = str(exp_row.get("Skill_Level", ""))
        skill_score = get_skill_score(skill_str)

        # 4. Qualification score
        qual_str = str(exp_row.get("Qualification", ""))
        qual_score = get_qualification_score(qual_str)

        # Weighted base score
        base_score = (
            w["preference"] * pref_score +
            w["experience"] * exp_score +
            w["skill"] * skill_score +
            w["qualification"] * qual_score
        )

        final_score = round(base_score, 2)
        score_matrix[(fac_id, subject)] = final_score

        score_records.append({
            "Faculty_ID": fac_id,
            "Faculty_Name": fac_name,
            "Designation": designation,
            "Role": role,
            "Subject": subject,
            "Preference_Rank": pref_rank if pref_rank else "Unlisted",
            "Preference_Score": pref_score,
            "Experience_Years": raw_exp_years,
            "Experience_Score": exp_score,
            "Skill_Level": skill_str or "Unknown",
            "Skill_Score": skill_score,
            "Qualification": qual_str or "Unspecified",
            "Qualification_Score": qual_score,
            "Final_Score": final_score
        })

    scores_df = pd.DataFrame(score_records)

    return {
        "weights_used": w,
        "score_matrix": score_matrix,
        "scores_df": scores_df,
        "unpopular_subjects": unpopular_map
    }
