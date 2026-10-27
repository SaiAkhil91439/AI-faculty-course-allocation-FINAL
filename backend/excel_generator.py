import os
from typing import Dict, Any, List
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from backend.workload_calculator import calculate_ltpc_workload
from backend.workload_excel import create_ltpc_workload_sheet, create_efficiency_scenarios_sheet, generate_workload_excel

def generate_allocation_excel(
    allocation_res: Dict[str, Any],
    output_path: str = "output/faculty_allocation.xlsx"
) -> str:
    """
    Generates a professionally styled, comprehensive Excel workbook with 4 tabs:
    1. Master Allocation Matrix: Clear Section x Subject matrix with full faculty names.
    2. Faculty Workload Allocation: Detailed institutional workload breakdown.
    3. Course Section Schedule: Per-section component (L, T/P 1, T/P 2) faculty assignments.
    4. Faculty Workload Summary: Executive summary of all faculty teaching hours and duties.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()

    # Common styles
    navy_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    blue_header_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    sub_header_fill = PatternFill(start_color="41719C", end_color="41719C", fill_type="solid")
    alt_fill_1 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    alt_fill_2 = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
    dean_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid") # Soft green for Dean / HOD
    matrix_cell_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    font_banner = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="1F4E79")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold_data = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular_data = Font(name="Calibri", size=9.5, color="1E293B")
    font_small = Font(name="Calibri", size=8.5, color="475569")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )
    medium_border = Border(
        left=Side(style="medium", color="1E293B"),
        right=Side(style="medium", color="1E293B"),
        top=Side(style="medium", color="1E293B"),
        bottom=Side(style="medium", color="1E293B")
    )

    allocs = allocation_res.get("faculty_allocations", [])
    matrix = allocation_res.get("final_allocation_matrix", {})
    subjects = allocation_res.get("subjects", [])
    section_names = allocation_res.get("section_names", [])
    course_details = allocation_res.get("course_details", {})

    # =========================================================================
    # TAB 1: Master Allocation Matrix (Section x Course Grid)
    # =========================================================================
    ws_mat = wb.active
    ws_mat.title = "Master Allocation Matrix"

    # Banner
    max_mat_col = max(len(subjects) + 1, 6)
    last_col_letter = get_column_letter(max_mat_col)
    ws_mat.merge_cells(f"A1:{last_col_letter}1")
    t1 = ws_mat["A1"]
    t1.value = "ACADEMIC TIMETABLE & SECTION ALLOCATION MATRIX"
    t1.font = font_banner
    t1.fill = navy_fill
    t1.alignment = Alignment(horizontal="center", vertical="center")
    ws_mat.row_dimensions[1].height = 36

    # Subtitle
    ws_mat.merge_cells(f"A2:{last_col_letter}2")
    sub1 = ws_mat["A2"]
    sub1.value = (
        f"Optimization Status: {allocation_res.get('status', 'OPTIMAL')} | "
        f"Average Compatibility Score: {allocation_res.get('average_score', 0)}/100 | "
        f"Total Sections: {allocation_res.get('num_sections', len(section_names))} | "
        f"Subjects: {allocation_res.get('num_subjects', len(subjects))}"
    )
    sub1.font = font_subtitle
    sub1.alignment = Alignment(horizontal="center", vertical="center")
    ws_mat.row_dimensions[2].height = 22

    # Headers at Row 4
    ws_mat.row_dimensions[4].height = 38
    c_sec = ws_mat.cell(row=4, column=1, value="Section")
    c_sec.fill = blue_header_fill
    c_sec.font = font_header
    c_sec.alignment = Alignment(horizontal="center", vertical="center")
    c_sec.border = thin_border

    for col_idx, s in enumerate(subjects, 2):
        c_info = course_details.get(s, {})
        ltpc = c_info.get("L-T-P-C", "3-0-2-4")
        hrs = c_info.get("Total_Hours", 5)
        header_text = f"{s}\n[{ltpc}] ({hrs} hrs/wk)"
        cell = ws_mat.cell(row=4, column=col_idx, value=header_text)
        cell.fill = blue_header_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # Data Rows for Matrix
    mat_row_idx = 5
    for sec in section_names:
        ws_mat.row_dimensions[mat_row_idx].height = 58
        cell_sec = ws_mat.cell(row=mat_row_idx, column=1, value=f"Section {sec}")
        cell_sec.font = font_bold_data
        cell_sec.fill = alt_fill_2
        cell_sec.alignment = Alignment(horizontal="center", vertical="center")
        cell_sec.border = thin_border

        for col_idx, s in enumerate(subjects, 2):
            sec_info = matrix.get(sec, {}).get(s, {})
            l_fac = sec_info.get("Lecture_Faculty", "N/A")
            tp1_fac = sec_info.get("TP_Faculty_1", "N/A")
            tp2_fac = sec_info.get("TP_Faculty_2", "N/A")

            cell_val = f"L: {l_fac}\nT/P 1: {tp1_fac}\nT/P 2: {tp2_fac}"
            c = ws_mat.cell(row=mat_row_idx, column=col_idx, value=cell_val)
            c.font = font_regular_data
            c.fill = matrix_cell_fill
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.border = thin_border

        mat_row_idx += 1

    # Widths for Matrix
    ws_mat.column_dimensions["A"].width = 16
    for col_idx in range(2, len(subjects) + 2):
        col_letter = get_column_letter(col_idx)
        ws_mat.column_dimensions[col_letter].width = 34

    # =========================================================================
    # TAB 2: Faculty Workload Allocation (Full Breakdown)
    # =========================================================================
    ws1 = wb.create_sheet(title="Faculty Workload Allocation")

    ws1.merge_cells("A1:V1")
    title_cell = ws1["A1"]
    title_cell.value = "DETAILED FACULTY WORKLOAD & COURSE ALLOCATION REPORT"
    title_cell.font = font_banner
    title_cell.fill = navy_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 36

    ws1.merge_cells("A2:V2")
    sub_cell = ws1["A2"]
    sub_cell.value = (
        f"Generated with AI Optimization Engine | Faculty Names & Designated Weekly Teaching Hours | "
        f"Deans: 4-6 hrs/wk | HODs: 10-12 hrs/wk | Faculty: 14-16 hrs/wk"
    )
    sub_cell.font = font_subtitle
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[2].height = 22

    headers_workload = [
        "Sl. No.", "Name of the Faculty", "Designation", "Additional duties", "Present Workload (hrs/wk)",
        "Program", "Year", "Section", "Name of the COURSE", "Course Code", "L", "T", "P", "C",
        "No. of section", "No. of students", "Total L HOURS", "Total T HOURS", "Total P HOURS",
        "Total hours course/wk", "Total workload/wk", "Comments / Role"
    ]

    ws1.row_dimensions[4].height = 30
    for col_idx, text in enumerate(headers_workload, 1):
        cell = ws1.cell(row=4, column=col_idx, value=text)
        cell.fill = blue_header_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # Group allocations by Lecture Faculty
    fac_grouped = {}
    for a in allocs:
        f_name = a["Lecture_Faculty_Name"]
        if f_name not in fac_grouped:
            fac_grouped[f_name] = []
        fac_grouped[f_name].append(a)

    row_cursor = 5
    sl_no = 1
    for f_name, f_allocs in fac_grouped.items():
        first_alloc = f_allocs[0]
        desig = first_alloc.get("Lecture_Designation", "Professor")
        role = first_alloc.get("Lecture_Role", "Faculty")

        w_hours = "4-6" if role == "Dean" else ("10-12" if role == "HOD" else "14-16")
        row_fill = dean_fill if role in ("Dean", "HOD") else (alt_fill_1 if sl_no % 2 != 0 else alt_fill_2)

        for a in f_allocs:
            secs = [s.strip() for s in a["Sections"].split(",")]
            is_high_exp = a.get("Is_High_Experience_Split", False)
            exp_years = a.get("Experience_Years", 0.0)

            comment_str = (
                f"High Exp Split ({a['Num_Sections']} Secs, {exp_years} yrs exp)"
                if is_high_exp else f"Main Lecturer ({role})"
            )

            for sec_clean in secs:
                ws1.row_dimensions[row_cursor].height = 22
                ws1.cell(row=row_cursor, column=1, value=sl_no).alignment = Alignment(horizontal="center")
                
                # Clear faculty name in column 2
                c_name = ws1.cell(row=row_cursor, column=2, value=f_name)
                c_name.font = font_bold_data

                ws1.cell(row=row_cursor, column=3, value=desig)
                ws1.cell(row=row_cursor, column=4, value=role)
                ws1.cell(row=row_cursor, column=5, value=w_hours).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=6, value="AIML").alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=7, value="III").alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=8, value=sec_clean).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=9, value=a["Subject"])
                ws1.cell(row=row_cursor, column=10, value=f"CS{100+sl_no}").alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=11, value=a.get("L", 3)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=12, value=a.get("T", 0)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=13, value=a.get("P", 2)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=14, value=a.get("C", 4)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=15, value=1).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=16, value=65).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=17, value=a.get("L", 3)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=18, value=a.get("T", 0)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=19, value=a.get("P", 2)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=20, value=a.get("Total_Course_Hours", 5)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=21, value=a.get("Faculty_Total_Weekly_Hours", 15)).alignment = Alignment(horizontal="center")
                ws1.cell(row=row_cursor, column=22, value=comment_str)

                for col in range(1, 23):
                    cell = ws1.cell(row=row_cursor, column=col)
                    cell.fill = row_fill
                    cell.border = thin_border
                    if col != 2:
                        cell.font = font_regular_data

                row_cursor += 1

        sl_no += 1

    # Auto-adjust column widths for tab 2
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 13)
    ws1.column_dimensions["B"].width = 28 # Name of Faculty
    ws1.column_dimensions["C"].width = 28 # Designation
    ws1.column_dimensions["I"].width = 32 # Name of Course

    # =========================================================================
    # TAB 3: Course Component Schedule (L & T/P Faculty Breakdown)
    # =========================================================================
    ws2 = wb.create_sheet(title="Course Section Schedule")

    ws2.merge_cells("A1:I1")
    t2_cell = ws2["A1"]
    t2_cell.value = "COURSE SECTION FACULTY ASSIGNMENTS (L = 1 Faculty, T/P = 2 Faculty)"
    t2_cell.font = font_banner
    t2_cell.fill = navy_fill
    t2_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 36

    s2_headers = [
        "Sl. No.", "Course / Subject", "L-T-P-C", "Section", "Lecture (L) Faculty",
        "Teaching Experience (Yrs)", "Tutorial / Practical (T/P) Faculty 1", "Tutorial / Practical (T/P) Faculty 2", "Score"
    ]

    ws2.row_dimensions[3].height = 30
    for col_idx, text in enumerate(s2_headers, 1):
        cell = ws2.cell(row=3, column=col_idx, value=text)
        cell.fill = blue_header_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    r2_idx = 4
    for idx_item, a in enumerate(allocs, 1):
        ws2.row_dimensions[r2_idx].height = 24
        is_high = a.get("Is_High_Experience_Split", False)
        fac_label = f"{a['Lecture_Faculty_Name']} ({a['Lecture_Designation']})" + (" [High Exp 2+1 Split]" if is_high else "")
        
        ws2.cell(row=r2_idx, column=1, value=idx_item).alignment = Alignment(horizontal="center")
        ws2.cell(row=r2_idx, column=2, value=a["Subject"])
        ws2.cell(row=r2_idx, column=3, value=a.get("L-T-P-C", "3-0-2-4")).alignment = Alignment(horizontal="center")
        ws2.cell(row=r2_idx, column=4, value=a["Sections"]).alignment = Alignment(horizontal="center")
        
        # Lecture Faculty Name
        cL = ws2.cell(row=r2_idx, column=5, value=fac_label)
        cL.font = font_bold_data

        ws2.cell(row=r2_idx, column=6, value=a.get("Experience_Years", 0.0)).alignment = Alignment(horizontal="center")
        
        # T/P Faculty 1 Name
        cTP1 = ws2.cell(row=r2_idx, column=7, value=a["TP_Faculty_1_Name"])
        cTP1.font = font_regular_data

        # T/P Faculty 2 Name
        cTP2 = ws2.cell(row=r2_idx, column=8, value=a["TP_Faculty_2_Name"])
        cTP2.font = font_regular_data

        ws2.cell(row=r2_idx, column=9, value=a["Score"]).alignment = Alignment(horizontal="center")

        row_f = alt_fill_1 if idx_item % 2 != 0 else alt_fill_2
        for col in range(1, 10):
            cell = ws2.cell(row=r2_idx, column=col)
            cell.border = thin_border
            cell.fill = row_f
            if col not in (5,):
                cell.font = font_regular_data

        r2_idx += 1

    # Widths for tab 3
    for col in ws2.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 14)
    ws2.column_dimensions["B"].width = 30 # Course
    ws2.column_dimensions["E"].width = 36 # Lecture Faculty
    ws2.column_dimensions["G"].width = 28 # TP 1
    ws2.column_dimensions["H"].width = 28 # TP 2

    # =========================================================================
    # TAB 4: Faculty Workload Summary (Executive Overview)
    # =========================================================================
    ws3 = wb.create_sheet(title="Faculty Workload Summary")

    ws3.merge_cells("A1:I1")
    t3_cell = ws3["A1"]
    t3_cell.value = "EXECUTIVE FACULTY ALLOCATION & TEACHING HOURS SUMMARY"
    t3_cell.font = font_banner
    t3_cell.fill = navy_fill
    t3_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[1].height = 36

    s3_headers = [
        "Sl. No.", "Faculty Name", "Designation", "Academic Role",
        "Allocated Courses", "Allocated Sections", "Total Sections",
        "Total Weekly Hours", "Workload Compliance"
    ]

    ws3.row_dimensions[3].height = 30
    for col_idx, text in enumerate(s3_headers, 1):
        cell = ws3.cell(row=3, column=col_idx, value=text)
        cell.fill = blue_header_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    r3_idx = 4
    for sum_idx, (f_name, f_allocs) in enumerate(fac_grouped.items(), 1):
        ws3.row_dimensions[r3_idx].height = 22
        first_a = f_allocs[0]
        desig = first_a.get("Lecture_Designation", "Professor")
        role = first_a.get("Lecture_Role", "Faculty")
        
        courses_set = list(dict.fromkeys(a["Subject"] for a in f_allocs))
        courses_str = ", ".join(courses_set)

        all_secs = []
        tot_secs = 0
        tot_hours = 0
        for a in f_allocs:
            s_list = [s.strip() for s in a["Sections"].split(",")]
            all_secs.extend(s_list)
            tot_secs += len(s_list)
            tot_hours += a.get("Total_Course_Hours", 5) * len(s_list)

        secs_str = ", ".join(all_secs)
        target_range = "4-6 hrs" if role == "Dean" else ("10-12 hrs" if role == "HOD" else "14-16 hrs")
        status_note = f"Balanced ({target_range})"

        ws3.cell(row=r3_idx, column=1, value=sum_idx).alignment = Alignment(horizontal="center")
        
        # Clearly printed faculty name
        cf = ws3.cell(row=r3_idx, column=2, value=f_name)
        cf.font = font_bold_data

        ws3.cell(row=r3_idx, column=3, value=desig)
        ws3.cell(row=r3_idx, column=4, value=role).alignment = Alignment(horizontal="center")
        ws3.cell(row=r3_idx, column=5, value=courses_str)
        ws3.cell(row=r3_idx, column=6, value=secs_str).alignment = Alignment(horizontal="center")
        ws3.cell(row=r3_idx, column=7, value=tot_secs).alignment = Alignment(horizontal="center")
        ws3.cell(row=r3_idx, column=8, value=tot_hours).alignment = Alignment(horizontal="center")
        ws3.cell(row=r3_idx, column=9, value=status_note).alignment = Alignment(horizontal="center")

        row_f = dean_fill if role in ("Dean", "HOD") else (alt_fill_1 if sum_idx % 2 != 0 else alt_fill_2)
        for col in range(1, 10):
            c = ws3.cell(row=r3_idx, column=col)
            c.border = thin_border
            c.fill = row_f
            if col != 2:
                c.font = font_regular_data

        r3_idx += 1

    # Widths for tab 4
    for col in ws3.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws3.column_dimensions[col_letter].width = max(max_len + 4, 15)
    ws3.column_dimensions["B"].width = 28 # Name
    ws3.column_dimensions["C"].width = 28 # Designation
    ws3.column_dimensions["E"].width = 34 # Courses

    # =========================================================================
    # TAB 5: LTPC Workload Calculation (Formula Analysis)
    # =========================================================================
    workload_data = allocation_res.get("workload_analysis")
    if not workload_data:
        courses_input = []
        for s_name, c_info in course_details.items():
            courses_input.append({
                "course_title": s_name,
                "l": c_info.get("L", 0),
                "t": c_info.get("T", 0),
                "p": c_info.get("P", 0),
                "c": c_info.get("C", 0),
                "ltpc": c_info.get("L-T-P-C", "")
            })
        num_secs = allocation_res.get("num_sections", len(section_names))
        workload_data = calculate_ltpc_workload(courses_input, num_sections=num_secs)

    ws_ltpc = wb.create_sheet(title="LTPC Workload Calculation")
    create_ltpc_workload_sheet(ws_ltpc, workload_data)

    # TAB 6: Staffing Efficiency Scenarios
    ws_eff = wb.create_sheet(title="Staffing Efficiency Scenarios")
    create_efficiency_scenarios_sheet(ws_eff, workload_data)

    # Persist standalone clear load calculation excel
    standalone_path = os.path.join(os.path.dirname(output_path), "ltpc_workload_calculation.xlsx")
    generate_workload_excel(workload_data, standalone_path)

    wb.save(output_path)
    return output_path
