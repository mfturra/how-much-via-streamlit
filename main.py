import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
from dotenv import load_dotenv


# Import our custom modules
from services.api_service import CollegeScorecardAPI
from processors.api_processor import CollegeDataProcessor

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="How Much Does Your Occupation Cost?",
    page_icon="💰",
    layout="wide"
)

# Initialize our services (using Streamlit's cache to avoid recreating on each rerun)
@st.cache_resource
def get_api_service():
    """Create or retrieve the API service singleton."""
    return CollegeScorecardAPI()

@st.cache_resource
def get_data_processor():
    """Create or retrieve the data processor singleton."""
    return CollegeDataProcessor()

# Function to load college data with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_college_data(state_code, file_path):
    """Load college data from API with caching."""
    processor = get_data_processor()
    try:
        data = processor.load_data(file_path)
        df = processor.process_data(data)
        return processor.clean_data(df)
    except Exception as e:
        st.error(f"Error loading college data: {str(e)}")
        return pd.DataFrame()

# Function to load occupation data with caching
@st.cache_data
def load_occupation_data(file_path):
    """Load occupation data from a CSV file."""
    try:
        data = pd.read_csv(file_path, sep='|', index_col=False)
        return data.sort_values('College Degree')
    except Exception as e:
        st.error(f"Error loading occupation data: {str(e)}")
        return pd.DataFrame()
    
# Function to fetch fresh data from API
def fetch_college_data(state_code):
    """Fetch college data from API and save to file."""
    api = get_api_service()
    
    fields = [
        'id',
        'school.name',
        'school.state',
        'latest.cost.tuition.in_state',
        'latest.cost.tuition.out_of_state',
        'latest.completion.rate_suppressed.overall'
    ]
    
    try:
        data = api.get_all_schools(state=state_code, fields=fields)
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save to a file in the data directory
        filename = os.path.join('data', f"{state_code}_school_data.json")
        api.save_results_to_json(data, filename)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []
    
# Function to ensure data is available (either from cache or freshly fetched)
def get_college_data(state_code):
    """Get college data, fetching from API if necessary."""
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, f"{state_code}_school_data.json")
    
    # Check if file exists and is recent (less than 24 hours old)
    if os.path.exists(file_path):
        file_age = datetime.now().timestamp() - os.path.getmtime(file_path)
        if file_age < 86400:  # 24 hours in seconds
            return load_college_data(file_path)
    
    # If file doesn't exist or is old, fetch fresh data
    data = load_college_data(state_code)
    if data:
        return fetch_college_data(file_path)
    return pd.DataFrame()

# ---------- Main App ----------
st.title("How Much Does Your Occupation Cost?")
project_desc = "Every year graduates from universities and colleges across the U.S.A. leave with debt. This projects hope is to bring undergrads some price transparency to teach them how much their degree will cost in the long run...even after they leave college."

# output project description
st.write(project_desc)
st.divider()


# ---------- Data Loading Section ----------
# Sidebar with minimal options focused on MA data only
with st.sidebar:
    st.header("Massachusetts College Data")
    
    # Create data directory if it doesn't exist
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Set fixed file paths (hidden from user)
    ma_file_path = os.path.join(data_dir, "MA_school_data.json")
    occupation_file = os.path.join(data_dir, "occupational_data.csv")
    
    # Show when data was last updated
    if os.path.exists(ma_file_path):
        last_updated = datetime.fromtimestamp(os.path.getmtime(ma_file_path))
        st.info(f"Data last updated: {last_updated.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.warning("MA college data not found")

    # Simple refresh button
    if st.button("Refresh Massachusetts College Data"):
        with st.spinner("Fetching latest data for Massachusetts colleges..."):
            data = fetch_college_data("MA")
            if data:
                st.success(f"Successfully updated data for {len(data)} Massachusetts colleges")
            else:
                st.error("Failed to fetch data")
    
    
# ---------- Load and Process Data ----------
# Load college data
college_df = load_college_data("MA", "data/MA_school_data.json")

# Ensure college data is formatted correctly
if not college_df.empty:
    # Fix column names if needed
    name_column = 'school_name' if 'school_name' in college_df.columns else 'school.name'
    tuition_column = 'tuition_in_state' if 'tuition_in_state' in college_df.columns else 'latest.cost.tuition.in_state'
    state_column = 'school_state' if 'school_state' in college_df.columns else 'school.state'
    
    # Create a standardized view for the app
    if "df" not in st.session_state or st.session_state.df.empty:
        st.session_state.df = pd.DataFrame({
            'school name': college_df[name_column],
            'school state': college_df[state_column] if state_column in college_df.columns else 'MA',
            'school tuition': college_df[tuition_column]
        })
else:
    st.error(f"Could not load college data from {ma_file_path}")
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame({'school name': [], 'school state': [], 'school tuition': []})

# Load occupation data
occupation_df = load_occupation_data("data/occupational_data.csv")


#---------- Main Content ----------
# Student scholastic details
st.subheader("Estimated Tuition Costs")
st.write("Which college/university are you planning to or are currently attending in Massachusetts?")

# Layout for selection
col1, col2 = st.columns(2)

# College selection
school_options = st.session_state.df['school name'].dropna().unique()
school_sel = col1.selectbox(
    "*University Attending", 
    school_options,
    index=None, 
    placeholder="University Options", 
    label_visibility="visible"
)

# Display selected college information
if school_sel:
    selected_school_info = st.session_state.df[st.session_state.df['school name'] == school_sel]
    
    if not selected_school_info.empty:
        col5, col6 = st.columns(2)
        tuition = selected_school_info['school tuition'].iloc[0]
        
        # if tuition:
        #     semester_cost = col5.number_input("*Cost of Tuition Per Semester", value=tuition, placeholder="Amount in USD", label_visibility="visible")
        # else:
        #     semester_cost = col5.number_input("*Cost of Tuition Per Semester", min_value=0, max_value=100000, placeholder="Amount in USD", label_visibility="visible")


        any_loans = col5.selectbox("*Did you have to take out any loans?",
                                ('Yes','No'), index=None, label_visibility="visible")

        scholarship = col6.number_input("Amount of Scholarship Earned Per Year", min_value=0, max_value=100000, placeholder="Amount in USD")
        scholarship_savings = scholarship

        col2.metric(
            "Annual Tuition", 
            f"${tuition:,.2f}" if pd.notna(tuition) and tuition != -1 else "Not Available"
        )
        
        # Calculate 4-year cost
        if pd.notna(tuition) and tuition != -1:
            yearly_cost = tuition - scholarship_savings
            four_year_cost = (tuition - scholarship_savings) * 4
            st.metric(
                "Estimated 4-Year Cost (with scholarship) *Does not consider financial aid)",
                f"${four_year_cost:,.2f}"
            )
st.divider()

st.write("    \n\n\n")
if school_sel:
    st.subheader("Actual Tuition Costs*")
    st.write(f"What degree are you pursuing at {school_sel}?")
else:
    st.write(f"What degree are you pursuing?")

# degree options
undergrad_stat = {'Freshman': 4, 'Sophmore': 3, 'Junior': 2, 'Senior': 1}

col3, col4 = st.columns(2)
deg_sel =           col3.selectbox("*Degree Pursuing",
                          occupation_df['College Degree'].dropna().unique(),
                          index=None, placeholder="Degree Options", label_visibility="visible")
college_year =      col4.selectbox("*Current year in college",
                                   list(undergrad_stat.keys()), index=None, placeholder="College Year Options", 
                                   label_visibility="visible")
st.write("*Calculations are based on academic year")


# # Student Loan Financials
st.write("#### Financial Terms for Academic Pursuit")
if college_year is not None:
    years_left = undergrad_stat[college_year]

    if any_loans is not None:

        if any_loans == 'Yes':
            st.write("    \n\n\n")
            st.write("Please specify your loan conditions to receive the most accurate insights")
            # loan_rate = col4.number_input("What was your loan amount")
            loan_rate = st.slider("What is your loan rate (%)", min_value=0.5, max_value=20.0, step=0.1, label_visibility="visible")
            st.write(f"Actual Loan Rate: {loan_rate:.1f}%")

            if loan_rate > 0:
                # amount due at end of college experience
                yearly_interest_due =  (loan_rate * 10**-2) * yearly_cost
                total_interest_due = years_left * yearly_interest_due
                total_balance_w_interest = (yearly_cost * years_left) + total_interest_due
                st.write("*Assuming your tuition and scholarship money doesn't change throughout your academic career")
                st.metric(
                    "You'll owe this much when you're done:",
                    f"${total_balance_w_interest:,.2f}"
                )
                
                # st.write(f"You'll owe this much when you're done: **${sem_amount_due:.2f}**")

                loan_term_years = st.slider("What is your loan term (Years)", min_value=1, max_value=30, value=10)
                start_date = st.date_input("Loan Start Date", value=datetime.today())
                monthly_rate = loan_rate / 100 / 12
                num_payments = loan_term_years * 12
                monthly_payment = total_balance_w_interest * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
                st.metric(
                    "Your estimated monthly payment is:",
                    f"${monthly_payment:,.2f}"
                )
                # st.write(f"Your estimated monthly payment is: **${monthly_payment:,.2f}**")

            
        else:
            st.write("You're not going to own anything! Congratulations!")

# df = st.session_state.df
# df['school tuition'] = df['school tuition'].fillna("NaN")

# if school_sel is not None:
#     # school_update = st.session_state.df["school tuition"].fillna("Unavailable")

#     school_tuition = st.session_state.df[st.session_state.df["school name"] == school_sel]['tuition_in_state'].iloc[0]

#     if pd.notna(school_tuition):
#         with col2:
#             st.write(f"Your estimated tuition costs are: ${school_tuition:,.2f}")
#     else:
#         with col1:
#             st.write(f"Your schools estimated tuition costs are unavailable.")

    

# ---------- Footer ----------
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
