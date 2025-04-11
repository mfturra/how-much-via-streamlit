import json
import pandas as pd
from dotenv import load_dotenv

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
                # print(f"School name:{school_name}\nState: {school_state} \nCost: ${school_tuition}\n\n")

    school_data = pd.DataFrame({'school name': school_names, 'school state': school_states, 'school tuition': school_tuitions})
        # for i in range(1, 140):
        #     school_name = filt_results["latest"]["school"]["name"]
        #     print(school_name)
    # school_of_interest = "Anna Maria College"
    # index_data = school_data[school_data["school name"] == school_of_interest]['school tuition'].iloc[0]

    raw_school_data = pd.DataFrame({'school name': school_names, 'school state': school_states, 'school tuition': school_tuitions})
    school_data = raw_school_data["school tuition"].fillna("Unavailable")


    # index_data = school_data.query('"school name" == "Amherst College"')['school tuition']
    print(school_data)
except FileNotFoundError:
    print(f"Error: File not found: {file_path}")

# extract specific data from pulled data set

    # school_state = all_results["results"][i]["latest"]["school"]["state"]
    # school_tuition = all_results["results"][i]["latest"]["cost"]["tuition"]["in_state"]
    # print(f"{school_name} yearly cost: ${school_tuition}  |   Located in: {school_state} \n")


