import spacy
from spacy.matcher import PhraseMatcher
from utils import resume_data


nlp = spacy.load("en_core_web_sm")

job_title_skills = {
    "Java Developer": ["Java", "Spring Boot", "Hibernate", "Maven", "REST APIs", "Git", "JUnit", "SQL"],
    "Testing": ["Manual Testing", "Automation Testing", "Selenium", "JUnit", "TestNG", "Bugzilla", "LoadRunner"],
    "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "Ansible", "Terraform", "AWS", "Git", "CI/CD", "Linux"],
    "Python Developer": ["Python", "Flask", "Django", "Pandas", "NumPy", "REST APIs", "Git", "SQL", "FastAPI"],
    "Web Designing": ["HTML", "CSS", "JavaScript", "Bootstrap", "Figma", "Adobe XD", "UX/UI", "Photoshop"],
    "HR": ["MS Excel", "HRIS", "ATS", "Workday", "Zoho Recruit", "Payroll Software", "Google Workspace"],
    "Hadoop": ["Hadoop", "MapReduce", "Hive", "Pig", "Sqoop", "HDFS", "Spark", "Oozie"],
    "Blockchain": ["Solidity", "Ethereum", "Web3.js", "Hyperledger", "Smart Contracts", "Truffle", "Metamask"],
    "ETL Developer": ["Informatica", "Talend", "SSIS", "SQL", "Python", "Data Warehousing", "DataStage"],
    "Operations Manager": ["MS Excel", "SAP ERP", "CRM Tools", "Tableau", "Project Management Software"],
    "Data Science": ["Python", "R", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "SQL", "Jupyter", "Machine Learning", "Deep Learning"],
    "Sales": ["Salesforce", "CRM", "MS Excel", "Google Sheets", "Data Analysis", "HubSpot"],
    "Mechanical Engineer": ["AutoCAD", "SolidWorks", "CATIA", "Ansys", "MATLAB", "GD&T", "Creo"],
    "Arts": ["Adobe Photoshop", "Illustrator", "InDesign", "CorelDRAW", "Blender", "Premiere Pro"],
    "Database": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle DB", "PL/SQL", "DBMS"],
    "Electrical Engineering": ["MATLAB", "Simulink", "PCB Design", "PSpice", "Multisim", "AutoCAD Electrical"],
    "Health and fitness": ["BMI Calculator Tools", "Nutrition Apps", "Fitness Trackers", "Excel for diet planning"],
    "PMO": ["MS Project", "JIRA", "Confluence", "Trello", "Gantt Charts", "Excel", "Risk Analysis"],
    "Business Analyst": ["Excel", "Power BI", "SQL", "Tableau", "JIRA", "BRD", "Wireframing Tools"],
    "DotNet Developer": ["C#", "ASP.NET", ".NET Core", "MVC", "SQL Server", "LINQ", "Visual Studio"],
    "Automation Testing": ["Selenium", "TestNG", "JUnit", "Jenkins", "Appium", "Cucumber", "Postman"],
    "Network Security Engineer": ["Wireshark", "Kali Linux", "Firewalls", "IDS/IPS", "Cisco ASA", "Nmap", "VPN", "OpenSSL"],
    "SAP Developer": ["SAP ABAP", "SAP Fiori", "SAP HANA", "BAPI", "SAP UI5", "ALV Reports"],
    "Civil Engineer": ["AutoCAD", "STAAD Pro", "Revit", "MS Project", "ETABS", "Primavera"],
    "Advocate": ["Manupatra", "SCC Online", "MS Word", "Legal Drafting", "Case Management Software"]
}

all_skills = list(set(skill.lower() for skills in job_title_skills.values() for skill in skills))

matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(skill) for skill in all_skills]
matcher.add("SKILLS", patterns)

def extract_skills_from_text(file):
    """
    Extracts known hard skills from the given resume text.

    Args:
        text (str): The resume or job description text.

    Returns:
        List[str]: A list of matched skills (in lowercase).
    """

    text , _ = resume_data(file)
    doc = nlp(text.lower())
    matches = matcher(doc)

    found_skills = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        found_skills.add(span.text)

    return list(found_skills)


def missingskills(labels , skills):
    missingskills = []
    for label in labels:
        required_skills = [sk.lower() for sk in job_title_skills[label]]
        missing = set(required_skills) - set(skills)
        missingskills.append([label,missing])
    return missingskills



