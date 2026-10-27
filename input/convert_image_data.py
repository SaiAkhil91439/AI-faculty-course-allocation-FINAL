import os
import pandas as pd

raw_data = [
    {"Faculty_ID": "A001", "Faculty_Name": "Ramesh Kumar", "Qualification": "M.Tech", "Domain": "AI/ML", 
     "p1": "ML", "exp1": 10, "p2": "DSA", "exp2": 4, "p3": "Cyber Security", "exp3": 4, "p4": "Cloud Computing", "exp4": 0, "p5": "Human-Computer Interaction", "exp5": 0},
    {"Faculty_ID": "A002", "Faculty_Name": "Sunita Sharma", "Qualification": "PhD", "Domain": "AI/ML", 
     "p1": "Computer Networks", "exp1": 14, "p2": "ML", "exp2": 13, "p3": "Computer Graphics", "exp3": 0, "p4": "AI", "exp4": 6, "p5": "Big Data Analytics", "exp5": 0},
    {"Faculty_ID": "A003", "Faculty_Name": "Anil Verma", "Qualification": "M.Tech", "Domain": "Data Science", 
     "p1": "DBMS", "exp1": 8, "p2": "DSA", "exp2": 4, "p3": "AI", "exp3": 1, "p4": "Data Mining", "exp4": 3, "p5": "Cloud Computing", "exp5": 0},
    {"Faculty_ID": "A004", "Faculty_Name": "Priya Reddy", "Qualification": "PhD", "Domain": "Software Engineering", 
     "p1": "Human-Computer Interaction", "exp1": 16, "p2": "DSA", "exp2": 6, "p3": "Computer Graphics", "exp3": 0, "p4": "Data Mining", "exp4": 0, "p5": "Big Data Analytics", "exp5": 0},
    {"Faculty_ID": "A005", "Faculty_Name": "Suresh Iyer", "Qualification": "M.Sc", "Domain": "Core CS", 
     "p1": "Cloud Computing", "exp1": 4, "p2": "IoT", "exp2": 2, "p3": "Cyber Security", "exp3": 0, "p4": "DSA", "exp4": 2, "p5": "Operating Systems", "exp5": 1},
    {"Faculty_ID": "A006", "Faculty_Name": "Kavita Nair", "Qualification": "PhD", "Domain": "Data Science", 
     "p1": "Big Data Analytics", "exp1": 11, "p2": "Web Technologies", "exp2": 5, "p3": "Cyber Security", "exp3": 0, "p4": "Computer Networks", "exp4": 3, "p5": "Data Mining", "exp5": 2},
    {"Faculty_ID": "A007", "Faculty_Name": "Rajesh Gupta", "Qualification": "PhD", "Domain": "AI/ML", 
     "p1": "Web Technologies", "exp1": 16, "p2": "ML", "exp2": 15, "p3": "AI", "exp3": 11, "p4": "Distributed Systems", "exp4": 3, "p5": "Theory of Computation", "exp5": 0},
    {"Faculty_ID": "A008", "Faculty_Name": "Deepa Menon", "Qualification": "M.Tech", "Domain": "Core CS", 
     "p1": "Compiler Design", "exp1": 7, "p2": "Mobile App Development", "exp2": 3, "p3": "Cyber Security", "exp3": 3, "p4": "DBMS", "exp4": 0, "p5": "IoT", "exp5": 0},
    {"Faculty_ID": "A009", "Faculty_Name": "Vikram Singh", "Qualification": "M.Tech", "Domain": "AI/ML", 
     "p1": "Computer Graphics", "exp1": 0, "p2": "ML", "exp2": 4, "p3": "Distributed Systems", "exp3": 6, "p4": "AI", "exp4": 2, "p5": "Software Engineering", "exp5": 0},
    {"Faculty_ID": "A010", "Faculty_Name": "Anjali Rao", "Qualification": "PhD", "Domain": "Data Science", 
     "p1": "Mobile App Development", "exp1": 8, "p2": "Compiler Design", "exp2": 7, "p3": "Data Mining", "exp3": 6, "p4": "AI", "exp4": 2, "p5": "DBMS", "exp5": 0},
    {"Faculty_ID": "A011", "Faculty_Name": "Manoj Pillai", "Qualification": "M.Tech", "Domain": "Cloud Computing", 
     "p1": "Cloud Computing", "exp1": 7, "p2": "Software Engineering", "exp2": 0, "p3": "AI", "exp3": 2, "p4": "Mobile App Development", "exp4": 1, "p5": "ML", "exp5": 5},
    {"Faculty_ID": "A012", "Faculty_Name": "Neha Joshi", "Qualification": "PhD", "Domain": "Core CS", 
     "p1": "Distributed Systems", "exp1": 14, "p2": "Cyber Security", "exp2": 9, "p3": "IoT", "exp3": 0, "p4": "Compiler Design", "exp4": 5, "p5": "Operating Systems", "exp5": 6},
    {"Faculty_ID": "A013", "Faculty_Name": "Sanjay Patel", "Qualification": "PhD", "Domain": "Core CS", 
     "p1": "Compiler Design", "exp1": 17, "p2": "Mobile App Development", "exp2": 7, "p3": "Data Mining", "exp3": 6, "p4": "Cyber Security", "exp4": 2, "p5": "AI", "exp5": 3},
    {"Faculty_ID": "A014", "Faculty_Name": "Pooja Desai", "Qualification": "M.Tech", "Domain": "Core CS", 
     "p1": "Mobile App Development", "exp1": 2, "p2": "Operating Systems", "exp2": 1, "p3": "Computer Graphics", "exp3": 1, "p4": "Cloud Computing", "exp4": 0, "p5": "Theory of Computation", "exp5": 0},
    {"Faculty_ID": "A015", "Faculty_Name": "Arun Chandran", "Qualification": "M.Tech", "Domain": "Cloud Computing", 
     "p1": "IoT", "exp1": 10, "p2": "Distributed Systems", "exp2": 10, "p3": "Cyber Security", "exp3": 0, "p4": "Cloud Computing", "exp4": 3, "p5": "Web Technologies", "exp5": 0},
    {"Faculty_ID": "A016", "Faculty_Name": "Meera Krishnan", "Qualification": "PhD", "Domain": "Data Science", 
     "p1": "DBMS", "exp1": 17, "p2": "Cloud Computing", "exp2": 7, "p3": "Mobile App Development", "exp3": 0, "p4": "Web Technologies", "exp4": 0, "p5": "Distributed Systems", "exp5": 0},
    {"Faculty_ID": "A017", "Faculty_Name": "Ashok Bhatt", "Qualification": "M.Tech", "Domain": "Cyber Security", 
     "p1": "Cyber Security", "exp1": 2, "p2": "AI", "exp2": 0, "p3": "Data Mining", "exp3": 1, "p4": "Web Technologies", "exp4": 0, "p5": "Computer Graphics", "exp5": 0},
    {"Faculty_ID": "A018", "Faculty_Name": "Divya Subramanian", "Qualification": "M.Sc", "Domain": "Cyber Security", 
     "p1": "Blockchain", "exp1": 5, "p2": "Distributed Systems", "exp2": 3, "p3": "IoT", "exp3": 1, "p4": "Computer Networks", "exp4": 0, "p5": "Cyber Security", "exp5": 2},
    {"Faculty_ID": "A019", "Faculty_Name": "Rahul Mehta", "Qualification": "M.Tech", "Domain": "Networks", 
     "p1": "Computer Networks", "exp1": 13, "p2": "Cloud Computing", "exp2": 7, "p3": "Computer Graphics", "exp3": 4, "p4": "Cyber Security", "exp4": 2, "p5": "Big Data Analytics", "exp5": 0},
    {"Faculty_ID": "A020", "Faculty_Name": "Swati Kulkarni", "Qualification": "M.Tech", "Domain": "Core CS", 
     "p1": "Theory of Computation", "exp1": 10, "p2": "Distributed Systems", "exp2": 0, "p3": "Compiler Design", "exp3": 5, "p4": "Cloud Computing", "exp4": 0, "p5": "Computer Networks", "exp5": 0},
    {"Faculty_ID": "A021", "Faculty_Name": "Vijay Rangan", "Qualification": "PhD", "Domain": "AI/ML", 
     "p1": "Human-Computer Interaction", "exp1": 6, "p2": "Blockchain", "exp2": 4, "p3": "AI", "exp3": 6, "p4": "DBMS", "exp4": 0, "p5": "ML", "exp5": 3},
    {"Faculty_ID": "A022", "Faculty_Name": "Lakshmi Narayanan", "Qualification": "M.Sc", "Domain": "Networks", 
     "p1": "Computer Networks", "exp1": 9, "p2": "Operating Systems", "exp2": 0, "p3": "AI", "exp3": 0, "p4": "AI", "exp4": 1, "p5": "Distributed Systems", "exp5": 0},
    {"Faculty_ID": "A023", "Faculty_Name": "Kiran Bose", "Qualification": "PhD", "Domain": "Cloud Computing", 
     "p1": "Distributed Systems", "exp1": 9, "p2": "IoT", "exp2": 3, "p3": "Human-Computer Interaction", "exp3": 1, "p4": "Cyber Security", "exp4": 2, "p5": "DSA", "exp5": 0},
    {"Faculty_ID": "A024", "Faculty_Name": "Nandini Iyengar", "Qualification": "PhD", "Domain": "Software Engineering", 
     "p1": "ML", "exp1": 18, "p2": "Computer Graphics", "exp2": 11, "p3": "Cyber Security", "exp3": 8, "p4": "Web Technologies", "exp4": 4, "p5": "Mobile App Development", "exp5": 3},
    {"Faculty_ID": "A025", "Faculty_Name": "Prakash Rao", "Qualification": "M.Tech", "Domain": "Core CS", 
     "p1": "Software Engineering", "exp1": 4, "p2": "Big Data Analytics", "exp2": 2, "p3": "Operating Systems", "exp3": 2, "p4": "IoT", "exp4": 0, "p5": "DSA", "exp5": 1},
]

def derive_skill_level(exp_years: float) -> str:
    if exp_years >= 8:
        return "Expert"
    elif exp_years >= 5:
        return "Advanced"
    elif exp_years >= 2:
        return "Intermediate"
    else:
        return "Beginner"

def generate_exact_two_excels(output_dir: str = "input"):
    os.makedirs(output_dir, exist_ok=True)
    
    preferences_rows = []
    experience_rows = []

    for item in raw_data:
        fac_id = item["Faculty_ID"]
        fac_name = item["Faculty_Name"]
        qual = item["Qualification"]

        # Preference row
        pref_row = {
            "Faculty_ID": fac_id,
            "Faculty_Name": fac_name,
            "Preference_1": item["p1"],
            "Preference_2": item["p2"],
            "Preference_3": item["p3"],
            "Preference_4": item["p4"],
            "Preference_5": item["p5"]
        }
        preferences_rows.append(pref_row)

        # Experience rows for each course
        for rank in range(1, 6):
            subj = item[f"p{rank}"]
            exp = item[f"exp{rank}"]
            skill = derive_skill_level(exp)
            
            experience_rows.append({
                "Faculty_ID": fac_id,
                "Subject": subj,
                "Qualification": qual,
                "Skill_Level": skill,
                "Experience_Years": exp
            })

    pref_df = pd.DataFrame(preferences_rows)
    exp_df = pd.DataFrame(experience_rows)

    pref_path = os.path.join(output_dir, "faculty_preferences.xlsx")
    exp_path = os.path.join(output_dir, "faculty_experience.xlsx")

    pref_df.to_excel(pref_path, index=False)
    exp_df.to_excel(exp_path, index=False)

    print(f"Generated faculty_preferences.xlsx ({len(pref_df)} rows) at {pref_path}")
    print(f"Generated faculty_experience.xlsx ({len(exp_df)} rows) at {exp_path}")

if __name__ == "__main__":
    generate_exact_two_excels()
