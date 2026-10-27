import pandas as pd
from typing import Union, BinaryIO, Tuple, Optional

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
    """Detects role: Dean, HOD, Associate Professor, Assistant Professor, Professor."""
    combined = f"{designation} {addl_duties} {fac_name}".lower()
    if "dean" in combined:
        return "Dean"
    elif "hod" in combined or "head of" in combined or "h.o.d" in combined:
        return "HOD"
    elif "associate" in combined or "assoc" in combined:
        return "Associate Professor"
    elif "assistant" in combined or "asst" in combined:
        return "Assistant Professor"
    elif "professor" in combined or "prof" in combined:
        return "Professor"
    return "Faculty"

def parse_ltpc_string(ltpc_str: str) -> Tuple[int, int, int, int]:
    """Parses 'L-T-P-C' format string like '3-0-2-4' or '1-2-0-2' into (L, T, P, C)."""
    try:
        parts = [int(x.strip()) for x in str(ltpc_str).split("-")]
        if len(parts) >= 4:
            return parts[0], parts[1], parts[2], parts[3]
        elif len(parts) == 3:
            return parts[0], parts[1], parts[2], parts[0] + parts[1] + parts[2]
    except Exception:
        pass
    return 3, 0, 2, 4

def read_course_details(file_source: Union[str, BinaryIO]) -> pd.DataFrame:
    """
    Reads Course Details Excel file containing Courses and L-T-P-C columns.
    Returns cleaned DataFrame with columns: ['Subject', 'L', 'T', 'P', 'C', 'L-T-P-C', 'Total_Hours'].
    """
    df = pd.read_excel(file_source)
    df.columns = [str(col).strip() for col in df.columns]

    course_col = None
    course_candidates = [
        "Courses", "Course", "Subject", "Course Name", "Name of the COURSE", 
        "Course_Name", "Course Title", "Course_Title", "Subject Name", "Course Title"
    ]
    for c in course_candidates:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                course_col = col
                break
        if course_col:
            break
    if not course_col:
        course_col = df.columns[0]

    ltpc_col = None
    for c in ["L-T-P-C", "L-T-P-C Structure", "LTPC", "Structure"]:
        if c in df.columns:
            ltpc_col = c
            break

    records = []
    for _, row in df.iterrows():
        subj = str(row[course_col]).replace('–', '-').replace('—', '-').replace('−', '-').strip()
        if not subj or subj.lower() in ('nan', 'none', ''):
            continue

        l_val, t_val, p_val, c_val = 3, 0, 2, 4
        if ltpc_col and pd.notna(row.get(ltpc_col)):
            l_val, t_val, p_val, c_val = parse_ltpc_string(row[ltpc_col])
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
        records.append({
            "Subject": subj,
            "L": l_val,
            "T": t_val,
            "P": p_val,
            "C": c_val,
            "L-T-P-C": f"{l_val}-{t_val}-{p_val}-{c_val}",
            "Total_Hours": total_hrs
        })

    return pd.DataFrame(records)


def parse_wide_combined_sheet(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parses a single combined Excel sheet into standard Preferences and Experience DataFrames.
    Robustly identifies Faculty Name (avoiding serial numbers), Designation, Qualification,
    and side-by-side Course Preferences (1-5+) and Course Experience.
    """
    # Clean and strip column names
    df.columns = [str(col).strip() for col in df.columns]

    # 1. Identify Faculty Name Column (Avoid serial number / ID columns)
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

    # If exact candidate not found, look for any column containing 'name'
    if not name_col:
        for c in df.columns:
            cl = str(c).strip().lower()
            if "name" in cl and not any(k in cl for k in ["course", "subject", "dept", "department", "college", "school"]):
                name_col = c
                break

    # If still not found, search for first non-numeric text column
    if not name_col:
        for c in df.columns:
            cl = str(c).strip().lower()
            if not any(k in cl for k in avoid_keywords):
                # Check if values look like person names (strings > 2 chars)
                sample_vals = df[c].dropna().astype(str).tolist()[:5]
                if sample_vals and not any(v.replace('.', '', 1).isdigit() for v in sample_vals):
                    name_col = c
                    break

    if not name_col:
        name_col = df.columns[0]

    # 2. Identify Designation Column
    desig_col = None
    for c in ["Designation", "Role", "Position", "Title", "Post"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                desig_col = col
                break
        if desig_col:
            break

    # 3. Identify Additional Duties Column
    addl_col = None
    for c in ["Additional Duties", "Additional_Duties", "Addl Duties", "Addl_Duties", "Duties", "Responsibility"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                addl_col = col
                break
        if addl_col:
            break

    # 4. Identify Qualification Column
    qual_col = None
    for c in ["Qualification", "Degree", "Highest Qualification", "Qual"]:
        for col in df.columns:
            if str(col).strip().lower() == c.lower():
                qual_col = col
                break
        if qual_col:
            break

    # 5. Identify Employee Code / ID Column
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
        # Clean faculty name
        raw_name = row[name_col] if name_col in df.columns else None
        if pd.isna(raw_name) or str(raw_name).strip() in ("", "nan", "None"):
            continue

        fac_name = str(raw_name).strip()
        # If the name is purely an integer and an id_col exists that is different, try to avoid
        if fac_name.isdigit() and len(fac_name) <= 3 and id_col and id_col != name_col:
            continue

        emp_code = str(row[id_col]).strip() if id_col and pd.notna(row[id_col]) else f"{idx+1}"
        fac_id = f"F{idx+1:03d}"

        # Clean designation
        desig = str(row[desig_col]).strip() if desig_col and pd.notna(row[desig_col]) else "Professor"
        
        # Clean additional duties
        if addl_col and pd.notna(row[addl_col]):
            addl = str(row[addl_col]).strip()
        else:
            # Infer from designation
            desig_low = desig.lower()
            if "dean" in desig_low:
                addl = "Dean"
            elif "hod" in desig_low or "head" in desig_low:
                addl = "HOD"
            elif "selection grade" in desig_low:
                addl = "Selection Grade"
            elif "senior" in desig_low:
                addl = "Senior Level"
            else:
                addl = "None"

        # Clean qualification
        if qual_col and pd.notna(row[qual_col]):
            qual = str(row[qual_col]).strip()
        else:
            # Infer from name or designation
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
            found_pref = False

            for col in df.columns:
                col_clean = str(col).lower().replace("_", " ").strip()
                is_exp_col = any(k in col_clean for k in ["exp", "year", "teaching", "duration", "yrs"])

                # Check for preference course name
                if not is_exp_col:
                    matches_rank = (
                        f"preference {rank}" in col_clean or
                        f"pref {rank}" in col_clean or
                        f"course preference {rank}" in col_clean or
                        col_clean == f"course {rank}" or
                        col_clean == f"p{rank}" or
                        col_clean == f"pref_{rank}"
                    )
                    if matches_rank and pd.notna(row[col]) and str(row[col]).strip().lower() not in ('nan', 'none', ''):
                        pref_val = str(row[col]).replace('–', '-').replace('—', '-').replace('−', '-').strip()
                        found_pref = True

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
                exp_rows.append({
                    "Faculty_ID": fac_id,
                    "Subject": pref_val,
                    "Qualification": qual,
                    "Skill_Level": derive_skill_level(exp_val),
                    "Experience_Years": exp_val,
                    "Preference_Rank": rank,
                    "Role": role
                })

        # Ensure Preference_1 to Preference_5 exist in p_dict
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

    if any("course preference" in c.lower() or "preference 1" in c.lower() for c in df.columns):
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
                df[col] = df[col].str.replace('–', '-').str.replace('—', '-').str.replace('−', '-')
            df[col] = df[col].replace({'nan': None, 'None': None, '': None})

    if "Faculty_ID" in df.columns:
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

    if any("course preference" in c.lower() or "preference 1" in c.lower() for c in df.columns):
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
                df[col] = df[col].str.replace('–', '-').str.replace('—', '-').str.replace('−', '-')
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
    """
    Loads faculty preferences and experience.
    Supports either:
    1. A single combined Excel sheet (when exp_file is None or identical to pref_file).
    2. Two separate Excel files for backward compatibility.
    """
    # If only one file is provided or both point to same source
    if exp_file is None or exp_file == "" or pref_file == exp_file:
        if hasattr(pref_file, 'seek'):
            pref_file.seek(0)
        
        # Check workbook sheets
        xl = pd.ExcelFile(pref_file)
        sheet_names_lower = [s.strip().lower() for s in xl.sheet_names]
        
        # Check if workbook has separate Preferences and Experience sheets
        has_pref_sheet = any("pref" in s for s in sheet_names_lower)
        has_exp_sheet = any("exp" in s or "qual" in s for s in sheet_names_lower)
        
        if has_pref_sheet and has_exp_sheet:
            pref_sheet = [s for s in xl.sheet_names if "pref" in s.strip().lower()][0]
            exp_sheet = [s for s in xl.sheet_names if any(k in s.strip().lower() for k in ["exp", "qual"])][0]
            pref_df = read_faculty_preferences(pd.read_excel(xl, sheet_name=pref_sheet))
            exp_df = read_faculty_experience(pd.read_excel(xl, sheet_name=exp_sheet))
            return pref_df, exp_df

        # Otherwise parse as wide combined sheet
        df = pd.read_excel(xl, sheet_name=0)
        return parse_wide_combined_sheet(df)

    # If two separate files are provided
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
    course_file: Optional[Union[str, BinaryIO]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads preferences, experience, and course details DataFrames."""
    pref_df, exp_df = load_both_excel_files(pref_file, exp_file)

    if course_file is not None:
        if hasattr(course_file, 'seek'):
            course_file.seek(0)
        course_df = read_course_details(course_file)
    else:
        # Check if pref_file workbook contains a Course Details sheet
        found_in_workbook = False
        try:
            if hasattr(pref_file, 'seek'):
                pref_file.seek(0)
            xl = pd.ExcelFile(pref_file)
            for s in xl.sheet_names:
                if any(k in s.strip().lower() for k in ["course", "subject", "structure", "ltpc"]):
                    course_df = read_course_details(pd.read_excel(xl, sheet_name=s))
                    found_in_workbook = True
                    break
        except Exception:
            pass

        if not found_in_workbook:
            import os
            default_course_path = "input/course_details.xlsx"
            if os.path.exists(default_course_path):
                course_df = read_course_details(default_course_path)
            else:
                records = [
                    {"Subject": "Quantitative Aptitude & Logical Reasoning", "L": 1, "T": 2, "P": 0, "C": 2, "L-T-P-C": "1-2-0-2", "Total_Hours": 3},
                    {"Subject": "Deep Learning", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
                    {"Subject": "Web Technologies", "L": 2, "T": 0, "P": 4, "C": 4, "L-T-P-C": "2-0-4-4", "Total_Hours": 6},
                    {"Subject": "Inter Departmental Project with Agentic Tools", "L": 0, "T": 0, "P": 2, "C": 1, "L-T-P-C": "0-0-2-1", "Total_Hours": 2},
                    {"Subject": "Machine Learning Operations (DE-2)", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4},
                    {"Subject": "Computer Vision (DE-2)", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5}
                ]
                course_df = pd.DataFrame(records)

    return pref_df, exp_df, course_df


