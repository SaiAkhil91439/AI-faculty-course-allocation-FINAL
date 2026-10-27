# AI Faculty–Subject–Section Allocation Agent

An intelligent, web-based constraint optimization system built using **Python, Google OR-Tools, Pandas, OpenPyXL, FastAPI, and an AI Agent layer**.

The system dynamically assigns faculty members to subjects and section blocks based on:
1. Faculty subject preferences (40%)
2. Teaching experience per subject (30%)
3. Faculty skill levels (20%)
4. Qualification scores (10%)

---

## Key Features

- **Google OR-Tools Optimization Engine**: Formulates and solves an Integer Linear Programming (ILP) model to find the global maximum compatibility score.
- **Dynamic Configuration**: Supports arbitrary section sizes, subject counts, sections-per-faculty ratios, and customizable scoring weight sliders.
- **Strict Academic Rules**:
  - Rule 1: Every subject is taught in every section.
  - Rule 2: Exactly `num_sections / sections_per_faculty` faculty are assigned per subject.
  - Rule 3: Each selected faculty teaches a contiguous block of `sections_per_faculty` sections.
  - Rule 4: Faculty must be qualified for the subject.
  - Rule 5: Faculty load limit enforced (`max_subjects_per_faculty`).
- **Data Validation & Diagnostics**: Division remainder checks, duplicate Faculty ID detection, and detailed infeasibility diagnostics.
- **Multi-Sheet Excel Generator**: Outputs styled `faculty_allocation.xlsx` containing Matrix view, Detailed breakdown, and Summary sheets.
- **AI Agent Explanation**: Synthesizes human-readable rationales and execution traces for academic leadership.

---

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Sample Data (Optional)**:
   ```bash
   python input/sample_generator.py
   ```

3. **Start the Web Application**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

4. **Access the Web Dashboard**:
   Open browser at: `http://127.0.0.1:8000/`

---

## Project Structure

```text
faculty-allocation-agent/
├── backend/
│   ├── main.py             # FastAPI Server & API routes
│   ├── excel_reader.py     # Pandas Excel loader & normalizer
│   ├── validator.py        # Input schema & constraint validator
│   ├── scoring.py          # Multi-criteria scoring calculator
│   ├── optimizer.py        # Google OR-Tools CP-SAT solver
│   ├── excel_generator.py  # OpenPyXL multi-sheet Excel generator
│   └── agent.py            # AI Agent orchestration layer
│
├── frontend/
│   ├── index.html          # Web dashboard layout
│   ├── style.css           # Modern dark-mode styling
│   └── script.js           # Client-side UI & REST API controller
│
├── input/                  # Input Excel files storage
├── output/                 # Output generated Excel workbooks
├── requirements.txt        # Python dependency manifest
└── README.md               # Documentation
```
