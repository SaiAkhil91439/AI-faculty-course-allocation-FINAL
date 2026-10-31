import os
import pandas as pd

def create_multiyear_dataset(output_dir: str = "input"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Faculty Roster & Preferences (57 faculty members from user's data)
    faculty_data = [
        {"S.No": 1, "Name of the Faculty": "Dr. D. Venkatesulu", "Designation": "Professor, Dean R&D and Additional Dean", "Theory-1": None, "Theory-2": None, "Theory-3": None, "Theory-4": None, "Theory-5": None},
        {"S.No": 2, "Name of the Faculty": "Dr. B. Jyostna Devi", "Designation": "Associate Professor, AIML HoD", "Theory-1": "Natural Language Processing", "Theory-2": "Machine Learning", "Theory-3": "Web and Sequence Data Mining", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Python Programming Essentials"},
        {"S.No": 3, "Name of the Faculty": "Dr. Eva Patel", "Designation": "Professor", "Theory-1": "Operating Systems", "Theory-2": "Natural Language Processing", "Theory-3": "Cloud Computing", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Machine Learning"},
        {"S.No": 4, "Name of the Faculty": "Dr. Fathimabi Shaik", "Designation": "Asst. Prof. Selection Grade", "Theory-1": "Big Data Analytics", "Theory-2": "Natural Language Processing", "Theory-3": "Web and Sequence Data Mining", "Theory-4": "Cloud Computing", "Theory-5": "Design Thinking and Engineering Orientation"},
        {"S.No": 5, "Name of the Faculty": "Dr. Mastan Sharif", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Python Programming Essentials", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Design Thinking and Engineering Orientation", "Theory-4": "Computer Networks", "Theory-5": "Natural Language Processing"},
        {"S.No": 6, "Name of the Faculty": "Dr. P.M. Benson Mansingh", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Computer Networks", "Theory-2": "Cloud Computing", "Theory-3": None, "Theory-4": None, "Theory-5": None},
        {"S.No": 7, "Name of the Faculty": "Dr. C. Sateesh Kumar Reddy", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Machine Learning", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Computer Networks", "Theory-4": "Design Thinking and Engineering Orientation", "Theory-5": "Cloud Computing"},
        {"S.No": 8, "Name of the Faculty": "Dr. B. Sudha Rani", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Digital Logic and Computer Organization", "Theory-2": "Machine Learning", "Theory-3": "Python Programming Essentials", "Theory-4": "Computer Networks", "Theory-5": None},
        {"S.No": 9, "Name of the Faculty": "Dr. Jawad Ahmad Dar", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Reinforcement Learning", "Theory-2": "Machine Learning", "Theory-3": "Operating Systems", "Theory-4": "Python Programming Essentials", "Theory-5": "Algorithm Design and Analysis"},
        {"S.No": 10, "Name of the Faculty": "Dr. Ramesh Kumar Mojjada", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Operating Systems", "Theory-4": "Computer Networks", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 11, "Name of the Faculty": "Dr. Gurusamy Murugesan", "Designation": "Asst. Prof. Senior Level", "Theory-1": "Natural Language Processing", "Theory-2": "Big Data Analytics", "Theory-3": "Computer Networks", "Theory-4": "Reinforcement Learning", "Theory-5": "Web and Sequence Data Mining"},
        {"S.No": 12, "Name of the Faculty": "Dr. Arnab De", "Designation": "Assistant Professor", "Theory-1": "Computer Networks", "Theory-2": "Cloud Computing", "Theory-3": "Operating Systems", "Theory-4": "Machine Learning", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 13, "Name of the Faculty": "Dr. Chennapradaga Amarendra", "Designation": "Assistant Professor", "Theory-1": "Design Thinking and Engineering Orientation", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Full Stack Development", "Theory-4": "Front-End Web Development", "Theory-5": "Operating Systems"},
        {"S.No": 14, "Name of the Faculty": "Dr. G. Kalaiarasi", "Designation": "Assistant Professor", "Theory-1": "Machine Learning", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Python Programming Essentials", "Theory-4": "Computer Networks", "Theory-5": None},
        {"S.No": 15, "Name of the Faculty": "Dr. S.Srikantha Reddy", "Designation": "Assistant Professor", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Machine Learning", "Theory-5": "Natural Language Processing"},
        {"S.No": 16, "Name of the Faculty": "Dr. A Subramanyam", "Designation": "Assistant Professor", "Theory-1": "Python Programming Essentials", "Theory-2": "Design Thinking and Engineering Orientation", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Front-End Web Development", "Theory-5": "Machine Learning"},
        {"S.No": 17, "Name of the Faculty": "Dr. P. Giri Prasad", "Designation": "Assistant Professor", "Theory-1": "Machine Learning", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Natural Language Processing", "Theory-4": "Computer Networks", "Theory-5": "Python Programming Essentials"},
        {"S.No": 18, "Name of the Faculty": "Dr. Subham Kumar Sahoo", "Designation": "Assistant Professor", "Theory-1": "Cloud Computing", "Theory-2": "Computer Networks", "Theory-3": "Operating Systems", "Theory-4": "Python Programming Essentials", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 19, "Name of the Faculty": "Dr. B Sai Sambasiva Rao", "Designation": "Assistant Professor", "Theory-1": "Python Programming Essentials", "Theory-2": "Machine Learning", "Theory-3": "Big Data Analytics", "Theory-4": "Natural Language Processing", "Theory-5": "Cloud Computing"},
        {"S.No": 20, "Name of the Faculty": "Ms. S. Radha Rani", "Designation": "Assistant Professor", "Theory-1": "Machine Learning", "Theory-2": "Full Stack Development", "Theory-3": "Front-End Web Development", "Theory-4": "Computer Networks", "Theory-5": "Python Programming Essentials"},
        {"S.No": 21, "Name of the Faculty": "Ms. G. Mahalakshmi", "Designation": "Assistant Professor", "Theory-1": "Machine Learning", "Theory-2": "Computer Networks", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Operating Systems", "Theory-5": "Algorithm Design and Analysis"},
        {"S.No": 22, "Name of the Faculty": "Mr. Anirudh Khade", "Designation": "Assistant Professor", "Theory-1": "Front-End Web Development", "Theory-2": "Python Programming Essentials", "Theory-3": "Machine Learning", "Theory-4": None, "Theory-5": None},
        {"S.No": 23, "Name of the Faculty": "Ms. Beulah Bontha", "Designation": "Assistant Professor", "Theory-1": "Cloud Computing", "Theory-2": "Machine Learning", "Theory-3": "Cloud Computing", "Theory-4": "Machine Learning", "Theory-5": "Cloud Computing"},
        {"S.No": 24, "Name of the Faculty": "Ms. I.Leela Priya", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Operating Systems", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Computer Networks", "Theory-4": "Cloud Computing", "Theory-5": "Machine Learning"},
        {"S.No": 25, "Name of the Faculty": "Ms. Jayamma Rodda", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Operating Systems", "Theory-2": "Computer Networks", "Theory-3": "Full Stack Development", "Theory-4": "Front-End Web Development", "Theory-5": "Algorithm Design and Analysis"},
        {"S.No": 26, "Name of the Faculty": "Mr. Brundavanam Satya Sai", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Digital Logic and Computer Organization", "Theory-2": "Machine Learning", "Theory-3": "Natural Language Processing", "Theory-4": "Computer Networks", "Theory-5": None},
        {"S.No": 27, "Name of the Faculty": "Ms. P Seetha Lakshmi", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Machine Learning", "Theory-2": "Natural Language Processing", "Theory-3": "Design Thinking and Engineering Orientation", "Theory-4": "Web and Sequence Data Mining", "Theory-5": None},
        {"S.No": 28, "Name of the Faculty": "Mr. PLN Manoj Kumar", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Full Stack Development", "Theory-4": "Operating Systems", "Theory-5": "Cloud Computing"},
        {"S.No": 29, "Name of the Faculty": "Mr. Bharadwaja Chepuri", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Computer Networks", "Theory-3": "Operating Systems", "Theory-4": "Python Programming Essentials", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 30, "Name of the Faculty": "Ms. D. Urlamma", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Computer Networks", "Theory-2": "Machine Learning", "Theory-3": "Python Programming Essentials", "Theory-4": "Operating Systems", "Theory-5": "Natural Language Processing"},
        {"S.No": 31, "Name of the Faculty": "MR. M. Komal Krishna", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Python Programming Essentials", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Machine Learning", "Theory-4": "Natural Language Processing", "Theory-5": "Web and Sequence Data Mining"},
        {"S.No": 32, "Name of the Faculty": "Ms. Syed Reshma", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Full Stack Development", "Theory-2": "Front-End Web Development", "Theory-3": "Operating Systems", "Theory-4": "Computer Networks", "Theory-5": None},
        {"S.No": 33, "Name of the Faculty": "Mr. Vivek Kumar Saini", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Computer Networks", "Theory-2": "Operating Systems", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Cloud Computing", "Theory-5": "Python Programming Essentials"},
        {"S.No": 34, "Name of the Faculty": "Mr. Srinivasa Rao Lukka", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Python Programming Essentials", "Theory-2": "Algorithm Design and Analysis", "Theory-3": "Operating Systems", "Theory-4": "Machine Learning", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 35, "Name of the Faculty": "Mr. Vinod Kumar Dasari", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Machine Learning", "Theory-2": "Digital Logic and Computer Organization", "Theory-3": "Cloud Computing", "Theory-4": "Operating Systems", "Theory-5": "Mini Project - Branch Specific"},
        {"S.No": 36, "Name of the Faculty": "Ms. K. Krupa Sagari", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Machine Learning", "Theory-4": "Computer Networks", "Theory-5": "Operating Systems"},
        {"S.No": 37, "Name of the Faculty": "Mr. Sattwik Barua", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Machine Learning", "Theory-2": "Reinforcement Learning", "Theory-3": "Natural Language Processing", "Theory-4": "Digital Logic and Computer Organization", "Theory-5": "Python Programming Essentials"},
        {"S.No": 38, "Name of the Faculty": "Ms. Morampudi Sravika", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Front-End Web Development", "Theory-2": "Design Thinking and Engineering Orientation", "Theory-3": "Computer Networks", "Theory-4": "Cloud Computing", "Theory-5": "Operating Systems"},
        {"S.No": 39, "Name of the Faculty": "Mrs. Alladi Vennela", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Python Programming Essentials", "Theory-2": "Operating Systems", "Theory-3": "Machine Learning", "Theory-4": "Computer Networks", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 40, "Name of the Faculty": "Mr. Sourabh Viswakarma", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Computer Networks", "Theory-2": "Operating Systems", "Theory-3": "Machine Learning", "Theory-4": "Computer Networks", "Theory-5": None},
        {"S.No": 41, "Name of the Faculty": "Mr. Bhukya Akash", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Front-End Web Development", "Theory-2": "Machine Learning", "Theory-3": "Operating Systems", "Theory-4": "Python Programming Essentials", "Theory-5": "Computer Networks"},
        {"S.No": 42, "Name of the Faculty": "Mr. Satwik Singh", "Designation": "Asst. Prof. (Contract)", "Theory-1": "Machine Learning", "Theory-2": "Machine Learning", "Theory-3": "Machine Learning", "Theory-4": "Python Programming Essentials", "Theory-5": "Machine Learning"},
        {"S.No": 43, "Name of the Faculty": "Mr. D. Pavan Kalyan", "Designation": "Teaching Associate", "Theory-1": "Operating Systems", "Theory-2": "Cloud Computing", "Theory-3": "Front-End Web Development", "Theory-4": "Computer Networks", "Theory-5": "Full Stack Development"},
        {"S.No": 44, "Name of the Faculty": "Mr. A.Siva Naga Rama Gopal", "Designation": "Teaching Associate", "Theory-1": "Digital Logic and Computer Organization", "Theory-2": "Machine Learning", "Theory-3": "Python Programming Essentials", "Theory-4": "Operating Systems", "Theory-5": "Computer Networks"},
        {"S.No": 45, "Name of the Faculty": "Mr. S. Uday Kiran", "Designation": "Teaching Associate", "Theory-1": "Design Thinking and Engineering Orientation", "Theory-2": "Machine Learning", "Theory-3": "Front-End Web Development", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Python Programming Essentials"},
        {"S.No": 46, "Name of the Faculty": "Mitikala Ramanjaneyulu", "Designation": "Teaching Associate", "Theory-1": "Python Programming Essentials", "Theory-2": "Operating Systems", "Theory-3": "Front-End Web Development", "Theory-4": "Computer Networks", "Theory-5": "Full Stack Development"},
        {"S.No": 47, "Name of the Faculty": "Mr.Jujjuvarapu Nagendra", "Designation": "Teaching Associate", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Operating Systems", "Theory-4": "Computer Networks", "Theory-5": "Digital Logic and Computer Organization"},
        {"S.No": 48, "Name of the Faculty": "Mr. Kolisetti Jagadeeswar", "Designation": "Teaching Associate", "Theory-1": "Operating Systems", "Theory-2": "Full Stack Development", "Theory-3": "Front-End Web Development", "Theory-4": "Computer Networks", "Theory-5": "Cloud Computing"},
        {"S.No": 49, "Name of the Faculty": "Ms. Kurapati Supraja", "Designation": "Teaching Associate", "Theory-1": "Front-End Web Development", "Theory-2": "Natural Language Processing", "Theory-3": "Python Programming Essentials", "Theory-4": "Cloud Computing", "Theory-5": "Machine Learning"},
        {"S.No": 50, "Name of the Faculty": "Mr. K. Phanindra", "Designation": "Teaching Associate", "Theory-1": "Python Programming Essentials", "Theory-2": "Machine Learning", "Theory-3": "Design Thinking and Engineering Orientation", "Theory-4": "Natural Language Processing", "Theory-5": "Front-End Web Development"},
        {"S.No": 51, "Name of the Faculty": "Mr. K. Venkata Naga Vamsi", "Designation": "Teaching Associate", "Theory-1": "Python Programming Essentials", "Theory-2": "Design Thinking and Engineering Orientation", "Theory-3": "Machine Learning", "Theory-4": "Natural Language Processing", "Theory-5": "Front-End Web Development"},
        {"S.No": 52, "Name of the Faculty": "Mr. T. Leela Venkata Umamahesh", "Designation": "Teaching Associate", "Theory-1": "Python Programming Essentials", "Theory-2": "Algorithm Design and Analysis", "Theory-3": "Design Thinking and Engineering Orientation", "Theory-4": "Digital Logic and Computer Organization", "Theory-5": "Operating Systems"},
        {"S.No": 53, "Name of the Faculty": "Mr. N. Murali Krishna", "Designation": "Prog./ Teaching Assistant", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Machine Learning", "Theory-4": "Machine Learning", "Theory-5": "Machine Learning"},
        {"S.No": 54, "Name of the Faculty": "Ms. Ambati Hemalatha", "Designation": "CAP", "Theory-1": "Machine Learning", "Theory-2": "Natural Language Processing", "Theory-3": "Python Programming Essentials", "Theory-4": "Computer Networks", "Theory-5": "Operating Systems"},
        {"S.No": 55, "Name of the Faculty": "Ms. G. Prathyusha", "Designation": "ERA", "Theory-1": "Python Programming Essentials", "Theory-2": "Computer Networks", "Theory-3": "Machine Learning", "Theory-4": "Cloud Computing", "Theory-5": "Operating Systems"},
        {"S.No": 56, "Name of the Faculty": "Mr. A. Sivaram", "Designation": "ERA", "Theory-1": "Python Programming Essentials", "Theory-2": "Machine Learning", "Theory-3": "Computer Networks", "Theory-4": "Cloud Computing", "Theory-5": "Operating Systems"},
        {"S.No": 57, "Name of the Faculty": "Ms. Vemuri Lakshmi Ravali", "Designation": "ERA", "Theory-1": "Machine Learning", "Theory-2": "Natural Language Processing", "Theory-3": "Python Programming Essentials", "Theory-4": "Front-End Web Development", "Theory-5": "Full Stack Development"}
    ]
    df_fac = pd.DataFrame(faculty_data)
    df_fac.to_excel(os.path.join(output_dir, "faculty_preferences.xlsx"), index=False)

    # 2. Teaching Assistants Dataset (31 TAs from user's data)
    ta_data = [
        {"Sl.No": 1, "Name of the Teaching Assistant": "Mr. M. Pramod Chandra", "Theory-1": "Natural Language Processing", "Theory-2": "Full Stack Development", "Theory-3": "Algorithm Design and Analysis", "Theory-4": "Computer Networks", "Theory-5": "Operating Systems"},
        {"Sl.No": 2, "Name of the Teaching Assistant": "Ms. K. Sabhamini", "Theory-1": "Design Thinking and Engineering Orientation", "Theory-2": "Machine Learning", "Theory-3": "Front-End Web Development", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Python Programming Essentials"},
        {"Sl.No": 3, "Name of the Teaching Assistant": "Mrs. Bokkisam Bhavana Sreeja", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Full Stack Development", "Theory-3": "Computer Networks", "Theory-4": "Natural Language Processing", "Theory-5": "Digital Logic and Computer Organization"},
        {"Sl.No": 4, "Name of the Teaching Assistant": "Marepalli Harya Vardhan", "Theory-1": "Machine Learning", "Theory-2": "Python Programming Essentials", "Theory-3": "Operating Systems", "Theory-4": "Cloud Computing", "Theory-5": "Computer Networks"},
        {"Sl.No": 5, "Name of the Teaching Assistant": "Ms.Satuluri Venkata Bhavani", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Operating Systems", "Theory-4": "Natural Language Processing", "Theory-5": "Full Stack Development"},
        {"Sl.No": 6, "Name of the Teaching Assistant": "Ms. Peethala Girija", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Full Stack Development", "Theory-3": "Operating Systems", "Theory-4": "Computer Networks", "Theory-5": "Digital Logic and Computer Organization"},
        {"Sl.No": 7, "Name of the Teaching Assistant": "Ms. Nune Naga Surekha", "Theory-1": "Python Programming Essentials", "Theory-2": "Machine Learning", "Theory-3": "Natural Language Processing", "Theory-4": "Full Stack Development", "Theory-5": "Web and Sequence Data Mining"},
        {"Sl.No": 8, "Name of the Teaching Assistant": "Ms. Kankanampati Nikhitha", "Theory-1": "Full Stack Development", "Theory-2": "Algorithm Design and Analysis", "Theory-3": "Front-End Web Development", "Theory-4": "Operating Systems", "Theory-5": "Computer Networks"},
        {"Sl.No": 9, "Name of the Teaching Assistant": "Ms. Kota Lakshmi Likhitha", "Theory-1": "Machine Learning", "Theory-2": "Full Stack Development", "Theory-3": "Natural Language Processing", "Theory-4": "Operating Systems", "Theory-5": "Computer Networks"},
        {"Sl.No": 10, "Name of the Teaching Assistant": "Ms. Parasa Jasmitha", "Theory-1": "Machine Learning", "Theory-2": "Full Stack Development", "Theory-3": "Computer Networks", "Theory-4": "Natural Language Processing", "Theory-5": "Operating Systems"},
        {"Sl.No": 11, "Name of the Teaching Assistant": "Mr. Yetcherla Ashok", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Mini Project - Branch Specific", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Computer Networks"},
        {"Sl.No": 12, "Name of the Teaching Assistant": "MR. K Karthik", "Theory-1": "Full Stack Development", "Theory-2": "Python Programming Essentials", "Theory-3": "Cloud Computing", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Operating Systems"},
        {"Sl.No": 13, "Name of the Teaching Assistant": "Mr. M S S Satya Mahendra Varma", "Theory-1": "Machine Learning", "Theory-2": "Natural Language Processing", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Cloud Computing", "Theory-5": "Python Programming Essentials"},
        {"Sl.No": 14, "Name of the Teaching Assistant": "Ms. Shaik Sameera Sultana", "Theory-1": "Operating Systems", "Theory-2": "Algorithm Design and Analysis", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Full Stack Development", "Theory-5": "Computer Networks"},
        {"Sl.No": 15, "Name of the Teaching Assistant": "Ms. Manda Sri Chakrapani", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Computer Networks", "Theory-3": "Operating Systems", "Theory-4": "Python Programming Essentials", "Theory-5": "Digital Logic and Computer Organization"},
        {"Sl.No": 16, "Name of the Teaching Assistant": "Mr. Vankayalapati Amarnath", "Theory-1": "Front-End Web Development", "Theory-2": "Mini Project - Branch Specific", "Theory-3": "Natural Language Processing", "Theory-4": "Generative and Agentic AI", "Theory-5": "Big Data Analytics"},
        {"Sl.No": 17, "Name of the Teaching Assistant": "Ms. Donepudi Supriya", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Computer Networks", "Theory-4": "Operating Systems", "Theory-5": "Full Stack Development"},
        {"Sl.No": 18, "Name of the Teaching Assistant": "Mr.Sunkara Devendra Kumar", "Theory-1": "Natural Language Processing", "Theory-2": "Machine Learning", "Theory-3": "Big Data Analytics", "Theory-4": "Generative and Agentic AI", "Theory-5": "ML Ops and LLM Ops"},
        {"Sl.No": 19, "Name of the Teaching Assistant": "Ms. B. Himaja", "Theory-1": "Full Stack Development", "Theory-2": "Computer Networks", "Theory-3": "Natural Language Processing", "Theory-4": "Digital Logic and Computer Organization", "Theory-5": "Machine Learning"},
        {"Sl.No": 20, "Name of the Teaching Assistant": "Ms Gnapika", "Theory-1": "Generative and Agentic AI", "Theory-2": "ML Ops and LLM Ops", "Theory-3": "Natural Language Processing", "Theory-4": "Reinforcement Learning", "Theory-5": "Cloud Computing"},
        {"Sl.No": 21, "Name of the Teaching Assistant": "Mr. P V V Satya Surya Teja Sri Manoj", "Theory-1": "Python Programming Essentials", "Theory-2": "Full Stack Development", "Theory-3": "Algorithm Design and Analysis", "Theory-4": "Mini Project - Branch Specific", "Theory-5": "Front-End Web Development"},
        {"Sl.No": 22, "Name of the Teaching Assistant": "Mr. Kosana Rajasekhar", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Mini Project - Branch Specific", "Theory-4": "Cloud Computing", "Theory-5": "Full Stack Development"},
        {"Sl.No": 23, "Name of the Teaching Assistant": "Ms. P. Prasanna", "Theory-1": "Front-End Web Development", "Theory-2": "Python Programming Essentials", "Theory-3": "Machine Learning", "Theory-4": "Computer Networks", "Theory-5": "Natural Language Processing"},
        {"Sl.No": 24, "Name of the Teaching Assistant": "Ms. V. Priya Sahithi", "Theory-1": "Algorithm Design and Analysis", "Theory-2": "Python Programming Essentials", "Theory-3": "Digital Logic and Computer Organization", "Theory-4": "Operating Systems", "Theory-5": "Computer Networks"},
        {"Sl.No": 25, "Name of the Teaching Assistant": "Mr. K. Satish Kumar", "Theory-1": "Natural Language Processing", "Theory-2": "Python Programming Essentials", "Theory-3": "Cloud Computing", "Theory-4": "Computer Networks", "Theory-5": "Machine Learning"},
        {"Sl.No": 26, "Name of the Teaching Assistant": "Gopi Ajay Kumar", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Mini Project - Branch Specific", "Theory-4": "Computer Networks", "Theory-5": "Operating Systems"},
        {"Sl.No": 27, "Name of the Teaching Assistant": "Kammapati Teja", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Mini Project - Branch Specific", "Theory-4": "Computer Networks", "Theory-5": "Operating Systems"},
        {"Sl.No": 28, "Name of the Teaching Assistant": "V S N S Yashwanth Kommuri", "Theory-1": "Design Thinking and Engineering Orientation", "Theory-2": "Machine Learning", "Theory-3": "Front-End Web Development", "Theory-4": "Algorithm Design and Analysis", "Theory-5": "Python Programming Essentials"},
        {"Sl.No": 29, "Name of the Teaching Assistant": "M Gopi", "Theory-1": "Natural Language Processing", "Theory-2": "Python Programming Essentials", "Theory-3": "Cloud Computing", "Theory-4": "Computer Networks", "Theory-5": "Machine Learning"},
        {"Sl.No": 30, "Name of the Teaching Assistant": "N Meghendra", "Theory-1": "Python Programming Essentials", "Theory-2": "Front-End Web Development", "Theory-3": "Operating Systems", "Theory-4": "Cloud Computing", "Theory-5": "Natural Language Processing"},
        {"Sl.No": 31, "Name of the Teaching Assistant": "Mannava Ganesh", "Theory-1": "Front-End Web Development", "Theory-2": "Python Programming Essentials", "Theory-3": "Mini Project - Branch Specific", "Theory-4": "Full Stack Development", "Theory-5": "Cloud Computing"}
    ]
    df_ta = pd.DataFrame(ta_data)
    df_ta.to_excel(os.path.join(output_dir, "teaching_assistants.xlsx"), index=False)

    # 3. Multi-Year Course Curriculum (18 courses across I Year, II Year, III Year, and M.Tech I Year)
    course_data = [
        # I Year Courses
        {"Year": "I Year", "Course Code": "25CS101", "Course Name": "Python Programming Essentials", "L": 1, "T": 2, "P": 2, "C": 3, "L-T-P-C": "1-2-2-3", "Total_Hours": 5},
        {"Year": "I Year", "Course Code": "25CS102", "Course Name": "Front-End Web Development", "L": 0, "T": 2, "P": 2, "C": 2, "L-T-P-C": "0-2-2-2", "Total_Hours": 4},
        {"Year": "I Year", "Course Code": "25CS103", "Course Name": "Mini Project - Branch Specific", "L": 0, "T": 0, "P": 2, "C": 1, "L-T-P-C": "0-0-2-1", "Total_Hours": 2},

        # II Year Courses
        {"Year": "II Year", "Course Code": "25AM202", "Course Name": "Design Thinking and Engineering Orientation", "L": 0, "T": 2, "P": 0, "C": 1, "L-T-P-C": "0-2-0-1", "Total_Hours": 2},
        {"Year": "II Year", "Course Code": "25CY208", "Course Name": "Algorithm Design and Analysis", "L": 2, "T": 2, "P": 2, "C": 4, "L-T-P-C": "2-2-2-4", "Total_Hours": 6},
        {"Year": "II Year", "Course Code": "25AM205", "Course Name": "Machine Learning", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
        {"Year": "II Year", "Course Code": "25CY301", "Course Name": "Full Stack Development", "L": 2, "T": 0, "P": 4, "C": 4, "L-T-P-C": "2-0-4-4", "Total_Hours": 6},
        {"Year": "II Year", "Course Code": "25CS203", "Course Name": "Digital Logic and Computer Organization", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4},

        # III Year Courses
        {"Year": "III Year", "Course Code": "24AM301", "Course Name": "Natural Language Processing", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
        {"Year": "III Year", "Course Code": "22CY204", "Course Name": "Computer Networks", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
        {"Year": "III Year", "Course Code": "22CY206", "Course Name": "Operating Systems", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4},
        {"Year": "III Year", "Course Code": "22AM801", "Course Name": "Cloud Computing", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
        {"Year": "III Year", "Course Code": "22AM802", "Course Name": "Web and Sequence Data Mining", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},

        # M.Tech I Year Courses
        {"Year": "M.Tech I Year", "Course Code": "26ADB107", "Course Name": "Big Data Analytics", "L": 3, "T": 0, "P": 2, "C": 4, "L-T-P-C": "3-0-2-4", "Total_Hours": 5},
        {"Year": "M.Tech I Year", "Course Code": "26ADB110", "Course Name": "Natural Language Processing", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4},
        {"Year": "M.Tech I Year", "Course Code": "26ADB803", "Course Name": "Generative and Agentic AI", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4},
        {"Year": "M.Tech I Year", "Course Code": "26ADB804", "Course Name": "ML Ops and LLM Ops", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4},
        {"Year": "M.Tech I Year", "Course Code": "26ADB805", "Course Name": "Reinforcement Learning", "L": 2, "T": 0, "P": 2, "C": 3, "L-T-P-C": "2-0-2-3", "Total_Hours": 4}
    ]
    df_courses = pd.DataFrame(course_data)
    df_courses.to_excel(os.path.join(output_dir, "course_details.xlsx"), index=False)
    df_courses.to_excel(os.path.join(output_dir, "courses_multiyear.xlsx"), index=False)

    # 4. Also generate a complete multi-sheet workbook containing all three sheets
    multi_path = os.path.join(output_dir, "multiyear_complete_sample.xlsx")
    with pd.ExcelWriter(multi_path, engine="openpyxl") as writer:
        df_fac.to_excel(writer, sheet_name="Faculty Preferences", index=False)
        df_ta.to_excel(writer, sheet_name="Teaching Assistants", index=False)
        df_courses.to_excel(writer, sheet_name="Course Details", index=False)

    # Also generate faculty experience sheet for backward compatibility with 2-file mode
    exp_rows = []
    for _, f in df_fac.iterrows():
        f_id = f"F{int(f['S.No']):03d}"
        desig = str(f["Designation"])
        # infer role
        d_lower = desig.lower()
        if "dean" in d_lower:
            role = "Dean"
        elif "hod" in d_lower:
            role = "HOD"
        elif "associate" in d_lower:
            role = "Associate Professor"
        elif "assistant" in d_lower or "asst" in d_lower:
            role = "Assistant Professor"
        elif "teaching associate" in d_lower or "teaching assistant" in d_lower or "cap" in d_lower or "era" in d_lower:
            role = "Teaching Associate"
        else:
            role = "Professor"

        for rank in range(1, 6):
            subj = f.get(f"Theory-{rank}")
            if pd.notna(subj) and str(subj).strip():
                clean_subj = str(subj).strip()
                # Estimate realistic experience based on designation
                if role == "Dean":
                    exp_yrs = 12.0
                elif role == "HOD":
                    exp_yrs = 10.0
                elif role == "Professor":
                    exp_yrs = 9.0 - (rank * 0.5)
                elif "Associate" in role:
                    exp_yrs = 7.0 - (rank * 0.5)
                elif "Assistant" in role:
                    exp_yrs = 5.0 - (rank * 0.5)
                else:
                    exp_yrs = 2.5 - (rank * 0.3)
                
                exp_rows.append({
                    "Faculty_ID": f_id,
                    "Subject": clean_subj,
                    "Qualification": "PhD" if "dr." in str(f["Name of the Faculty"]).lower() else "M.Tech",
                    "Skill_Level": "Expert" if exp_yrs >= 8 else ("Advanced" if exp_yrs >= 5 else "Intermediate"),
                    "Experience_Years": max(0.5, exp_yrs),
                    "Preference_Rank": rank,
                    "Role": role
                })
    df_exp = pd.DataFrame(exp_rows)
    df_exp.to_excel(os.path.join(output_dir, "faculty_experience.xlsx"), index=False)

    # Combined single file (faculty_sample_combined.xlsx)
    # Put both preferences and experience into faculty_sample_combined.xlsx
    with pd.ExcelWriter(os.path.join(output_dir, "faculty_sample_combined.xlsx"), engine="openpyxl") as writer:
        df_fac.to_excel(writer, sheet_name="Faculty Preferences", index=False)
        df_ta.to_excel(writer, sheet_name="Teaching Assistants", index=False)
        df_exp.to_excel(writer, sheet_name="Experience & Roles", index=False)

    print("Multi-year dataset and sample files generated successfully!")

if __name__ == "__main__":
    create_multiyear_dataset()
