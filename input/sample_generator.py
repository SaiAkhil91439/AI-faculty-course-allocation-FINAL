import os
import pandas as pd

def generate_sample_files(output_dir: str = "input"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Course Details Dataset with exact 7 courses from the prompt image
    course_sample_data = [
        {"Course Title": "Advanced Linear Algebra and Optimization", "L": 2, "T": 2, "P": 2, "C": 4, "L-T-P-C": "2-2-2-4"},
        {"Course Title": "Full Stack AI Application Development", "L": 0, "T": 2, "P": 2, "C": 3, "L-T-P-C": "0-2-2-3"},
        {"Course Title": "Open Elective - 1", "L": 2, "T": 2, "P": 0, "C": 3, "L-T-P-C": "2-2-0-3"},
        {"Course Title": "Algorithm Design and Analysis", "L": 2, "T": 2, "P": 2, "C": 4, "L-T-P-C": "2-2-2-4"},
        {"Course Title": "Machine Learning", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4"},
        {"Course Title": "Operating Systems", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3"},
        {"Course Title": "Digital Logic and Computer Organization", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3"}
    ]
    course_df = pd.DataFrame(course_sample_data)
    course_path = os.path.join(output_dir, "course_details.xlsx")
    course_df.to_excel(course_path, index=False)

    # 2. Combined Wide Format Excel Dataset matching user's input specification
    wide_sample_data = [
        {
            "Faculty Name": "Dr. M. Venkateswarlu",
            "Designation": "Professor & Dean",
            "Additional Duties": "Dean",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Machine Learning", "Experience in Course 1": 12,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 10,
            "Course Preference 3": "Advanced Linear Algebra and Optimization", "Experience in Course 3": 8,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 5,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 3
        },
        {
            "Faculty Name": "Dr. M. Sreenivasa Rao",
            "Designation": "Professor & HOD",
            "Additional Duties": "HOD",
            "Qualification": "PhD AI",
            "Course Preference 1": "Algorithm Design and Analysis", "Experience in Course 1": 11,
            "Course Preference 2": "Machine Learning", "Experience in Course 2": 9,
            "Course Preference 3": "Full Stack AI Application Development", "Experience in Course 3": 7,
            "Course Preference 4": "Advanced Linear Algebra and Optimization", "Experience in Course 4": 6,
            "Course Preference 5": "Operating Systems", "Experience in Course 5": 4
        },
        {
            "Faculty Name": "Dr. D. Arban Das",
            "Designation": "Professor & Vice Dean",
            "Additional Duties": "Vice Dean",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Advanced Linear Algebra and Optimization", "Experience in Course 1": 10,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 8,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 6,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 4,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 2
        },
        {
            "Faculty Name": "Dr. Siva",
            "Designation": "Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Machine Learning", "Experience in Course 1": 10,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 7,
            "Course Preference 3": "Operating Systems", "Experience in Course 3": 5,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 2,
            "Course Preference 5": "Open Elective - 1", "Experience in Course 5": 2
        },
        {
            "Faculty Name": "Dr. Priya Verma",
            "Designation": "Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Machine Learning", "Experience in Course 1": 9,
            "Course Preference 2": "Open Elective - 1", "Experience in Course 2": 8,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 6,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 4,
            "Course Preference 5": "Full Stack AI Application Development", "Experience in Course 5": 2
        },
        {
            "Faculty Name": "Prof. Kumar Swamy",
            "Designation": "Professor",
            "Additional Duties": "None",
            "Qualification": "PhD DBMS",
            "Course Preference 1": "Full Stack AI Application Development", "Experience in Course 1": 10,
            "Course Preference 2": "Operating Systems", "Experience in Course 2": 7,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 5,
            "Course Preference 4": "Digital Logic and Computer Organization", "Experience in Course 4": 3,
            "Course Preference 5": "Machine Learning", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Anish Reddy",
            "Designation": "Associate Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Advanced Linear Algebra and Optimization", "Experience in Course 1": 7,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 6,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 4,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 3,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 2
        },
        {
            "Faculty Name": "Prof. Sunita Gupta",
            "Designation": "Associate Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech Cloud",
            "Course Preference 1": "Operating Systems", "Experience in Course 1": 8,
            "Course Preference 2": "Full Stack AI Application Development", "Experience in Course 2": 6,
            "Course Preference 3": "Open Elective - 1", "Experience in Course 3": 5,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Rajesh Iyer",
            "Designation": "Associate Professor",
            "Additional Duties": "None",
            "Qualification": "PhD Data Science",
            "Course Preference 1": "Machine Learning", "Experience in Course 1": 7,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 6,
            "Course Preference 3": "Advanced Linear Algebra and Optimization", "Experience in Course 3": 5,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 3,
            "Course Preference 5": "Full Stack AI Application Development", "Experience in Course 5": 2
        },
        {
            "Faculty Name": "Prof. Meena Patel",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Digital Logic and Computer Organization", "Experience in Course 1": 6,
            "Course Preference 2": "Operating Systems", "Experience in Course 2": 5,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 3,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Advanced Linear Algebra and Optimization", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Vikram Singh",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD IT",
            "Course Preference 1": "Full Stack AI Application Development", "Experience in Course 1": 6,
            "Course Preference 2": "Machine Learning", "Experience in Course 2": 4,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 3,
            "Course Preference 4": "Advanced Linear Algebra and Optimization", "Experience in Course 4": 2,
            "Course Preference 5": "Operating Systems", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Lakshmi N",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD AI",
            "Course Preference 1": "Algorithm Design and Analysis", "Experience in Course 1": 6,
            "Course Preference 2": "Full Stack AI Application Development", "Experience in Course 2": 4,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 3,
            "Course Preference 4": "Digital Logic and Computer Organization", "Experience in Course 4": 2,
            "Course Preference 5": "Open Elective - 1", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Suresh Kumar",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Open Elective - 1", "Experience in Course 1": 5,
            "Course Preference 2": "Operating Systems", "Experience in Course 2": 4,
            "Course Preference 3": "Digital Logic and Computer Organization", "Experience in Course 3": 3,
            "Course Preference 4": "Algorithm Design and Analysis", "Experience in Course 4": 2,
            "Course Preference 5": "Machine Learning", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Kavita Sharma",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Machine Learning", "Experience in Course 1": 6,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 5,
            "Course Preference 3": "Advanced Linear Algebra and Optimization", "Experience in Course 3": 3,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 2,
            "Course Preference 5": "Open Elective - 1", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Ramesh Babu",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech AI",
            "Course Preference 1": "Digital Logic and Computer Organization", "Experience in Course 1": 5,
            "Course Preference 2": "Operating Systems", "Experience in Course 2": 4,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 3,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 2,
            "Course Preference 5": "Advanced Linear Algebra and Optimization", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Neha Kulkarni",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD Data Science",
            "Course Preference 1": "Full Stack AI Application Development", "Experience in Course 1": 6,
            "Course Preference 2": "Advanced Linear Algebra and Optimization", "Experience in Course 2": 5,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 3,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 2,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Amit Shah",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech Cloud",
            "Course Preference 1": "Operating Systems", "Experience in Course 1": 5,
            "Course Preference 2": "Digital Logic and Computer Organization", "Experience in Course 2": 4,
            "Course Preference 3": "Advanced Linear Algebra and Optimization", "Experience in Course 3": 3,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Algorithm Design and Analysis", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Geeta Nair",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD IT",
            "Course Preference 1": "Advanced Linear Algebra and Optimization", "Experience in Course 1": 6,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 4,
            "Course Preference 3": "Digital Logic and Computer Organization", "Experience in Course 3": 3,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Operating Systems", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Nitin Desai",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Operating Systems", "Experience in Course 1": 4,
            "Course Preference 2": "Full Stack AI Application Development", "Experience in Course 2": 3,
            "Course Preference 3": "Advanced Linear Algebra and Optimization", "Experience in Course 3": 2,
            "Course Preference 4": "Digital Logic and Computer Organization", "Experience in Course 4": 2,
            "Course Preference 5": "Machine Learning", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Sunita Rao",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Algorithm Design and Analysis", "Experience in Course 1": 5,
            "Course Preference 2": "Machine Learning", "Experience in Course 2": 4,
            "Course Preference 3": "Operating Systems", "Experience in Course 3": 3,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 2,
            "Course Preference 5": "Open Elective - 1", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Pooja Sharma",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD AI",
            "Course Preference 1": "Open Elective - 1", "Experience in Course 1": 6,
            "Course Preference 2": "Digital Logic and Computer Organization", "Experience in Course 2": 5,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 4,
            "Course Preference 4": "Algorithm Design and Analysis", "Experience in Course 4": 2,
            "Course Preference 5": "Operating Systems", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Alok Kumar",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Open Elective - 1", "Experience in Course 1": 5,
            "Course Preference 2": "Advanced Linear Algebra and Optimization", "Experience in Course 2": 4,
            "Course Preference 3": "Digital Logic and Computer Organization", "Experience in Course 3": 3,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Algorithm Design and Analysis", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Arvind Swamy",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Digital Logic and Computer Organization", "Experience in Course 1": 6,
            "Course Preference 2": "Advanced Linear Algebra and Optimization", "Experience in Course 2": 5,
            "Course Preference 3": "Operating Systems", "Experience in Course 3": 4,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Full Stack AI Application Development", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Shweta Singh",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech AI",
            "Course Preference 1": "Full Stack AI Application Development", "Experience in Course 1": 5,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 4,
            "Course Preference 3": "Operating Systems", "Experience in Course 3": 3,
            "Course Preference 4": "Digital Logic and Computer Organization", "Experience in Course 4": 2,
            "Course Preference 5": "Machine Learning", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Harish Chandra",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD Math",
            "Course Preference 1": "Advanced Linear Algebra and Optimization", "Experience in Course 1": 9,
            "Course Preference 2": "Algorithm Design and Analysis", "Experience in Course 2": 6,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 4,
            "Course Preference 4": "Open Elective - 1", "Experience in Course 4": 2,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Divya Teja",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Open Elective - 1", "Experience in Course 1": 6,
            "Course Preference 2": "Full Stack AI Application Development", "Experience in Course 2": 5,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 3,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 2,
            "Course Preference 5": "Machine Learning", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Manoj Varma",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Digital Logic and Computer Organization", "Experience in Course 1": 7,
            "Course Preference 2": "Operating Systems", "Experience in Course 2": 5,
            "Course Preference 3": "Advanced Linear Algebra and Optimization", "Experience in Course 3": 3,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 2,
            "Course Preference 5": "Machine Learning", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Sneha Roy",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech IT",
            "Course Preference 1": "Open Elective - 1", "Experience in Course 1": 5,
            "Course Preference 2": "Advanced Linear Algebra and Optimization", "Experience in Course 2": 4,
            "Course Preference 3": "Full Stack AI Application Development", "Experience in Course 3": 3,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 2,
            "Course Preference 5": "Digital Logic and Computer Organization", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Tarun Sen",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD AI",
            "Course Preference 1": "Algorithm Design and Analysis", "Experience in Course 1": 7,
            "Course Preference 2": "Advanced Linear Algebra and Optimization", "Experience in Course 2": 6,
            "Course Preference 3": "Machine Learning", "Experience in Course 3": 5,
            "Course Preference 4": "Operating Systems", "Experience in Course 4": 2,
            "Course Preference 5": "Full Stack AI Application Development", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Bhavana Reddy",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Operating Systems", "Experience in Course 1": 7,
            "Course Preference 2": "Digital Logic and Computer Organization", "Experience in Course 2": 6,
            "Course Preference 3": "Full Stack AI Application Development", "Experience in Course 3": 4,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Algorithm Design and Analysis", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Karthik Rao",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Full Stack AI Application Development", "Experience in Course 1": 8,
            "Course Preference 2": "Operating Systems", "Experience in Course 2": 5,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 4,
            "Course Preference 4": "Advanced Linear Algebra and Optimization", "Experience in Course 4": 3,
            "Course Preference 5": "Open Elective - 1", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Pallavi Joshi",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech AI",
            "Course Preference 1": "Open Elective - 1", "Experience in Course 1": 6,
            "Course Preference 2": "Advanced Linear Algebra and Optimization", "Experience in Course 2": 5,
            "Course Preference 3": "Digital Logic and Computer Organization", "Experience in Course 3": 4,
            "Course Preference 4": "Machine Learning", "Experience in Course 4": 2,
            "Course Preference 5": "Operating Systems", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Dr. Vivek Murthy",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "PhD CSE",
            "Course Preference 1": "Digital Logic and Computer Organization", "Experience in Course 1": 7,
            "Course Preference 2": "Machine Learning", "Experience in Course 2": 6,
            "Course Preference 3": "Operating Systems", "Experience in Course 3": 4,
            "Course Preference 4": "Full Stack AI Application Development", "Experience in Course 4": 3,
            "Course Preference 5": "Algorithm Design and Analysis", "Experience in Course 5": 1
        },
        {
            "Faculty Name": "Prof. Ananya Das",
            "Designation": "Assistant Professor",
            "Additional Duties": "None",
            "Qualification": "M.Tech CSE",
            "Course Preference 1": "Machine Learning", "Experience in Course 1": 7,
            "Course Preference 2": "Full Stack AI Application Development", "Experience in Course 2": 6,
            "Course Preference 3": "Algorithm Design and Analysis", "Experience in Course 3": 5,
            "Course Preference 4": "Open Elective - 1", "Experience in Course 4": 2,
            "Course Preference 5": "Advanced Linear Algebra and Optimization", "Experience in Course 5": 1
        }
    ]

    wide_df = pd.DataFrame(wide_sample_data)
    wide_path = os.path.join(output_dir, "faculty_sample_combined.xlsx")
    pref_path = os.path.join(output_dir, "faculty_preferences.xlsx")
    exp_path = os.path.join(output_dir, "faculty_experience.xlsx")

    # Save wide format sample
    wide_df.to_excel(wide_path, index=False)
    
    # Save standard preferences & experience breakdown for backward compatibility
    pref_rows = []
    exp_rows = []
    for idx, row in wide_df.iterrows():
        fac_id = f"F{idx+1:03d}"
        pref_item = {
            "Faculty_ID": fac_id,
            "Faculty_Name": row["Faculty Name"],
            "Designation": row["Designation"],
            "Additional_Duties": row.get("Additional Duties", "None"),
            "Qualification": row["Qualification"]
        }
        for r in range(1, 6):
            pref_item[f"Preference_{r}"] = row[f"Course Preference {r}"]
            exp_rows.append({
                "Faculty_ID": fac_id,
                "Subject": row[f"Course Preference {r}"],
                "Qualification": row["Qualification"],
                "Skill_Level": "Expert" if row[f"Experience in Course {r}"] >= 8 else ("Advanced" if row[f"Experience in Course {r}"] >= 5 else "Intermediate"),
                "Experience_Years": row[f"Experience in Course {r}"]
            })
        pref_rows.append(pref_item)

    pd.DataFrame(pref_rows).to_excel(pref_path, index=False)
    pd.DataFrame(exp_rows).to_excel(exp_path, index=False)
    print(f"Sample files generated at {course_path} and {wide_path}")

if __name__ == "__main__":
    generate_sample_files()
