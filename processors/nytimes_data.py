import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np


nyfed_labor_data = pd.read_excel("data/college-labor-data.xlsx", index_col="Major", sheet_name="outcomes by major", header=0, skiprows=10)

stem_degrees = sorted([
    "Agriculture",
    "Animal and Plant Sciences",
    "Environmental Studies",
    "Information Systems & Management",
    "Computer Science",
    "General Engineering",
    "Aerospace Engineering",
    "Chemical Engineering",
    "Civil Engineering",
    "Computer Engineering",
    "Electrical Engineering",
    "Industrial Engineering",
    "Mechanical Engineering",
    "Miscellaneous Engineering",
    "Biology",
    "Biochemistry",
    "Miscellaneous Biological Science",
    "Mathematics",
    "Chemistry",
    "Earth Sciences",
    "Physics",
    "Miscellaneous Physical Sciences",
    "Engineering Technologies",
    "Miscellaneous Technologies"
])

business_degrees = sorted([
    "General Business",
    "Accounting",
    "Business Management",
    "Business Analytics",
    "Marketing",
    "Finance",
    "International Affairs",
    "Health Services",
    "Medical Technicians",
    "Nursing",
    "Pharmacy",
    "Treatment Therapy"
])

humanities_degrees = sorted([
    "Architecture",
    "Ethnic Studies",
    "Communications",
    "Journalism",
    "Mass Media",
    "Advertising and Public Relations",
    "Foreign Language",
    "Family and Consumer Sciences",
    "English Language",
    "Liberal Arts",
    "Philosophy",
    "Theology and Religion",
    "Art History",
    "Fine Arts",
    "Performing Arts",
    "Commercial Art & Graphic Design",
    "History"
])

education_degrees = sorted([
    "General Education",
    "Early Childhood Education",
    "Elementary Education",
    "Secondary Education",
    "Special Education",
    "Miscellaneous Education"
])

social_sciences_degrees = sorted([
    "Psychology",
    "Criminal Justice",
    "Public Policy and Law",
    "Social Services",
    "Anthropology",
    "Economics",
    "Geography",
    "Political Science",
    "Sociology",
    "General Social Sciences"
])

interdisciplinary_studies = sorted([
    'Interdisciplinary Studies',
    'Nutrition Sciences',
    'Leisure and Hospitality',
    'Construction Services'])

# organize data sets by degree categories
stem_group =                nyfed_labor_data.loc[stem_degrees]
business_group =            nyfed_labor_data.loc[business_degrees]
humanties_group =           nyfed_labor_data.loc[humanities_degrees]
education_group =           nyfed_labor_data.loc[education_degrees]
social_sciences_group =     nyfed_labor_data.loc[social_sciences_degrees]
interdisciplinary_group =   nyfed_labor_data.loc[interdisciplinary_studies]

# print chart of all degrees per group
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(stem_group.index, stem_group["Median Wage Early Career"])
ax.set_xlabel("Average Early Degree Earnings")
ax.set_ylabel("Degree Options")
ax.set_title("STEM Degree Earnings Plot")
# ax.tick_params(axis='x', rotation=90)
fig.tight_layout()
plt.show()