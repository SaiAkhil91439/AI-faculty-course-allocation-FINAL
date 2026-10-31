import os
import pandas as pd
from typing import Union, BinaryIO, Tuple, Optional, List, Dict, Any

CANONICAL_SUBJECT_MAP: Dict[str, str] = {
    'python': 'Python Programming Essentials',
    'python essentials': 'Python Programming Essentials',
    'python programming essentials': 'Python Programming Essentials',
    'front-end web development': 'Front-End Web Development',
    'front end web development': 'Front-End Web Development',
    'frontend web development': 'Front-End Web Development',
    'mini project - branch specific': 'Mini Project - Branch Specific',
    'mini project': 'Mini Project - Branch Specific',
    'design thinking and engineering orientation': 'Design Thinking and Engineering Orientation',
    'algorithm design and analysis': 'Algorithm Design and Analysis',
    'machine learning': 'Machine Learning',
    'machine learnings': 'Machine Learning',
    'machine learning(lab)': 'Machine Learning',
    'full stack development': 'Full Stack Development',
    'digital logic and computer organization': 'Digital Logic and Computer Organization',
    'natural language processing': 'Natural Language Processing',
    'computer networks': 'Computer Networks',
    'network': 'Computer Networks',
    'operating systems': 'Operating Systems',
    'operating system': 'Operating Systems',
    'cloud computing': 'Cloud Computing',
    'web and sequence data mining': 'Web and Sequence Data Mining',
    'big data analytics': 'Big Data Analytics',
    'generative and agentic ai': 'Generative and Agentic AI',
    'ml ops and llm ops': 'ML Ops and LLM Ops',
    'mlops and llm ops': 'ML Ops and LLM Ops',
    'reinforcement learning': 'Reinforcement Learning',
}

def clean_subject_name(name: Any) -> str:
    """Cleans, normalizes, and canonicalizes course subject names."""
    if not name or pd.isna(name):
        return ""
    cleaned = " ".join(str(name).replace('–', '-').replace('—', '-').replace('−', '-').split()).strip()
    c_lower = cleaned.lower()
    return CANONICAL_SUBJECT_MAP.get(c_lower, cleaned)

def derive_skill_level(exp_years: float) -> str:
    if exp_years >= 8:
        return "Expert"
    elif exp_years >= 5:
        return "Advanced"
    elif exp_years >= 2:
        return "Intermediate"
    else:
        return "Beginner"

def extract_role(designation: str, addl_duties: str, fac_name: str) -> str:
    """Detects role: Dean, HOD, Associate Professor, Assistant Professor, Professor, Teaching Associate."""
    combined = f"{designation} {addl_duties} {fac_name}".lower()
    if "dean" in combined:
        return "Dean"
    elif "hod" in combined or "head of" in combined or "h.o.d" in combined:
        return "HOD"
    elif "associate professor" in combined or "assoc" in combined:
        return "Associate Professor"
    elif "assistant professor" in combined or "asst. prof" in combined or "asst prof" in combined:
        return "Assistant Professor"
    elif "teaching associate" in combined or "teaching assistant" in combined or "prog." in combined or "cap" in combined or "era" in combined:
        return "Teaching Associate"
    elif "professor" in combined or "prof" in combined:
        return "Professor"
    return "Faculty"

def parse_ltpc_string(ltpc_str: str) -> Tuple[int, int, int, int]:
    """
    Parses 'L-T-P-C' format string like '3-0-2-4' or 5-part '1-2-2-1-3' (L-T-P-SL-C) into (L, T, P, C).
    """
    try:
        parts = [int(x.strip()) for x in str(ltpc_str).split("-")]
        if len(parts) >= 5:
            # Format: L - T - P - SL - C (e.g., 1-2-2-1-3 -> L=1, T=2, P=2, C=3)
            return parts[0], parts[1], parts[2], parts[4]
        elif len(parts) == 4:
            return parts[0], parts[1], parts[2], parts[3]
        elif len(parts) == 3:
            return parts[0], parts[1], parts[2], parts[0] + parts[1] + parts[2]
    except Exception:
        pass
    return 3, 0, 2, 4

def read_course_details(file_source: Union[str, BinaryIO]) -> pd.DataFrame:
    """
    Reads Course Details Excel file supporting both single-year and multi-year courses
    (e.g., I Year, II Year, III Year, M.Tech I Year), L-T-P-C and L-T-P-SL-C structures.
    Returns cleaned DataFrame with:
    ['Course_ID', 'Year', 'Course_Code', 'Subject', 'L', 'T', 'P', 'C', 'L-T-P-C', 'Total_Hours', 'Course_Key']
    """
    if hasattr(file_source, 'seek'):
        file_source.seek(0)

    records = []

    # Check if file has multiple year sheets (e.g. I Year, II Year, III Year, M.Tech)
    try:
        xl = pd.ExcelFile(file_source)
        sheet_names = xl.sheet_names
    except Exception:
        sheet_names = []

    year_sheets = [s for s in sheet_names if any(k in s.lower() for k in ["year", "m.tech", "b.tech", "sem", "term"])]

    if len(year_sheets) > 1:
        # Multi-sheet workbook where each sheet represents an academic year
        for s_name in year_sheets:
            df_sheet = pd.read_excel(xl, sheet_name=s_name)
            sub_records = _parse_course_dataframe(df_sheet, default_year=s_name)
            records.extend(sub_records)
    else:
        # Single sheet or default reading
        if sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_names[0])
        else:
            df = pd.read_excel(file_source)
        records = _parse_course_dataframe(df)

    if not records:
        # Fallback to default curriculum if empty
        default_sample = [
            {"Year": "I Year", "Course_Code": "25CS101", "Subject": "Python Programming Essentials", "L": 1, "T": 2, "P": 2, "C": 3, "L-T-P-C": "1-2-2-3", "Total_Hours": 5},
            {"Year": "I Year", "Course_Code": "25CS102", "Subject": "Front-End Web Development", "L": 0, "T": 2, "P": 2, "C": 2, "L-T-P-C": "0-2-2-2", "Total_Hours": 4},
            {"Year": "II Year", "Course_Code": "25AM205", "Subject": "Machine Learning", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
            {"Year": "II Year", "Course_Code": "25CY208", "Subject": "Algorithm Design and Analysis", "L": 2, "T": 2, "P": 2, "C": 4, "L-T-P-C": "2-2-2-4", "Total_Hours": 6},
            {"Year": "III Year", "Course_Code": "24AM301", "Subject": "Natural Language Processing", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
            {"Year": "III Year", "Course_Code": "22CY204", "Subject": "Computer Networks", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
            {"Year": "M.Tech I Year", "Course Code": "26ADB803", "Subject": "Generative and Agentic AI", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4}
        ]
        records = default_sample

    df_out = pd.DataFrame(records)
    if "Course_ID" not in df_out.columns:
        df_out["Course_ID"] = [f"C{i+1:03d}" for i in range(len(df_out))]

    # Ensure Course_Key incorporates Year for differentiation (e.g. [III Year] NLP vs [M.Tech] NLP)
    if "Course_Key" not in df_out.columns:
        df_out["Course_Key"] = df_out.apply(
            lambda r: f"[{r['Year']}] {r['Subject']}" if pd.notna(r.get("Year")) and str(r.get("Year")).strip() not in ("", "General") else r["Subject"],
            axis=1
        )

    return df_out

def _parse_course_dataframe(df: pd.DataFrame, default_year: str = "General") -> List[Dict[str, Any]]:
    """Helper to extract course rows from a single DataFrame."""
    df.columns = [str(col).strip() for col in df.columns]

    course_col = None
    course_candidates = [
        "Course Name", "Courses", "Course", "Subject", "Name of the COURSE", 
        "Course_Name", "Course Title", "Course_Title", "Subject Name"
    ]
    for cand in course_candidates:
        for col in df.columns:
            if str(col).strip().lower() == cand.lower():
                course_col = col
                break
        if course_col:
            break
    if not course_col:
        course_col = df.columns[0]

    code_col = None
    for cand in ["Course Code", "Course_Code", "Code", "CourseCode"]:
        for col in df.columns:
            if str(col).strip().lower() == cand.lower():
                code_col = col
                break
        if code_col:
            break

    year_col = None
    for cand in ["Year", "Academic Year", "Level", "Program", "Batch"]:
        for col in df.columns:
            if str(col).strip().lower() == cand.lower():
                year_col = col
                break
        if year_col:
            break

    ltpc_col = None
    for cand in ["L-T-P-C", "L-T-P-SL-C", "LTPC", "Structure", "L-T-P-C Structure"]:
        for col in df.columns:
            if str(col).strip().lower() == cand.lower():
                ltpc_col = col
                break
        if ltpc_col:
            break

    records = []
    current_year = default_year

    for idx, row in df.iterrows():
        val = row.get(course_col)
        if pd.isna(val) or not str(val).strip() or str(val).strip().lower() in ('nan', 'none', ''):
            continue

        str_val = str(val).strip()

        # Check if row is a section header like "I Year Courses" or "II Year Courses"
        if "year" in str_val.lower() and ("course" in str_val.lower() or "m.tech" in str_val.lower()):
            current_year = str_val.replace("Courses", "").strip()
            continue

        subj = clean_subject_name(str_val)
        code_val = str(row[code_col]).strip() if code_col and pd.notna(row.get(code_col)) and str(row.get(code_col)).strip().lower() != 'nan' else ""

        # Determine year
        if year_col and pd.notna(row.get(year_col)):
            y_val = str(row[year_col]).strip()
            if y_val == "1":
                y_val = "I Year"
            elif y_val == "2":
                y_val = "II Year"
            elif y_val == "3":
                y_val = "III Year"
            elif y_val == "4":
                y_val = "IV Year"
            row_year = y_val
        else:
            row_year = current_year

        l_val, t_val, p_val, c_val = 3, 0, 2, 4
        if ltpc_col and pd.notna(row.get(ltpc_col)):
            l_val, t_val, p_val, c_val = parse_ltpc_string(str(row[ltpc_col]))
        else:
            raw_l = pd.to_numeric(row.get("L"), errors='coerce')
            raw_t = pd.to_numeric(row.get("T"), errors='coerce')
            raw_p = pd.to_numeric(row.get("P"), errors='coerce')
            raw_c = pd.to_numeric(row.get("C"), errors='coerce')
            l_val = int(raw_l) if pd.notna(raw_l) else 3
            t_val = int(raw_t) if pd.notna(raw_t) else 0
            p_val = int(raw_p) if pd.notna(raw_p) else 2
            c_val = int(raw_c) if pd.notna(raw_c) else 4

        total_hrs = l_val + t_val + p_val
        course_key = f"[{row_year}] {subj}" if row_year and row_year != "General" else subj

        records.append({
            "Course_ID": f"C{len(records)+1:03d}",
            "Year": row_year,
            "Course_Code": code_val,
            "Subject": subj,
            "L": l_val,
            "T": t_val,
            "P": p_val,
            "C": c_val,
            "L-T-P-C": f"{l_val}-{t_val}-{p_val}-{c_val}",
            "Total_Hours": total_hrs,
            "Course_Key": course_key
        })

    return records

def read_teaching_assistants(file_source: Union[str, BinaryIO]) -> pd.DataFrame:
    """
    Reads Teaching Assistants roster & preferences Excel file into a cleaned DataFrame.
    Columns returned: ['TA_ID', 'TA_Name', 'Preference_1', ..., 'Preference_5', 'Role']
    """
    if hasattr(file_source, 'seek'):
        file_source.seek(0)
    
    try:
        xl = pd.ExcelFile(file_source)
        target_sheet = xl.sheet_names[0]
        for s in xl.sheet_names:
            if "teaching assistant" in s.lower() or "ta" in s.lower() or "assistant" in s.lower():
                target_sheet = s
                break
        df = pd.read_excel(xl, sheet_name=target_sheet)
    except Exception:
        df = pd.read_excel(file_source)

    df.columns = [str(col).strip() for col in df.columns]

    # Find name column
    name_col = None
    for cand in ["name of the teaching assistant", "teaching assistant name", "ta name", "teaching assistant", "name", "ta"]:
        for c in df.columns:
            if str(c).strip().lower() == cand:
                name_col = c
                break
        if name_col:
            break
    if not name_col:
        for c in df.columns:
            if "name" in str(c).lower() and "course" not in str(c).lower():
                name_col = c
                break
    if not name_col:
        name_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    # Find ID column
    id_col = None
    for cand in ["sl.no", "s.no", "sl no", "sno", "id", "ta_id", "ta id"]:
        for c in df.columns:
            if str(c).strip().lower() == cand:
                id_col = c
                break
        if id_col:
            break

    ta_records = []
    for idx, row in df.iterrows():
        raw_name = row.get(name_col)
        if pd.isna(raw_name) or not str(raw_name).strip() or str(raw_name).strip().lower() in ("nan", "none"):
            continue
        ta_name = str(raw_name).strip()
        ta_id = f"TA{idx+1:03d}" if not (id_col and pd.notna(row.get(id_col))) else f"TA{int(row[id_col]):03d}" if str(row[id_col]).isdigit() else f"TA{idx+1:03d}"

        p_dict = {
            "TA_ID": ta_id,
            "TA_Name": ta_name,
            "Role": "Teaching Assistant"
        }

        # Extract Theory-1 to Theory-5 or Preference 1-5
        for rank in range(1, 6):
            pref_val = None
            for col in df.columns:
                cl = str(col).lower().replace("_", " ").strip()
                cl_nodash = cl.replace("-", " ")
                if (f"theory {rank}" in cl_nodash or f"preference {rank}" in cl or f"pref {rank}" in cl or f"p{rank}" == cl):
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).strip().lower() not in ('nan', 'none'):
                        pref_val = clean_subject_name(str(val))
                        break
            p_dict[f"Preference_{rank}"] = pref_val
        
        ta_records.append(p_dict)

    return pd.DataFrame(ta_records)

def parse_wide_combined_sheet(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parses a single combined Excel sheet into standard Preferences and Experience DataFrames.
    Robustly identifies Faculty Name, Designation, Qualification, and Course Preferences/Theories (1-5+).
    """
    df.columns = [str(col).strip() for col in df.columns]

    name_col = None
    name_candidates = [
        "name of the faculty", "faculty name", "faculty_name", "facultyname",
        "name of faculty", "name of the teacher", "teacher name", "staff name",
        "faculty", "name"
    ]
    avoid_keywords = ["sl", "s.no", "sl.no", "serial", "sno", "id", "e.cod", "ecod", "code", "emp", "course", "subject", "exp"]

    for cand in name_candidates:
        for c in df.columns:
            cl = str(c).strip().lower()
            if cl == cand:
                name_col = c
                break
        if name_col:
            break

    if not name_col:
        for c in df.columns:
            cl = str(c).strip().lower()
            if "name" in cl and not any(k in cl for k in ["course", "subject", "dept", "department", "college", "school"]):
                name_col = c
                break

    if not name_col:
        for c in df.columns:
            cl = str(c).strip().lower()
            if not any(k in cl for k in avoid_keywords):
                sample_vals = df[c].dropna().astype(str).tolist()[:5]
                if sample_vals and not any(v.replace('.', '', 1).isdigit() for v in sample_vals):
                    name_col = c
                    break

    if not name_col:
        name_col = df.columns[0]

    desig_col = None
    for c in ["Designation", "Role", "Position", "Title", "Post"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                desig_col = col
                break
        if desig_col:
            break

    addl_col = None
    for c in ["Additional Duties", "Additional_Duties", "Addl Duties", "Addl_Duties", "Duties", "Responsibility"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                addl_col = col
                break
        if addl_col:
            break

    qual_col = None
    for c in ["Qualification", "Degree", "Highest Qualification", "Qual"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                qual_col = col
                break
        if qual_col:
            break

    id_col = None
    for c in ["E.Cod", "E_Cod", "ECod", "Employee Code", "Emp ID", "Faculty ID", "Faculty_ID", "ID", "Sl.No", "S.No"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                id_col = col
                break
        if id_col:
            break

    pref_rows = []
    exp_rows = []

    for idx, row in df.iterrows():
        raw_name = row[name_col] if name_col in df.columns else None
        if pd.isna(raw_name) or str(raw_name).strip() in ("", "nan", "None"):
            continue

        fac_name = str(raw_name).strip()
        if fac_name.isdigit() and len(fac_name) <= 3 and id_col and id_col != name_col:
            continue

        emp_code = str(row[id_col]).strip() if id_col and pd.notna(row[id_col]) else f"{idx+1}"
        fac_id = f"F{idx+1:03d}"

        desig = str(row[desig_col]).strip() if desig_col and pd.notna(row[desig_col]) else "Professor"
        
        if addl_col and pd.notna(row[addl_col]):
            addl = str(row[addl_col]).strip()
        else:
            desig_low = desig.lower()
            if "dean" in desig_low:
                addl = "Dean"
            elif "hod" in desig_low or "head" in desig_low:
                addl = "HOD"
            elif "selection grade" in desig_low:
                addl = "Selection Grade"
            elif "senior" in desig_low:
                addl = "Senior Level"
            elif "teaching associate" in desig_low or "teaching assistant" in desig_low or "cap" in desig_low or "era" in desig_low:
                addl = "Teaching Associate"
            else:
                addl = "None"

        if qual_col and pd.notna(row[qual_col]):
            qual = str(row[qual_col]).strip()
        else:
            if "dr." in fac_name.lower() or "prof" in desig.lower() or "dean" in desig.lower():
                qual = "PhD"
            else:
                qual = "M.Tech"

        role = extract_role(desig, addl, fac_name)

        p_dict = {
            "Faculty_ID": fac_id,
            "Faculty_Name": fac_name,
            "Employee_Code": emp_code,
            "Designation": desig,
            "Additional_Duties": addl,
            "Role": role,
            "Qualification": qual
        }

        # Check preferences 1 to 10
        for rank in range(1, 11):
            pref_val = None
            exp_val = 0.0

            for col in df.columns:
                col_clean = str(col).lower().replace("_", " ").strip()
                col_nodash = col_clean.replace("-", " ")
                is_exp_col = any(k in col_clean for k in ["exp", "year", "teaching", "duration", "yrs"])

                # Check for preference course name (Theory-1, Preference 1, etc.)
                if not is_exp_col:
                    matches_rank = (
                        f"theory {rank}" in col_nodash or
                        f"theory_{rank}" in col_clean or
                        f"theory-{rank}" in col_clean or
                        f"preference {rank}" in col_clean or
                        f"pref {rank}" in col_clean or
                        f"course preference {rank}" in col_clean or
                        col_clean == f"course {rank}" or
                        col_clean == f"p{rank}" or
                        col_clean == f"pref_{rank}"
                    )
                    if matches_rank and pd.notna(row[col]) and str(row[col]).strip().lower() not in ('nan', 'none', ''):
                        pref_val = clean_subject_name(str(row[col]))

                # Check for course experience
                if is_exp_col:
                    matches_exp_rank = (
                        f"{rank}" in col_clean and (
                            "course" in col_clean or "pref" in col_clean or "exp" in col_clean or f"p{rank}" in col_clean
                        )
                    )
                    if matches_exp_rank:
                        val = pd.to_numeric(row[col], errors='coerce')
                        if pd.notna(val):
                            exp_val = float(val)

            if rank <= 5:
                p_dict[f"Preference_{rank}"] = pref_val

            if pref_val:
                # If experience is not provided in sheet, estimate realistic value from role & rank
                if exp_val <= 0:
                    if role == "Dean":
                        exp_val = 12.0
                    elif role == "HOD":
                        exp_val = 10.0
                    elif role == "Professor":
                        exp_val = max(1.0, 9.0 - (rank * 0.5))
                    elif "Associate" in role:
                        exp_val = max(1.0, 7.0 - (rank * 0.5))
                    elif "Assistant" in role:
                        exp_val = max(1.0, 5.0 - (rank * 0.5))
                    else:
                        exp_val = max(0.5, 2.5 - (rank * 0.3))

                exp_rows.append({
                    "Faculty_ID": fac_id,
                    "Subject": pref_val,
                    "Qualification": qual,
                    "Skill_Level": derive_skill_level(exp_val),
                    "Experience_Years": exp_val,
                    "Preference_Rank": rank,
                    "Role": role
                })

        for r in range(1, 6):
            if f"Preference_{r}" not in p_dict:
                p_dict[f"Preference_{r}"] = None

        pref_rows.append(p_dict)

    pref_df = pd.DataFrame(pref_rows)
    exp_df = pd.DataFrame(exp_rows)

    return pref_df, exp_df

def read_faculty_preferences(file_source: Union[str, BinaryIO]) -> pd.DataFrame:
    """Reads faculty preferences Excel file into a cleaned DataFrame."""
    if hasattr(file_source, 'seek'):
        file_source.seek(0)
    df = pd.read_excel(file_source)
    df.columns = [str(col).strip() for col in df.columns]

    # If it's a wide combined sheet, or has 'theory-1' or 'preference 1', parse wide
    col_str = " ".join([c.lower() for c in df.columns])
    if any(k in col_str for k in ["course preference", "preference 1", "theory-1", "theory 1", "theory- 1", "name of the faculty"]):
        pref_df, _ = parse_wide_combined_sheet(df)
        return pref_df

    expected_cols = ["Faculty_ID", "Faculty_Name", "Preference_1", "Preference_2", "Preference_3", "Preference_4", "Preference_5"]
    for col in expected_cols:
        if col not in df.columns:
            for actual_col in df.columns:
                if actual_col.lower() == col.lower() or actual_col.lower().replace("_", " ") == col.lower().replace("_", " "):
                    df.rename(columns={actual_col: col}, inplace=True)
                    break

    for col in df.columns:
        if df[col].dtype == object or df[col].dtype == 'string':
            df[col] = df[col].astype(str).str.strip()
            if col.startswith("Preference_"):
                df[col] = df[col].apply(clean_subject_name)
            df[col] = df[col].replace({'nan': None, 'None': None, '': None})

    if "Faculty_ID" not in df.columns:
        df["Faculty_ID"] = [f"F{i+1:03d}" for i in range(len(df))]
    else:
        df.dropna(subset=["Faculty_ID"], inplace=True)

    if "Role" not in df.columns:
        df["Role"] = df.apply(lambda r: extract_role(str(r.get("Designation", "")), str(r.get("Additional_Duties", "")), str(r.get("Faculty_Name", ""))), axis=1)

    return df

def read_faculty_experience(file_source: Union[str, BinaryIO]) -> pd.DataFrame:
    """Reads faculty experience & qualification Excel file into a cleaned DataFrame."""
    if hasattr(file_source, 'seek'):
        file_source.seek(0)
    df = pd.read_excel(file_source)
    df.columns = [str(col).strip() for col in df.columns]

    col_str = " ".join([c.lower() for c in df.columns])
    if any(k in col_str for k in ["course preference", "preference 1", "theory-1", "theory 1", "name of the faculty"]):
        _, exp_df = parse_wide_combined_sheet(df)
        return exp_df

    expected_cols = ["Faculty_ID", "Subject", "Qualification", "Skill_Level", "Experience_Years"]
    for col in expected_cols:
        if col not in df.columns:
            for actual_col in df.columns:
                if actual_col.lower() == col.lower() or actual_col.lower().replace("_", " ") == col.lower().replace("_", " "):
                    df.rename(columns={actual_col: col}, inplace=True)
                    break

    for col in ["Faculty_ID", "Subject", "Qualification", "Skill_Level"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            if col == "Subject":
                df[col] = df[col].apply(clean_subject_name)
            df[col] = df[col].replace({'nan': None, 'None': None, '': None})

    if "Experience_Years" in df.columns:
        df["Experience_Years"] = pd.to_numeric(df["Experience_Years"], errors='coerce').fillna(0)

    if "Faculty_ID" in df.columns and "Subject" in df.columns:
        df.dropna(subset=["Faculty_ID", "Subject"], inplace=True)
    return df

def load_both_excel_files(
    pref_file: Union[str, BinaryIO],
    exp_file: Optional[Union[str, BinaryIO]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads faculty preferences and experience dataframes."""
    if exp_file is None or exp_file == "" or pref_file == exp_file:
        if hasattr(pref_file, 'seek'):
            pref_file.seek(0)
        
        xl = pd.ExcelFile(pref_file)
        sheet_names_lower = [s.strip().lower() for s in xl.sheet_names]
        
        has_pref_sheet = any("pref" in s for s in sheet_names_lower)
        has_exp_sheet = any("exp" in s or "qual" in s for s in sheet_names_lower)
        
        if has_pref_sheet and has_exp_sheet:
            pref_sheet = [s for s in xl.sheet_names if "pref" in s.strip().lower()][0]
            exp_sheet = [s for s in xl.sheet_names if any(k in s.strip().lower() for k in ["exp", "qual"])][0]
            pref_df = read_faculty_preferences(pd.read_excel(xl, sheet_name=pref_sheet))
            exp_df = read_faculty_experience(pd.read_excel(xl, sheet_name=exp_sheet))
            return pref_df, exp_df

        df = pd.read_excel(xl, sheet_name=0)
        return parse_wide_combined_sheet(df)

    if hasattr(pref_file, 'seek'):
        pref_file.seek(0)
    if hasattr(exp_file, 'seek'):
        exp_file.seek(0)

    pref_df = read_faculty_preferences(pref_file)
    exp_df = read_faculty_experience(exp_file)
    return pref_df, exp_df

def load_all_excel_files(
    pref_file: Union[str, BinaryIO],
    exp_file: Optional[Union[str, BinaryIO]] = None,
    course_file: Optional[Union[str, BinaryIO]] = None,
    ta_file: Optional[Union[str, BinaryIO]] = None,
    return_ta: bool = False
) -> Any:
    """
    Loads preferences, experience, multi-year course details, and optional teaching assistants.
    If return_ta is True: returns (pref_df, exp_df, course_df, ta_df)
    If return_ta is False: returns (pref_df, exp_df, course_df) for 100% backward compatibility.
    """
    pref_df, exp_df = load_both_excel_files(pref_file, exp_file)

    # 1. Load Courses
    if course_file is not None and course_file != "":
        if hasattr(course_file, 'seek'):
            course_file.seek(0)
        course_df = read_course_details(course_file)
    else:
        found_in_workbook = False
        try:
            if hasattr(pref_file, 'seek'):
                pref_file.seek(0)
            xl = pd.ExcelFile(pref_file)
            for s in xl.sheet_names:
                if any(k in s.strip().lower() for k in ["course", "subject", "structure", "ltpc", "year"]):
                    course_df = read_course_details(pd.read_excel(xl, sheet_name=s))
                    found_in_workbook = True
                    break
        except Exception:
            pass

        if not found_in_workbook:
            default_course_path = "input/course_details.xlsx"
            if os.path.exists(default_course_path):
                course_df = read_course_details(default_course_path)
            else:
                default_multi_path = "input/courses_multiyear.xlsx"
                if os.path.exists(default_multi_path):
                    course_df = read_course_details(default_multi_path)
                else:
                    course_df = read_course_details(pd.DataFrame([
                        {"Year": "I Year", "Course Name": "Python Programming Essentials", "L": 1, "T": 2, "P": 2, "C": 3, "L-T-P-C": "1-2-2-3", "Total_Hours": 5},
                        {"Year": "II Year", "Course Name": "Machine Learning", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
                        {"Year": "III Year", "Course Name": "Natural Language Processing", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5}
                    ]))

    # 2. Load Teaching Assistants (TAs)
    ta_df = None
    if ta_file is not None and ta_file != "":
        if hasattr(ta_file, 'seek'):
            ta_file.seek(0)
        try:
            ta_df = read_teaching_assistants(ta_file)
        except Exception as e:
            print(f"Warning reading TA file: {e}")

    if ta_df is None or ta_df.empty:
        # Check if pref_file workbook contains a TA sheet
        try:
            if hasattr(pref_file, 'seek'):
                pref_file.seek(0)
            xl = pd.ExcelFile(pref_file)
            for s in xl.sheet_names:
                if any(k in s.strip().lower() for k in ["teaching assistant", "ta", "assistant"]):
                    ta_df = read_teaching_assistants(pd.read_excel(xl, sheet_name=s))
                    break
        except Exception:
            pass

    if ta_df is None or ta_df.empty:
        default_ta_path = "input/teaching_assistants.xlsx"
        if os.path.exists(default_ta_path):
            try:
                ta_df = read_teaching_assistants(default_ta_path)
            except Exception:
                ta_df = pd.DataFrame(columns=["TA_ID", "TA_Name", "Preference_1", "Preference_2", "Preference_3", "Preference_4", "Preference_5"])
        else:
            ta_df = pd.DataFrame(columns=["TA_ID", "TA_Name", "Preference_1", "Preference_2", "Preference_3", "Preference_4", "Preference_5"])

    if return_ta:
        return pref_df, exp_df, course_df, ta_df
    return pref_df, exp_df, course_df
