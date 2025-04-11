import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# # Initialization
# if 'key' not in st.session_state:
#     st.session_state['key'] = 'value'

# # Session State also supports attribute based syntax
# if 'key' not in st.session_state:
#     st.session_state.key = 'value'

# outline app purpose
st.title("How Much Does Your Occupation Cost?")
project_desc = "Every year graduates from universities and colleges across the U.S.A. leave with debt. This projects hope is to bring undergrads some price transparency to teach them how much their degree will cost in the long run...even after they leave college."


# output project description
st.write(project_desc)
st.divider()

# import and process school data
file_path = "MA_school_pull"

try:
    with open(file_path, 'r') as file:
        all_results = json.load(file)
        filt_results = all_results[2:]

        school_names = []
        school_states = []
        school_tuitions = []
    
        for entry in filt_results:
            if "latest" in entry:
                school_name = entry["latest"]["school"]["name"]
                school_names.append(school_name)
                school_state = entry["latest"]["school"]["state"]
                school_states.append(school_state)
                school_tuition = entry["latest"]["cost"]["tuition"]["in_state"]
                school_tuitions.append(school_tuition)

    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame({'school name': school_names, 'school state': school_states, 'school tuition': school_tuitions})

except FileNotFoundError:
    print(f"Error: File not found: {file_path}")

df = st.session_state.df
# df['school tuition'] = df['school tuition'].fillna("NaN")



# import and process occupational data
data = pd.read_csv('occupational_data.csv', sep='|', index_col=False)
data_ascd = data.sort_values('College Degree')


# gather input from user
# school options in MA
st.write("Which college/university are you planning to or are currently attending in Massachusetts?")

# outline structure of data presentation
col1, col2 =    st.columns(2)
school_sel =    col1.selectbox("*University Attending",
                                st.session_state.df['school name'].unique(),
                                index=None, placeholder="University Options", 
                                label_visibility="visible")

if school_sel is not None:
    # school_update = st.session_state.df["school tuition"].fillna("Unavailable")

    school_tuition = df[df["school name"] == school_sel]['school tuition'].iloc[0]

    if pd.notna(school_tuition):
        with col2:
            st.write(f"Your estimated tuition costs are: ${school_tuition:,.2f}")
    else:
        with col1:
            st.write(f"Your schools estimated tuition costs are unavailable.")

# st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

if school_sel:
    st.write(f"What degree are you pursuing at {school_sel}?")
col3, col4 = st.columns(2)
# degree options
undergrad_stat = {'Freshman': 4, 'Sophmore': 3, 'Junior': 2, 'Senior': 1}

deg_sel =           col3.selectbox("*Degree Pursuing",
                          data_ascd['College Degree'].dropna().unique(),
                          index=None, placeholder="Degree Options", label_visibility="visible")
college_year =      col4.selectbox("*Current year in college",
                                   list(undergrad_stat.keys()), index=None, placeholder="College Year Options", 
                                   label_visibility="visible")
if school_tuition:
    semester_cost = col3.number_input("Cost of Tuition Per Semester", value=school_tuition, placeholder="Amount in USD", label_visibility="visible")
else:
    semester_cost = col3.number_input("Cost of Tuition Per Semester", min_value=0, max_value=100000, placeholder="Amount in USD", label_visibility="visible")
scholarship = col4.number_input("Amount of Scholarship Earned Per Semester", min_value=0, max_value=100000, placeholder="Amount in USD")
any_loans = col3.selectbox("*Did you have to take out any loans?",
                           ('Yes','No'), index=None, label_visibility="visible")
if college_year is not None:
    years_left = undergrad_stat[college_year]

    if any_loans is not None:

        if any_loans == 'Yes':
            # loan_rate = col4.number_input("What was your loan amount")
            loan_rate = st.slider("What was your loan rate (%)", min_value=0.5, max_value=20.0, step=0.1, label_visibility="visible")
            st.write(f"Actual Loan Rate: {loan_rate:.1f}%")

            if loan_rate > 0:
                # amount due at end of college experience
                sem_amount_due =  (loan_rate * 10**-2) * (semester_cost - scholarship) + (semester_cost - scholarship)
                total_amount_due = years_left * sem_amount_due
                st.write("*Assuming your tuition and scholarship money doesn't change throughout your academic career")
                st.write(f"You'll owe this much when you're done: ${sem_amount_due:.2f}")
            
        else:
            st.write("You're not going to own anything! Congratulations!")


st.markdown("""
    <style>
        .footer {
            position: sticky;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            margin-top: 50px;
            padding: 10px;
        }
    </style>
    <div class="footer">
        <p>The data presented here is sourced from the <a href="https://collegescorecard.ed.gov/" target="_blank">College Scorecard</a> and <a href="https://www.bls.gov/" target="_blank">U.S. Bureau of Labor Statistics</a>.</p>
        <p>While every effort has been made to ensure accuracy, the data is for informational purposes only. Please verify all information independently.</p>
    </div>
""", unsafe_allow_html=True)


# if deg_sel is not None: 
#     entry_row = (data_ascd[data_ascd['College Degree'].isin({deg_sel})])
    
#     # description of occupation
#     occupation = entry_row['Detailed Occupation'].iloc[0]
#     occ_desc = entry_row['Description'].iloc[0]

#     st.write("##### Prospective Occupations")
#     st.write(occupation)
#     st.write("##### Description of Occupation")
#     st.write(occ_desc)

#     # financial benefits of occupation
#     hourly_wage = entry_row['Mean Hourly Wage'].iloc[0]
#     annual_wage = entry_row['Mean Annual Wage'].iloc[0]

#     st.write("##### Average Hourly Earnings")
#     st.write(hourly_wage)
#     st.write("##### Average Yearly Earnings")
#     st.write(annual_wage)


# output 
# print(data.iloc[:, degree_val])
# print(data['Detailed Occupation'].isin([degree_val]))

# check if selection is in column
# if degree_val in data['College Degree'].values:
#     print(data[data['Detailed Occupation'].isin([degree_val])])
    # st.write(f"Potential Occupations: {data['Detailed Occupation']}\n Prospective Avg. Hourly Rate: {data['Mean Hourly Wage']}\n Prospective Avg Annual Wage: {data['Mean Annual Wage']}")

# st.write("### What is your profession of interest?")
# st.write("### What is your profession of interest?")



# # st.title("How much does your degree cost?")
# st.table(data)
