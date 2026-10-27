import os
import pytest
from starlette.testclient import TestClient

from backend.excel_reader import load_all_excel_files
from backend.validator import validate_inputs, AllocationValidationError
from backend.scoring import calculate_compatibility_scores
from backend.workload_calculator import calculate_ltpc_workload, DEFAULT_PROMPT_COURSES
from backend.workload_excel import generate_workload_excel
from backend.main import app

def test_load_all_excel_files():
    pref_df, exp_df, course_df = load_all_excel_files(
        "input/faculty_sample_combined.xlsx",
        "input/faculty_sample_combined.xlsx",
        "input/course_details.xlsx"
    )
    assert not pref_df.empty, "pref_df should not be empty"
    assert not exp_df.empty, "exp_df should not be empty"
    assert not course_df.empty, "course_df should not be empty"
    assert "Faculty_ID" in pref_df.columns
    assert "Subject" in exp_df.columns

def test_validator_success():
    pref_df, exp_df, course_df = load_all_excel_files(
        "input/faculty_sample_combined.xlsx",
        "input/faculty_sample_combined.xlsx",
        "input/course_details.xlsx"
    )
    res = validate_inputs(
        pref_df=pref_df,
        exp_df=exp_df,
        num_sections=12,
        num_subjects=6,
        sections_per_faculty=3,
        max_subjects_per_faculty=1,
        course_df=course_df,
        dean_max_sections=2,
        hod_max_sections=3,
        high_exp_threshold=8.0
    )
    assert res["valid"] is True
    assert res["num_sections"] == 12
    assert res["faculty_required_per_subject"] == 4

def test_validator_error_on_indivisible_sections():
    pref_df, exp_df, course_df = load_all_excel_files(
        "input/faculty_sample_combined.xlsx",
        "input/faculty_sample_combined.xlsx",
        "input/course_details.xlsx"
    )
    with pytest.raises(AllocationValidationError):
        validate_inputs(
            pref_df=pref_df,
            exp_df=exp_df,
            num_sections=10,
            num_subjects=6,
            sections_per_faculty=3,
            max_subjects_per_faculty=1,
            course_df=course_df
        )

def test_scoring():
    pref_df, exp_df, _ = load_all_excel_files(
        "input/faculty_sample_combined.xlsx",
        "input/faculty_sample_combined.xlsx",
        "input/course_details.xlsx"
    )
    scores_res = calculate_compatibility_scores(pref_df, exp_df)
    assert "scores_df" in scores_res
    assert "score_matrix" in scores_res
    assert len(scores_res["scores_df"]) > 0

def test_workload_calculator_and_excel():
    wl = calculate_ltpc_workload(DEFAULT_PROMPT_COURSES, num_sections=12)
    assert wl["total_courses"] == len(DEFAULT_PROMPT_COURSES)
    assert wl["num_sections"] == 12
    assert wl["dept_total_workload"] > 0

    excel_path = "output/test_ltpc_workload.xlsx"
    out = generate_workload_excel(wl, excel_path)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0

def test_optimizer_and_agent_pipeline():
    from backend.agent import FacultyAllocationAgent
    agent = FacultyAllocationAgent()
    res = agent.run_pipeline(
        pref_file_source="input/faculty_sample_combined.xlsx",
        exp_file_source="input/faculty_sample_combined.xlsx",
        course_file_source="input/course_details.xlsx",
        num_sections=12,
        num_subjects=6,
        sections_per_faculty=3,
        max_subjects_per_faculty=1,
        output_excel_path="output/test_faculty_allocation.xlsx"
    )
    assert res["success"] is True
    assert res["summary"]["status"] in ("OPTIMAL", "FEASIBLE")
    assert os.path.exists(res["summary"]["excel_file"])

def test_fastapi_endpoints():
    client = TestClient(app)
    
    # 1. Unauthenticated checks
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/calculate-ltpc-workload", json={}).status_code == 401

    # 2. Login
    login_resp = client.post("/api/login", data={"username": "admin", "password": "admin123"}, headers={"Accept": "application/json"})
    assert login_resp.status_code == 200
    assert login_resp.json()["success"] is True

    # 3. Authenticated session
    auth_resp = client.get("/api/auth/me")
    assert auth_resp.status_code == 200
    assert auth_resp.json()["authenticated"] is True

    # 4. Sample data zip
    sample_resp = client.post("/api/sample-data")
    assert sample_resp.status_code == 200
    assert len(sample_resp.content) > 1000

    # 5. Validate endpoint
    val_resp = client.post("/api/validate", data={
        "num_sections": 12,
        "num_subjects": 6,
        "sections_per_faculty": 3,
        "max_subjects_per_faculty": 1,
        "dean_max_sections": 2,
        "hod_max_sections": 3,
        "high_exp_threshold": 8.0
    })
    assert val_resp.status_code == 200
    assert val_resp.json()["success"] is True

    # 6. Workload calculation endpoint
    wl_resp = client.post("/api/calculate-ltpc-workload", json={"num_sections": 12})
    assert wl_resp.status_code == 200
    assert wl_resp.json()["success"] is True

    # 7. Allocate endpoint
    alloc_resp = client.post("/api/allocate", data={
        "num_sections": 12,
        "num_subjects": 6,
        "sections_per_faculty": 3,
        "max_subjects_per_faculty": 1,
        "dean_max_sections": 2,
        "hod_max_sections": 3,
        "high_exp_threshold": 8.0,
        "weight_pref": 0.40,
        "weight_exp": 0.30,
        "weight_skill": 0.20,
        "weight_qual": 0.10
    })
    assert alloc_resp.status_code == 200
    assert alloc_resp.json()["success"] is True

    # 8. Chat endpoint
    chat_resp = client.post("/api/chat", json={"question": "Show faculty teaching > 15 hours/week"})
    assert chat_resp.status_code == 200
    assert chat_resp.json()["success"] is True

    # 8b. Preview data endpoint
    preview_resp = client.get("/api/preview-data")
    assert preview_resp.status_code == 200
    assert preview_resp.json()["success"] is True
    assert preview_resp.json()["faculty"]["total_count"] > 0
    assert preview_resp.json()["courses"]["total_count"] > 0

    # 9. Download endpoints
    down_alloc = client.get("/api/download/faculty_allocation.xlsx")
    assert down_alloc.status_code == 200
    assert len(down_alloc.content) > 1000

    down_wl = client.get("/api/download/ltpc-workload.xlsx")
    assert down_wl.status_code == 200
    assert len(down_wl.content) > 1000

    # 10. Logout
    logout_resp = client.post("/api/logout")
    assert logout_resp.status_code == 200
    assert client.get("/api/auth/me").status_code == 401
