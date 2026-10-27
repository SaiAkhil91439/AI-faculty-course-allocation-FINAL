import os
from typing import Dict, Any, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_ltpc_workload_sheet(ws: openpyxl.worksheet.worksheet.Worksheet, workload_data: Dict[str, Any]):
    """
    Builds the complete, professionally formatted LTPC Workload Calculation report
    inside any given openpyxl worksheet.
    """
    # Color palette
    navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    indigo_fill = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid")
    blue_header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    teal_sub_fill = PatternFill(start_color="0D9488", end_color="0D9488", fill_type="solid")
    kpi_card_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    kpi_accent_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
    alt_fill_1 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    alt_fill_2 = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    total_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Warm amber for totals
    dept_total_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Soft green for dept total

    # Fonts
    font_banner = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="FFFFFF")
    font_sec_heading = Font(name="Calibri", size=12, bold=True, color="1E3A8A")
    font_tbl_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_kpi_label = Font(name="Calibri", size=9, bold=False, color="475569")
    font_kpi_val = Font(name="Calibri", size=13, bold=True, color="0F172A")
    font_kpi_val_accent = Font(name="Calibri", size=14, bold=True, color="1E40AF")
    font_kpi_val_green = Font(name="Calibri", size=14, bold=True, color="047857")
    font_bold_data = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular_data = Font(name="Calibri", size=9.5, color="1E293B")
    font_note = Font(name="Calibri", size=9, italic=True, color="475569")

    # Borders
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )
    thick_bottom = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="medium", color="0F172A")
    )
    double_bottom = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="double", color="0F172A")
    )

    num_sections = workload_data.get("num_sections", 12)
    l_fac = workload_data.get("l_faculty_multiplier", 1)
    t_fac = workload_data.get("t_faculty_multiplier", 3)
    p_fac = workload_data.get("p_faculty_multiplier", 3)
    courses = workload_data.get("courses", [])

    # 1. Main Banner
    last_col = "S"
    ws.merge_cells(f"A1:{last_col}1")
    b1 = ws["A1"]
    b1.value = "ACADEMIC CURRICULUM LTPC WORKLOAD & FACULTY REQUIREMENT ANALYSIS"
    b1.font = font_banner
    b1.fill = navy_fill
    b1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    ws.merge_cells(f"A2:{last_col}2")
    b2 = ws["A2"]
    b2.value = (
        f"Institutional Standard: L Hour = {l_fac} Faculty/Section | "
        f"T Hour = {t_fac} Faculty/Section | "
        f"P Hour = {p_fac} Faculty/Section | "
        f"Total Sections: {num_sections} | "
        f"Faculty Capacity Baseline: {workload_data.get('avg_faculty_capacity_hours', 15)} hrs/week"
    )
    b2.font = font_subtitle
    b2.fill = indigo_fill
    b2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 24

    # 2. Executive KPI Cards (Row 4 & 5)
    # KPI 1: Total L Hours & Workload
    ws.merge_cells("A4:C4")
    c = ws["A4"]
    c.value = "LECTURE (L) LOAD"
    c.font = font_kpi_label
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    ws.merge_cells("A5:C5")
    c = ws["A5"]
    c.value = f"{workload_data.get('total_l_hours', 0)} hrs × {l_fac} fac = {workload_data.get('dept_l_load', 0)} dept hrs"
    c.font = font_kpi_val_accent
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_accent_fill

    # KPI 2: Total T Hours & Workload
    ws.merge_cells("D4:F4")
    c = ws["D4"]
    c.value = "TUTORIAL (T) LOAD"
    c.font = font_kpi_label
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    ws.merge_cells("D5:F5")
    c = ws["D5"]
    c.value = f"{workload_data.get('total_t_hours', 0)} hrs × {t_fac} fac = {workload_data.get('dept_t_load', 0)} dept hrs"
    c.font = font_kpi_val_accent
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_accent_fill

    # KPI 3: Total P Hours & Workload
    ws.merge_cells("G4:I4")
    c = ws["G4"]
    c.value = "PRACTICAL / LAB (P) LOAD"
    c.font = font_kpi_label
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    ws.merge_cells("G5:I5")
    c = ws["G5"]
    c.value = f"{workload_data.get('total_p_hours', 0)} hrs × {p_fac} fac = {workload_data.get('dept_p_load', 0)} dept hrs"
    c.font = font_kpi_val_accent
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_accent_fill

    # KPI 4: Workload Per Section
    ws.merge_cells("J4:L4")
    c = ws["J4"]
    c.value = "WORKLOAD PER SECTION"
    c.font = font_kpi_label
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    ws.merge_cells("J5:L5")
    c = ws["J5"]
    c.value = f"{workload_data.get('section_total_workload', 0)} hrs / section / wk"
    c.font = font_kpi_val
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    # KPI 5: Total Department Workload
    ws.merge_cells("M4:P4")
    c = ws["M4"]
    c.value = "TOTAL DEPARTMENT WORKLOAD"
    c.font = font_kpi_label
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    ws.merge_cells("M5:P5")
    c = ws["M5"]
    c.value = f"{workload_data.get('dept_total_workload', 0)} FACULTY-HOURS / WK"
    c.font = font_kpi_val_green
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = dept_total_fill

    # KPI 6: Estimated Faculty Required
    ws.merge_cells("Q4:S4")
    c = ws["Q4"]
    c.value = "ESTIMATED FACULTY REQUIRED"
    c.font = font_kpi_label
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = kpi_card_fill

    ws.merge_cells("Q5:S5")
    c = ws["Q5"]
    c.value = f"~{workload_data.get('estimated_faculty_required', 0)} Faculty Members"
    c.font = font_kpi_val_green
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = dept_total_fill

    for r in (4, 5):
        ws.row_dimensions[r].height = 24
        for col_i in range(1, 20):
            ws.cell(row=r, column=col_i).border = thin_border

    # 3. Section Heading
    ws.cell(row=7, column=1, value="TABLE 1: COURSE-BY-COURSE LTPC WORKLOAD BREAKDOWN").font = font_sec_heading

    # 4. Table Headers (Row 8 & 9)
    headers = [
        "Sl. No.", "Course Title", "L", "T", "P", "C", "Contact Hours",
        "L Faculty", "T Faculty", "P Faculty",
        "Sec L Load (hrs)", "Sec T Load (hrs)", "Sec P Load (hrs)", "Total Sec Workload (hrs)",
        "Dept L Load (hrs)", "Dept T Load (hrs)", "Dept P Load (hrs)", "Total Dept Workload (hrs)", "% Share"
    ]

    ws.row_dimensions[8].height = 32
    for col_idx, h_text in enumerate(headers, 1):
        cell = ws.cell(row=8, column=col_idx, value=h_text)
        cell.fill = blue_header_fill
        cell.font = font_tbl_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # 5. Course Rows
    r_idx = 9
    for c_item in courses:
        ws.row_dimensions[r_idx].height = 22
        fill = alt_fill_1 if c_item["sl_no"] % 2 != 0 else alt_fill_2

        ws.cell(row=r_idx, column=1, value=c_item["sl_no"]).alignment = Alignment(horizontal="center")
        
        c_name = ws.cell(row=r_idx, column=2, value=c_item["course_title"])
        c_name.font = font_bold_data

        ws.cell(row=r_idx, column=3, value=c_item["l"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=4, value=c_item["t"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=5, value=c_item["p"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=6, value=c_item["c"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=7, value=c_item["contact_hours"]).alignment = Alignment(horizontal="center")

        ws.cell(row=r_idx, column=8, value=c_item["l_faculty"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=9, value=c_item["t_faculty"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=10, value=c_item["p_faculty"]).alignment = Alignment(horizontal="center")

        ws.cell(row=r_idx, column=11, value=c_item["sec_l_load"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=12, value=c_item["sec_t_load"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=13, value=c_item["sec_p_load"]).alignment = Alignment(horizontal="center")
        
        c_sec_tot = ws.cell(row=r_idx, column=14, value=c_item["sec_total_workload"])
        c_sec_tot.font = font_bold_data
        c_sec_tot.alignment = Alignment(horizontal="center")

        ws.cell(row=r_idx, column=15, value=c_item["dept_l_load"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=16, value=c_item["dept_t_load"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=17, value=c_item["dept_p_load"]).alignment = Alignment(horizontal="center")

        c_dept_tot = ws.cell(row=r_idx, column=18, value=c_item["dept_total_workload"])
        c_dept_tot.font = font_bold_data
        c_dept_tot.alignment = Alignment(horizontal="center")

        ws.cell(row=r_idx, column=19, value=f"{c_item.get('dept_share_pct', 0)}%").alignment = Alignment(horizontal="center")

        for col_j in range(1, 20):
            c_cell = ws.cell(row=r_idx, column=col_j)
            c_cell.fill = fill
            c_cell.border = thin_border
            if col_j not in (2, 14, 18):
                c_cell.font = font_regular_data

        r_idx += 1

    # 6. Total Summary Row
    ws.row_dimensions[r_idx].height = 26
    ws.cell(row=r_idx, column=1, value="").fill = total_fill
    c_tot_label = ws.cell(row=r_idx, column=2, value="TOTAL CURRICULUM WORKLOAD")
    c_tot_label.font = font_bold_data
    c_tot_label.fill = total_fill

    ws.cell(row=r_idx, column=3, value=workload_data.get("total_l_hours", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=4, value=workload_data.get("total_t_hours", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=5, value=workload_data.get("total_p_hours", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=6, value=workload_data.get("total_credits", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=7, value=workload_data.get("total_contact_hours", 0)).alignment = Alignment(horizontal="center")

    ws.cell(row=r_idx, column=8, value=l_fac).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=9, value=t_fac).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=10, value=p_fac).alignment = Alignment(horizontal="center")

    ws.cell(row=r_idx, column=11, value=workload_data.get("section_l_load", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=12, value=workload_data.get("section_t_load", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=13, value=workload_data.get("section_p_load", 0)).alignment = Alignment(horizontal="center")

    c_s_tot = ws.cell(row=r_idx, column=14, value=workload_data.get("section_total_workload", 0))
    c_s_tot.font = font_kpi_val_accent
    c_s_tot.alignment = Alignment(horizontal="center")

    ws.cell(row=r_idx, column=15, value=workload_data.get("dept_l_load", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=16, value=workload_data.get("dept_t_load", 0)).alignment = Alignment(horizontal="center")
    ws.cell(row=r_idx, column=17, value=workload_data.get("dept_p_load", 0)).alignment = Alignment(horizontal="center")

    c_d_tot = ws.cell(row=r_idx, column=18, value=workload_data.get("dept_total_workload", 0))
    c_d_tot.font = font_kpi_val_green
    c_d_tot.alignment = Alignment(horizontal="center")

    ws.cell(row=r_idx, column=19, value="100.0%").alignment = Alignment(horizontal="center")

    for col_j in range(1, 20):
        tot_c = ws.cell(row=r_idx, column=col_j)
        tot_c.fill = total_fill
        tot_c.border = double_bottom
        tot_c.font = font_bold_data

    # 7. Mathematical Formula Reference Box (Row r_idx + 2)
    f_row = r_idx + 2
    ws.merge_cells(f"A{f_row}:S{f_row}")
    f_title = ws[f"A{f_row}"]
    f_title.value = "MATHEMATICAL FORMULAS & WORKLOAD GOVERNING PRINCIPLES"
    f_title.font = font_sec_heading
    ws.row_dimensions[f_row].height = 24

    formulas_text = [
        ("Section Workload Formula", workload_data.get("formula_section", "")),
        (f"Department Workload Formula ({num_sections} Sections)", workload_data.get("formula_dept", "")),
        ("Institutional Multiplier Rule", f"Each Lecture (L) hour has 1 faculty. Each Tutorial (T) hour has {t_fac} faculty allotted. Each Practical (P) hour has {p_fac} faculty allotted per section."),
        ("Faculty Count Requirement", f"Total Department Workload ({workload_data.get('dept_total_workload', 0)} hrs) ÷ Standard Capacity ({workload_data.get('avg_faculty_capacity_hours', 15)} hrs/fac) = ~{workload_data.get('estimated_faculty_required', 0)} Faculty Members needed.")
    ]

    for offset, (lbl, val_str) in enumerate(formulas_text, 1):
        cur_r = f_row + offset
        ws.row_dimensions[cur_r].height = 22
        ws.merge_cells(f"A{cur_r}:D{cur_r}")
        ws.merge_cells(f"E{cur_r}:S{cur_r}")

        l_c = ws[f"A{cur_r}"]
        l_c.value = f"• {lbl}:"
        l_c.font = font_bold_data
        l_c.fill = kpi_card_fill
        l_c.alignment = Alignment(horizontal="left", vertical="center")

        v_c = ws[f"E{cur_r}"]
        v_c.value = str(val_str)
        v_c.font = font_regular_data
        v_c.fill = kpi_card_fill
        v_c.alignment = Alignment(horizontal="left", vertical="center")

    # 8. Workload Efficiency & Capacity Analysis Section (Row cur_r + 2)
    eff_row = cur_r + 2
    ws.merge_cells(f"A{eff_row}:S{eff_row}")
    eff_title = ws[f"A{eff_row}"]
    eff_title.value = "WORKLOAD EFFICIENCY & CAPACITY UTILIZATION SUMMARY"
    eff_title.font = font_sec_heading
    ws.row_dimensions[eff_row].height = 24

    eff_metrics = [
        ("Workload Efficiency Score", f"{workload_data.get('workload_efficiency_score', 0)}% ({workload_data.get('efficiency_status', 'N/A')})"),
        ("Available Faculty Capacity", f"{workload_data.get('num_available_faculty', 34)} faculty × {workload_data.get('avg_faculty_capacity_hours', 15)}h = {workload_data.get('available_capacity_hours', 0)} faculty-hours available"),
        ("Capacity Utilization Rate", f"{workload_data.get('capacity_utilization_pct', 0)}% of total department capacity demand"),
        ("Faculty Headcount Balance", f"Needed: {workload_data.get('estimated_faculty_required', 0)} | Available: {workload_data.get('num_available_faculty', 34)} | Deficit: -{workload_data.get('faculty_deficit', 0)} faculty")
    ]

    for offset, (lbl, val_str) in enumerate(eff_metrics, 1):
        cur_e = eff_row + offset
        ws.row_dimensions[cur_e].height = 22
        ws.merge_cells(f"A{cur_e}:D{cur_e}")
        ws.merge_cells(f"E{cur_e}:S{cur_e}")

        l_c = ws[f"A{cur_e}"]
        l_c.value = f"• {lbl}:"
        l_c.font = font_bold_data
        l_c.fill = kpi_card_fill
        l_c.alignment = Alignment(horizontal="left", vertical="center")

        v_c = ws[f"E{cur_e}"]
        v_c.value = str(val_str)
        v_c.font = font_regular_data
        v_c.fill = kpi_card_fill
        v_c.alignment = Alignment(horizontal="left", vertical="center")

        for col_j in range(1, 20):
            ws.cell(row=cur_e, column=col_j).border = thin_border

    # Adjust Column Widths
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 38
    ws.column_dimensions["C"].width = 8
    ws.column_dimensions["D"].width = 8
    ws.column_dimensions["E"].width = 8
    ws.column_dimensions["F"].width = 8
    ws.column_dimensions["G"].width = 14
    ws.column_dimensions["H"].width = 12
    ws.column_dimensions["I"].width = 12
    ws.column_dimensions["J"].width = 12
    ws.column_dimensions["K"].width = 16
    ws.column_dimensions["L"].width = 16
    ws.column_dimensions["M"].width = 16
    ws.column_dimensions["N"].width = 22
    ws.column_dimensions["O"].width = 17
    ws.column_dimensions["P"].width = 17
    ws.column_dimensions["Q"].width = 17
    ws.column_dimensions["R"].width = 24
    ws.column_dimensions["S"].width = 12

def create_section_matrix_sheet(ws: openpyxl.worksheet.worksheet.Worksheet, workload_data: Dict[str, Any]):
    """Creates a secondary tab showing the Section-by-Section load distribution."""
    navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    blue_header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    alt_fill_1 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    alt_fill_2 = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    total_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

    font_banner = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_tbl_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold_data = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular_data = Font(name="Calibri", size=9.5, color="1E293B")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    ws.merge_cells("A1:G1")
    b1 = ws["A1"]
    b1.value = "SECTION-BY-SECTION WORKLOAD LOAD DISTRIBUTION MATRIX"
    b1.font = font_banner
    b1.fill = navy_fill
    b1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 34

    headers = [
        "Sl. No.", "Section Name", "Active Courses",
        "Section L Hours", "Section T Hours", "Section P Hours",
        "Total Weekly Workload (hrs)", "Cumulative Department Workload (hrs)"
    ]

    ws.row_dimensions[3].height = 30
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.fill = blue_header_fill
        cell.font = font_tbl_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    sections = workload_data.get("sections", [])
    r_idx = 4
    for idx, s in enumerate(sections, 1):
        ws.row_dimensions[r_idx].height = 22
        fill = alt_fill_1 if idx % 2 != 0 else alt_fill_2

        ws.cell(row=r_idx, column=1, value=idx).alignment = Alignment(horizontal="center")
        
        c_sec = ws.cell(row=r_idx, column=2, value=s["section_name"])
        c_sec.font = font_bold_data
        c_sec.alignment = Alignment(horizontal="center")

        ws.cell(row=r_idx, column=3, value=s["num_courses"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=4, value=s["l_hours"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=5, value=s["t_hours"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=6, value=s["p_hours"]).alignment = Alignment(horizontal="center")

        c_tot = ws.cell(row=r_idx, column=7, value=s["section_total_workload"])
        c_tot.font = font_bold_data
        c_tot.alignment = Alignment(horizontal="center")

        c_cum = ws.cell(row=r_idx, column=8, value=s["cumulative_dept_workload"])
        c_cum.font = font_bold_data
        c_cum.alignment = Alignment(horizontal="center")

        for col_j in range(1, 9):
            cell = ws.cell(row=r_idx, column=col_j)
            cell.fill = fill
            cell.border = thin_border
            if col_j not in (2, 7, 8):
                cell.font = font_regular_data

        r_idx += 1

    # Column Widths
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 18
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 28
    ws.column_dimensions["H"].width = 34

def create_efficiency_scenarios_sheet(ws: openpyxl.worksheet.worksheet.Worksheet, workload_data: Dict[str, Any]):
    """Creates a dedicated worksheet comparing Staffing Efficiency Models and Optimization Scenarios."""
    navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    indigo_fill = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid")
    blue_header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    alt_fill_1 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    alt_fill_2 = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    highlight_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
    success_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

    font_banner = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_tbl_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold_data = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular_data = Font(name="Calibri", size=9.5, color="1E293B")
    font_sec_heading = Font(name="Calibri", size=12, bold=True, color="1E3A8A")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    ws.merge_cells("A1:K1")
    b1 = ws["A1"]
    b1.value = "FACULTY WORKLOAD EFFICIENCY & STAFFING CAPACITY OPTIMIZATION"
    b1.font = font_banner
    b1.fill = navy_fill
    b1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 34

    headers = [
        "Scenario / Staffing Model", "L Fac", "T Fac", "P Fac",
        "Section Load (hrs)", "Dept Demand (hrs)", "Faculty Required",
        "Available Faculty", "Deficit / Surplus", "Hours Saved (hrs)", "Load Reduction %"
    ]

    ws.row_dimensions[3].height = 28
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.fill = blue_header_fill
        cell.font = font_tbl_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    scenarios = workload_data.get("efficiency_scenarios", [])
    avail_fac = workload_data.get("num_available_faculty", 34)
    r_idx = 4
    for sc in scenarios:
        ws.row_dimensions[r_idx].height = 24
        fill = highlight_fill if sc.get("is_active") else (alt_fill_1 if r_idx % 2 == 0 else alt_fill_2)
        
        ws.cell(row=r_idx, column=1, value=sc["name"] + (" (CURRENT)" if sc.get("is_active") else "")).font = font_bold_data
        ws.cell(row=r_idx, column=2, value=sc["l_faculty"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=3, value=sc["t_faculty"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=4, value=sc["p_faculty"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=5, value=f"{sc['section_workload']}h").alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=6, value=f"{sc['dept_workload']}h").alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=7, value=sc["faculty_required"]).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=8, value=avail_fac).alignment = Alignment(horizontal="center")
        
        diff = round(avail_fac - sc["faculty_required"], 1)
        diff_str = f"+{diff} surplus" if diff >= 0 else f"{diff} deficit"
        c_diff = ws.cell(row=r_idx, column=9, value=diff_str)
        c_diff.alignment = Alignment(horizontal="center")
        c_diff.font = font_bold_data

        c_saved = ws.cell(row=r_idx, column=10, value=f"{sc['hours_saved']}h")
        c_saved.alignment = Alignment(horizontal="center")
        if sc['hours_saved'] > 0:
            c_saved.fill = success_fill

        ws.cell(row=r_idx, column=11, value=f"{sc['savings_percent']}%").alignment = Alignment(horizontal="center")

        for col_j in range(1, 12):
            cell = ws.cell(row=r_idx, column=col_j)
            if col_j != 10 or sc['hours_saved'] == 0:
                cell.fill = fill
            cell.border = thin_border
            if col_j not in (1, 9):
                cell.font = font_regular_data

        r_idx += 1

    # Designation-Based Staffing Mix Table
    d_row = r_idx + 2
    ws.merge_cells(f"A{d_row}:F{d_row}")
    ws[f"A{d_row}"].value = "RECOMMENDED FACULTY DESIGNATION WORKLOAD ABSORPTION"
    ws[f"A{d_row}"].font = font_sec_heading
    ws.row_dimensions[d_row].height = 24

    d_headers = ["Faculty Designation", "Standard Load Limit (hrs/wk)", "Recommended Headcount", "Capacity Delivered (hrs)"]
    ws.row_dimensions[d_row + 1].height = 26
    for col_idx, dh in enumerate(d_headers, 1):
        cell = ws.cell(row=d_row + 1, column=col_idx, value=dh)
        cell.fill = indigo_fill
        cell.font = font_tbl_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    desig_mix = workload_data.get("designation_mix", [])
    dr_idx = d_row + 2
    for dm in desig_mix:
        ws.row_dimensions[dr_idx].height = 22
        ws.cell(row=dr_idx, column=1, value=dm["designation"]).font = font_bold_data
        ws.cell(row=dr_idx, column=2, value=f"{dm['weekly_target_load']} hrs/wk").alignment = Alignment(horizontal="center")
        ws.cell(row=dr_idx, column=3, value=f"{dm['recommended_count']} faculty").alignment = Alignment(horizontal="center")
        ws.cell(row=dr_idx, column=4, value=f"{dm['capacity_hours']} hrs").alignment = Alignment(horizontal="center")

        for col_j in range(1, 5):
            c = ws.cell(row=dr_idx, column=col_j)
            c.border = thin_border
            c.fill = alt_fill_1 if dr_idx % 2 == 0 else alt_fill_2
        dr_idx += 1

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 18
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 18
    ws.column_dimensions["H"].width = 18
    ws.column_dimensions["I"].width = 20
    ws.column_dimensions["J"].width = 18
    ws.column_dimensions["K"].width = 18

def generate_workload_excel(
    workload_data: Dict[str, Any],
    output_path: str = "output/ltpc_workload_calculation.xlsx"
) -> str:
    """
    Generates a standalone, beautifully styled Excel workbook containing the complete
    clear workload calculation results for the user to download.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()

    # Sheet 1: LTPC Workload Calculation
    ws1 = wb.active
    ws1.title = "LTPC Workload Calculation"
    create_ltpc_workload_sheet(ws1, workload_data)

    # Sheet 2: Section Load Matrix
    ws2 = wb.create_sheet(title="Section Load Breakdown")
    create_section_matrix_sheet(ws2, workload_data)

    # Sheet 3: Staffing Efficiency Scenarios
    ws3 = wb.create_sheet(title="Staffing Efficiency Scenarios")
    create_efficiency_scenarios_sheet(ws3, workload_data)

    wb.save(output_path)
    return output_path
