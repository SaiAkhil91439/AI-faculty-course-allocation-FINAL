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

def test_multiyear_courses_and_custom_ta_allocation():
    from backend.agent import FacultyAllocationAgent
    agent = FacultyAllocationAgent()
    res = agent.run_pipeline(
        pref_file_source="input/faculty_preferences.xlsx",
        exp_file_source="input/faculty_experience.xlsx",
        course_file_source="input/courses_multiyear.xlsx",
        ta_file_source="input/teaching_assistants.xlsx",
        num_sections=12,
        num_subjects=6,
        sections_per_faculty=3,
        max_subjects_per_faculty=1,
        tas_per_section=2,
        year_filter="All",
        output_excel_path="output/test_multiyear_ta_allocation.xlsx"
    )
    assert res["success"] is True
    assert res["summary"]["status"] in ("OPTIMAL", "FEASIBLE")
    assert res["summary"]["tas_per_section"] == 2
    assert res["summary"]["total_tas_allocated"] == 144
    assert os.path.exists("output/test_multiyear_ta_allocation.xlsx")

    # Test Chatbot Queries
    chat_ta = agent.handle_chat_query("Which teaching assistants are assigned?")
    assert chat_ta["success"] is True
    assert "Teaching Assistants Allocation Overview" in chat_ta["answer"]

    chat_yr = agent.handle_chat_query("What courses are in III Year?")
    assert chat_yr["success"] is True
    assert "III Year" in chat_yr["answer"]

def test_year_filter_optimization():
    from backend.agent import FacultyAllocationAgent
    agent = FacultyAllocationAgent()
    res = agent.run_pipeline(
        pref_file_source="input/faculty_preferences.xlsx",
        exp_file_source="input/faculty_experience.xlsx",
        course_file_source="input/courses_multiyear.xlsx",
        ta_file_source="input/teaching_assistants.xlsx",
        num_sections=12,
        num_subjects=5,
        sections_per_faculty=3,
        max_subjects_per_faculty=1,
        tas_per_section=2,
        year_filter="III Year",
        output_excel_path="output/test_iii_year_allocation.xlsx"
    )
    assert res["success"] is True
    assert all("III Year" in s for s in res["allocation_data"]["subjects"])
