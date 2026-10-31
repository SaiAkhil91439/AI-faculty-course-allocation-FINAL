import os
import io
from typing import Optional, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import hmac
import zipfile
import numpy as np
import pandas as pd

from pydantic import BaseModel
from backend.excel_reader import load_all_excel_files
from backend.validator import validate_inputs, AllocationValidationError
from backend.agent import FacultyAllocationAgent
from backend.workload_calculator import calculate_ltpc_workload, DEFAULT_PROMPT_COURSES, convert_course_df_to_workload_input
from backend.workload_excel import generate_workload_excel
from input.sample_generator import generate_sample_files

app = FastAPI(title="AI Faculty-Subject-Section Allocation Agent API", version="1.0.0")

class ChatRequest(BaseModel):
    question: str

class LTPCWorkloadRequest(BaseModel):
    num_sections: int = 12
    l_faculty_multiplier: int = 1
    t_faculty_multiplier: int = 3
    p_faculty_multiplier: int = 3
    avg_faculty_capacity_hours: float = 15.0
    num_available_faculty: Optional[int] = 34
    courses: Optional[list] = None

# Session-based login. Change these environment variables in production.
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-session-secret-in-production")
LOGIN_USERNAME = os.getenv("FACULTY_APP_USERNAME", "admin")
LOGIN_PASSWORD = os.getenv("FACULTY_APP_PASSWORD", "admin123")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, max_age=60 * 60 * 8, same_site="lax", https_only=False)

def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated") is True

def verify_credentials(username: str, password: str) -> bool:
    return hmac.compare_digest(username, LOGIN_USERNAME) and hmac.compare_digest(password, LOGIN_PASSWORD)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store persistent upload paths
UPLOAD_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ensure sample files exist
generate_sample_files(UPLOAD_DIR)

agent_orchestrator = FacultyAllocationAgent()

def is_valid_upload(f: Optional[UploadFile]) -> bool:
    """Checks if UploadFile has a non-empty filename and valid stream."""
    return f is not None and bool(getattr(f, "filename", None) and str(f.filename).strip())

def resolve_file_sources(
    faculty_file: Optional[UploadFile] = None,
    pref_file: Optional[UploadFile] = None,
    exp_file: Optional[UploadFile] = None,
    course_file: Optional[UploadFile] = None,
    ta_file: Optional[UploadFile] = None
):
    """Safely extracts valid file streams from multipart form or falls back to disk samples."""
    target_fac = faculty_file if is_valid_upload(faculty_file) else (pref_file if is_valid_upload(pref_file) else None)
    has_exp = is_valid_upload(exp_file)
    has_course = is_valid_upload(course_file)
    has_ta = is_valid_upload(ta_file)

    if target_fac:
        pref_src = target_fac.file
        exp_src = exp_file.file if has_exp else None
    elif has_exp:
        comb_sample = os.path.join(UPLOAD_DIR, "faculty_sample_combined.xlsx")
        pref_src = comb_sample if os.path.exists(comb_sample) else os.path.join(UPLOAD_DIR, "faculty_preferences.xlsx")
        exp_src = exp_file.file
    else:
        comb_sample = os.path.join(UPLOAD_DIR, "faculty_sample_combined.xlsx")
        if os.path.exists(comb_sample):
            pref_src = comb_sample
            exp_src = None
        else:
            pref_src = os.path.join(UPLOAD_DIR, "faculty_preferences.xlsx")
            exp_src = os.path.join(UPLOAD_DIR, "faculty_experience.xlsx")

    if has_course:
        course_src = course_file.file
    else:
        # Match course file with faculty file source
        if pref_src and "preferences" in str(pref_src).lower():
            multi_course = os.path.join(UPLOAD_DIR, "courses_multiyear.xlsx")
            norm_course = os.path.join(UPLOAD_DIR, "course_details.xlsx")
            course_src = multi_course if os.path.exists(multi_course) else (norm_course if os.path.exists(norm_course) else None)
        else:
            norm_course = os.path.join(UPLOAD_DIR, "course_details.xlsx")
            multi_course = os.path.join(UPLOAD_DIR, "courses_multiyear.xlsx")
            course_src = norm_course if os.path.exists(norm_course) else (multi_course if os.path.exists(multi_course) else None)

    if has_ta:
        ta_src = ta_file.file
    else:
        ta_sample = os.path.join(UPLOAD_DIR, "teaching_assistants.xlsx")
        ta_src = ta_sample if os.path.exists(ta_sample) else None

    return pref_src, exp_src, course_src, ta_src

def sanitize_for_json(data: Any) -> Any:
    """Recursively converts numpy and pandas types to standard Python primitives for JSON response."""
    if isinstance(data, dict):
        return {str(k): sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple, set)):
        return [sanitize_for_json(v) for v in data]
    elif isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32)):
        return float(data)
    elif isinstance(data, np.ndarray):
        return [sanitize_for_json(v) for v in data.tolist()]
    elif pd.isna(data):
        return None
    return data

@app.post("/api/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not verify_credentials(username.strip(), password):
        accept = request.headers.get("accept", "")
        if "application/json" in accept or request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JSONResponse(status_code=401, content={"success": False, "message": "Invalid username or password."})
        return RedirectResponse(url="/login?error=invalid", status_code=303)
    request.session.clear()
    request.session["authenticated"] = True
    request.session["username"] = username.strip()
    accept = request.headers.get("accept", "")
    if "application/json" in accept or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JSONResponse(content={"success": True, "message": "Login successful."})
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/auth/me")
async def auth_me(request: Request):
    if not is_authenticated(request):
        return JSONResponse(status_code=401, content={"authenticated": False})
    return {"authenticated": True, "username": request.session.get("username", "User")}

@app.post("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return {"success": True}

@app.post("/api/sample-data")
async def get_sample_files(request: Request):
    """Generates sample Excel files and returns them as a zip package."""
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    pref_path = os.path.join(UPLOAD_DIR, "faculty_preferences.xlsx")
    exp_path = os.path.join(UPLOAD_DIR, "faculty_experience.xlsx")
    course_path = os.path.join(UPLOAD_DIR, "course_details.xlsx")
    comb_path = os.path.join(UPLOAD_DIR, "faculty_sample_combined.xlsx")
    
    if not os.path.exists(comb_path) or not os.path.exists(course_path):
        generate_sample_files(UPLOAD_DIR)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if os.path.exists(comb_path):
            zip_file.write(comb_path, arcname="faculty_sample_combined.xlsx")
        if os.path.exists(pref_path):
            zip_file.write(pref_path, arcname="faculty_preferences.xlsx")
        if os.path.exists(exp_path):
            zip_file.write(exp_path, arcname="faculty_experience.xlsx")
        if os.path.exists(course_path):
            zip_file.write(course_path, arcname="course_details.xlsx")
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=faculty_sample_excel_files.zip"}
    )

@app.get("/api/preview-data")
@app.post("/api/preview-data")
async def preview_data(
    request: Request,
    faculty_file: Optional[UploadFile] = File(None),
    pref_file: Optional[UploadFile] = File(None),
    exp_file: Optional[UploadFile] = File(None),
    course_file: Optional[UploadFile] = File(None),
    ta_file: Optional[UploadFile] = File(None)
):
    """
    Returns preview records, summary analytics, and column details for faculty, course curriculum,
    and Teaching Assistants (TAs). Works with either uploaded Excel files or default sample files.
    """
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        pref_src, exp_src, course_src, ta_src = resolve_file_sources(faculty_file, pref_file, exp_file, course_file, ta_file)
        pref_df, exp_df, course_df, ta_df = load_all_excel_files(pref_src, exp_src, course_src, ta_src, return_ta=True)

        faculty_records = []
        role_counts = {}
        designation_counts = {}

        # Build faculty experiences lookup from exp_df
        exp_by_fac = {}
        if exp_df is not None and not exp_df.empty and "Faculty_ID" in exp_df.columns:
            for _, erow in exp_df.iterrows():
                fid = str(erow.get("Faculty_ID", "")).strip()
                subj = str(erow.get("Subject", "")).strip()
                yrs = erow.get("Experience_Years", 0)
                try:
                    yrs_num = float(yrs)
                    yrs_str = f"{int(yrs_num) if yrs_num.is_integer() else yrs_num}y"
                except Exception:
                    yrs_str = f"{yrs}y"
                if fid not in exp_by_fac:
                    exp_by_fac[fid] = []
                if subj:
                    exp_by_fac[fid].append(f"{subj}: {yrs_str}")

        for _, row in pref_df.iterrows():
            role = str(row.get("Role", "Faculty"))
            desig = str(row.get("Designation", "Faculty"))
            role_counts[role] = role_counts.get(role, 0) + 1
            designation_counts[desig] = designation_counts.get(desig, 0) + 1
            
            fid = str(row.get("Faculty_ID", "")).strip()

            pref_list = []
            for r in range(1, 11):
                col = f"Preference_{r}"
                if col in row and pd.notna(row[col]):
                    val = str(row[col]).strip()
                    if val and val.lower() not in ("none", "nan", ""):
                        pref_list.append(f"{r}. {val}")
            
            if not pref_list and "Preferences" in row and isinstance(row["Preferences"], list):
                pref_list = [f"{i+1}. {p}" for i, p in enumerate(row["Preferences"]) if p]

            pref_str = ", ".join(pref_list) if pref_list else "None specified"
            
            fac_exps = exp_by_fac.get(fid, [])
            exp_str = ", ".join(fac_exps) if fac_exps else "No prior recorded course experience"

            faculty_records.append({
                "Faculty_ID": fid,
                "Faculty_Name": str(row.get("Faculty_Name", "")),
                "Designation": desig,
                "Role": role,
                "Qualification": str(row.get("Qualification", "")),
                "Preferences": pref_str,
                "Experience": exp_str
            })

        course_records = []
        years_available = []
        total_l = 0
        total_t = 0
        total_p = 0
        total_c = 0
        total_contact = 0
        if course_df is not None and not course_df.empty:
            if "Year" in course_df.columns:
                years_available = [str(y).strip() for y in course_df["Year"].dropna().unique() if str(y).strip()]

            for idx, row in course_df.iterrows():
                l = int(row.get("L", 0))
                t = int(row.get("T", 0))
                p = int(row.get("P", 0))
                c = int(row.get("C", 0))
                contact = int(row.get("Total_Hours", l + t + p))
                total_l += l
                total_t += t
                total_p += p
                total_c += c
                total_contact += contact
                course_records.append({
                    "sl_no": idx + 1,
                    "Year": str(row.get("Year", "N/A")),
                    "Course_Code": str(row.get("Course_Code", f"CS{idx+1}")),
                    "Subject": str(row.get("Subject", f"Course {idx+1}")),
                    "L": l,
                    "T": t,
                    "P": p,
                    "C": c,
                    "L-T-P-C": str(row.get("L-T-P-C", f"{l}-{t}-{p}-{c}")),
                    "Total_Hours": contact
                })

        # Process Teaching Assistants records
        ta_records = []
        if ta_df is not None and not ta_df.empty:
            for idx, row in ta_df.iterrows():
                t_id = str(row.get("TA_ID", f"TA{idx+1:03d}")).strip()
                t_name = str(row.get("TA_Name", f"TA {idx+1}")).strip()

                t_prefs = []
                for r in range(1, 6):
                    c_col = f"Preference_{r}"
                    if c_col in row and pd.notna(row[c_col]):
                        val = str(row[c_col]).strip()
                        if val and val.lower() not in ("none", "nan", ""):
                            t_prefs.append(f"{r}. {val}")

                ta_records.append({
                    "sl_no": idx + 1,
                    "TA_ID": t_id,
                    "TA_Name": t_name,
                    "Preferences": ", ".join(t_prefs) if t_prefs else "Open to any course",
                    "Preferences_List": t_prefs
                })

        return JSONResponse(content=jsonable_encoder(sanitize_for_json({
            "success": True,
            "faculty": {
                "records": faculty_records,
                "total_count": len(faculty_records),
                "role_counts": role_counts,
                "designation_counts": designation_counts
            },
            "courses": {
                "records": course_records,
                "total_count": len(course_records),
                "years_available": years_available,
                "total_l": total_l,
                "total_t": total_t,
                "total_p": total_p,
                "total_c": total_c,
                "total_contact_hours": total_contact
            },
            "teaching_assistants": {
                "records": ta_records,
                "total_count": len(ta_records)
            }
        })))
    except Exception as e:
        return JSONResponse(status_code=500, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "message": str(e)
        })))


@app.post("/api/validate")
async def validate_allocation_request(
    request: Request,
    num_sections: int = Form(...),
    num_subjects: int = Form(...),
    sections_per_faculty: int = Form(...),
    max_subjects_per_faculty: int = Form(...),
    dean_max_sections: int = Form(2),
    hod_max_sections: int = Form(3),
    high_exp_threshold: float = Form(8.0),
    tas_per_section: int = Form(2),
    year_filter: Optional[str] = Form("All"),
    faculty_file: Optional[UploadFile] = File(None),
    pref_file: Optional[UploadFile] = File(None),
    exp_file: Optional[UploadFile] = File(None),
    course_file: Optional[UploadFile] = File(None),
    ta_file: Optional[UploadFile] = File(None)
):
    """
    Validates uploaded Excel files, academic year configuration, and TA settings.
    """
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        pref_src, exp_src, course_src, ta_src = resolve_file_sources(faculty_file, pref_file, exp_file, course_file, ta_file)
        pref_df, exp_df, course_df, ta_df = load_all_excel_files(pref_src, exp_src, course_src, ta_src, return_ta=True)
        
        val_summary = validate_inputs(
            pref_df=pref_df,
            exp_df=exp_df,
            num_sections=num_sections,
            num_subjects=num_subjects,
            sections_per_faculty=sections_per_faculty,
            max_subjects_per_faculty=max_subjects_per_faculty,
            course_df=course_df,
            dean_max_sections=dean_max_sections,
            hod_max_sections=hod_max_sections,
            high_exp_threshold=high_exp_threshold,
            ta_df=ta_df,
            tas_per_section=tas_per_section,
            year_filter=year_filter
        )

        return JSONResponse(content=jsonable_encoder(sanitize_for_json({
            "success": True,
            "message": "Data & constraint validation passed successfully!",
            "summary": val_summary
        })))
    except AllocationValidationError as e:
        return JSONResponse(status_code=400, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "error_type": "ValidationError",
            "message": e.message,
            "details": e.details
        })))
    except Exception as e:
        return JSONResponse(status_code=500, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "error_type": "SystemError",
            "message": str(e)
        })))

@app.post("/api/allocate")
async def run_allocation(
    request: Request,
    num_sections: int = Form(...),
    num_subjects: int = Form(...),
    sections_per_faculty: int = Form(...),
    max_subjects_per_faculty: int = Form(...),
    dean_max_sections: int = Form(2),
    hod_max_sections: int = Form(3),
    high_exp_threshold: float = Form(8.0),
    weight_pref: float = Form(0.40),
    weight_exp: float = Form(0.30),
    weight_skill: float = Form(0.20),
    weight_qual: float = Form(0.10),
    tas_per_section: int = Form(2),
    year_filter: Optional[str] = Form("All"),
    faculty_file: Optional[UploadFile] = File(None),
    pref_file: Optional[UploadFile] = File(None),
    exp_file: Optional[UploadFile] = File(None),
    course_file: Optional[UploadFile] = File(None),
    ta_file: Optional[UploadFile] = File(None)
):
    """
    Runs full allocation pipeline with Multi-Year Courses and Custom Teaching Assistants:
    Validation -> Scoring -> OR-Tools CP-SAT Optimization -> Multi-Tab Excel Export -> AI Explanation.
    """
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        pref_src, exp_src, course_src, ta_src = resolve_file_sources(faculty_file, pref_file, exp_file, course_file, ta_file)

        custom_weights = {
            "preference": weight_pref,
            "experience": weight_exp,
            "skill": weight_skill,
            "qualification": weight_qual
        }

        output_path = os.path.join(OUTPUT_DIR, "faculty_allocation.xlsx")

        result = agent_orchestrator.run_pipeline(
            pref_file_source=pref_src,
            exp_file_source=exp_src,
            num_sections=num_sections,
            num_subjects=num_subjects,
            sections_per_faculty=sections_per_faculty,
            max_subjects_per_faculty=max_subjects_per_faculty,
            course_file_source=course_src,
            dean_max_sections=dean_max_sections,
            hod_max_sections=hod_max_sections,
            high_exp_threshold=high_exp_threshold,
            weights=custom_weights,
            output_excel_path=output_path,
            ta_file_source=ta_src,
            tas_per_section=tas_per_section,
            year_filter=year_filter
        )

        return JSONResponse(content=jsonable_encoder(sanitize_for_json(result)))

        return JSONResponse(content=jsonable_encoder(sanitize_for_json(result)))

    except AllocationValidationError as e:
        return JSONResponse(status_code=400, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "error_type": "ValidationError",
            "message": e.message,
            "details": e.details
        })))
    except Exception as e:
        return JSONResponse(status_code=500, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "error_type": "AllocationError",
            "message": str(e)
        })))


@app.get("/api/download/faculty_allocation.xlsx")
async def download_allocation_excel(request: Request):
    """Downloads the generated faculty_allocation.xlsx file."""
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    file_path = os.path.join(OUTPUT_DIR, "faculty_allocation.xlsx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Allocation Excel file has not been generated yet.")
    return FileResponse(
        path=file_path,
        filename="faculty_allocation.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=faculty_allocation.xlsx",
            "Cache-Control": "no-cache"
        }
    )

@app.post("/api/calculate-ltpc-workload")
async def api_calculate_ltpc_workload(req: LTPCWorkloadRequest, request: Request):
    """
    Calculates faculty workload based on LTPC structure, section count, and faculty multipliers.
    Formulas:
    Section Workload = (Total L * L_fac) + (Total T * T_fac) + (Total P * P_fac)
    Department Workload = Section Workload * Num_Sections
    """
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        courses = req.courses
        if not courses:
            course_path = os.path.join(UPLOAD_DIR, "course_details.xlsx")
            if os.path.exists(course_path):
                from backend.excel_reader import read_course_details
                cdf = read_course_details(course_path)
                courses = convert_course_df_to_workload_input(cdf)
            else:
                courses = DEFAULT_PROMPT_COURSES

        workload_res = calculate_ltpc_workload(
            courses=courses,
            num_sections=req.num_sections,
            l_faculty_multiplier=req.l_faculty_multiplier,
            t_faculty_multiplier=req.t_faculty_multiplier,
            p_faculty_multiplier=req.p_faculty_multiplier,
            avg_faculty_capacity_hours=req.avg_faculty_capacity_hours,
            num_available_faculty=req.num_available_faculty or 34
        )

        # Pre-generate Excel file for immediate download availability
        out_excel = os.path.join(OUTPUT_DIR, "ltpc_workload_calculation.xlsx")
        generate_workload_excel(workload_res, out_excel)

        return JSONResponse(content=jsonable_encoder(sanitize_for_json({
            "success": True,
            "data": workload_res
        })))
    except Exception as e:
        return JSONResponse(status_code=500, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "message": str(e)
        })))

@app.get("/api/download/ltpc-workload.xlsx")
async def download_workload_excel(request: Request):
    """Downloads the generated clear LTPC workload calculation Excel file."""
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    file_path = os.path.join(OUTPUT_DIR, "ltpc_workload_calculation.xlsx")
    if not os.path.exists(file_path):
        data = calculate_ltpc_workload()
        generate_workload_excel(data, file_path)
    return FileResponse(
        path=file_path,
        filename="ltpc_workload_calculation.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=ltpc_workload_calculation.xlsx",
            "Cache-Control": "no-cache"
        }
    )

@app.post("/api/download/ltpc-workload.xlsx")
async def download_custom_workload_excel(req: LTPCWorkloadRequest, request: Request):
    """Generates and downloads a custom LTPC workload calculation Excel file from payload."""
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        courses = req.courses or DEFAULT_PROMPT_COURSES
        workload_res = calculate_ltpc_workload(
            courses=courses,
            num_sections=req.num_sections,
            l_faculty_multiplier=req.l_faculty_multiplier,
            t_faculty_multiplier=req.t_faculty_multiplier,
            p_faculty_multiplier=req.p_faculty_multiplier,
            avg_faculty_capacity_hours=req.avg_faculty_capacity_hours,
            num_available_faculty=req.num_available_faculty or 34
        )
        file_path = os.path.join(OUTPUT_DIR, "ltpc_workload_calculation.xlsx")
        generate_workload_excel(workload_res, file_path)
        return FileResponse(
            path=file_path,
            filename="ltpc_workload_calculation.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=ltpc_workload_calculation.xlsx",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_agent(req: ChatRequest, request: Request):
    """
    Handles live natural language queries from Deans and HODs regarding allocation results,
    workload totals, assignment rationales, and scenario A/B comparison.
    """
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        chat_res = agent_orchestrator.handle_chat_query(req.question)
        return JSONResponse(content=jsonable_encoder(sanitize_for_json(chat_res)))
    except Exception as e:
        return JSONResponse(status_code=500, content=jsonable_encoder(sanitize_for_json({
            "success": False,
            "error_type": "ChatError",
            "message": str(e)
        })))

# Serve Frontend static assets
frontend_dir = os.path.abspath("frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend index.html not found"}

@app.get("/login")
async def serve_login(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/")
    return FileResponse(os.path.join(frontend_dir, "login.html"))
