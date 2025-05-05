import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# ingest .env vars
BASE_URL =      os.getenv('DOMAIN')
API_KEY =       os.getenv('COLLEGE_SCORECARD_API')
state =         'MA'
base_page =     0
results_per_page =   100

all_results = []
url = f'{BASE_URL}?api_key={API_KEY}&school.state=MA&fields=id,school.name,state,latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,latest.completion.rate'

# &school.state={state}&page={base_page}&per_page={results_per_page}'

# A GET request to the API
api_response = requests.get(url)
pretty_response = json.loads(api_response.text)
all_results.extend(pretty_response['results'])


# extract insights for pagination
total_results = pretty_response["metadata"]["total"]
total_pages = (total_results + results_per_page - 1) // results_per_page
# print(total_pages)


for page in range(1, total_pages):
    full_data_url = f"{BASE_URL}?api_key={API_KEY}&school.state={state}&page={page}&per_page={results_per_page}"
    full_request = requests.get(full_data_url)
    full_pretty_response = json.loads(full_request.text)

    all_results.extend(pretty_response['results'])
    print(f"Current page number: {page}")
#     all_results.extend(pretty_response['results'])




# extract specific data from pulled data set
# for i in range(20):
#     school_name = all_results["results"][i]["latest"]["school"]["name"]
#     school_state = all_results["results"][i]["latest"]["school"]["state"]
#     school_tuition = all_results["results"][i]["latest"]["cost"]["tuition"]["in_state"]
#     print(f"{school_name} yearly cost: ${school_tuition} \n")






# create a file with the necessary json payload
create_json_file = True
if create_json_file:
    filename = 'MA_school_pull'
    with open(filename, 'w') as file:
        json.dump(all_results, file, indent=4)

    print(f"JSON data written to '{filename}' successfully.")