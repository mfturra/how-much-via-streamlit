import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

# outline app purpose
st.write("### How Much Does Your Occupation Cost?")
project_desc = "Every year graduates from universities and colleges across the U.S.A. leave with debt. This projects hope is to bring undergrads some price transparency to teach them how much their degree will cost in the long run...even after they leave college."

# 
st.write(project_desc)

# import and process data
data = pd.read_csv('occupational_data.csv', sep='|', index_col=False)
data_ascd = data.sort_values('College Degree')

# outline structure of data presentation
col1, col2 = st.columns(2)

# gather input from user
# present a dropdown list of available degree options
undergrad_stat = {'Freshman': 4, 'Sophmore': 3, 'Junior': 2, 'Senior': 1}

deg_sel =           col1.selectbox("Degree Pursuing",
                          data_ascd['College Degree'].dropna().unique(),
                          index=None, placeholder="Degree Options", label_visibility="visible")
college_year =      col2.selectbox("Current year in college",
                                   list(undergrad_stat.keys()), index=None, placeholder="College Year Options", 
                                   label_visibility="visible")

semester_cost = col1.number_input("Cost of Tuition Per Semester", min_value=0, max_value=100000, placeholder="Amount in USD", label_visibility="visible")
scholarship = col2.number_input("Amount of Scholarship Earned Per Semester", min_value=0, max_value=100000, placeholder="Amount in USD")
any_loans = col1.selectbox("Did you have to take out any loans?",
                           ('Yes','No'), index=None, label_visibility="visible")
if college_year is not None:
    years_left = undergrad_stat[college_year]

    if any_loans is not None:

        if any_loans == 'Yes':
            loan_rate = col2.number_input("What was your loan amount")

            if loan_rate > 0:
                # amount due at end of college experience
                sem_amount_due =  (loan_rate * 10**-2) * (semester_cost - scholarship) + (semester_cost - scholarship)
                st.write("Assuming your tuition and scholarship money doesn't change throughout your academic career, you'll owe this much when you're done")
                st.write(f"${sem_amount_due:.2f}")
            
        else:
            st.write("You're not going to own anything! Congratulations!")




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
