import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv


class CollegeScorecardAPI:
    """Service class for interacting with the College Scorecard API."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the College Scorecard API service.
        
        Args:
            base_url: Base URL for the College Scorecard API (currently in .env)
            api_key: API key for authentication (currently in .env)
        """

        # Load environment variables
        load_dotenv()

        # Use provided values or fall back to environment variables
        self.base_url = base_url or os.getenv('DOMAIN')
        self.api_key = api_key or os.getenv('COLLEGE_SCORECARD_API')

        if not self.base_url or not self.api_key:
            raise ValueError("Missing required API configuration. Provide base_url and api_key "
                             "either as parameters or in your .env file.")

        # Create a session for connection pooling and consistent headers
        self.session = requests.Session()

    def get_schools(self, 
                    state: Optional[str] = None,
                    fields: Optional[List[str]] = None,
                    page: int = 0,
                    per_page: int = 100,
                    **additional_filters) -> Dict[str, Any]:
        """
        Fetch school data from the College Scorecard API.
        
        Args:
            state: Two-letter state code to filter schools by state
            fields: List of fields to include in the response
            page: Page number for pagination (0-indexed)
            per_page: Number of results per page
            additional_filters: Any additional query parameters to include
            
        Returns:
            API response as a dictionary
        """
        # Build query parameters
        params = {
            'api_key': self.api_key,
            'page': page,
            'per_page': per_page
        }
        
        # Add state filter if provided
        if state:
            params['school.state'] = state
            
        # Add fields if provided
        if fields:
            params['fields'] = ','.join(fields)
            
        # Add any additional filters
        params.update(additional_filters)
        
        # Make the API request
        response = self.session.get(self.base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        return response.json()
    
    def get_all_schools(self, 
                       state: Optional[str] = None,
                       fields: Optional[List[str]] = None,
                       per_page: int = 100,
                       max_pages: Optional[int] = None,
                       **additional_filters) -> List[Dict[str, Any]]:
        """
        Fetch all school data across multiple pages.
        
        Args:
            state: Two-letter state code to filter schools by state
            fields: List of fields to include in the response
            per_page: Number of results per page
            max_pages: Maximum number of pages to fetch (None for all)
            additional_filters: Any additional query parameters to include
            
        Returns:
            List of school data dictionaries
        """
        all_results = []
        page = 0
        
        # Get first page to determine total pages
        first_response = self.get_schools(
            state=state,
            fields=fields,
            page=page,
            per_page=per_page,
            **additional_filters
        )
        
        # Extract metadata
        total_results = first_response.get("metadata", {}).get("total", 0)
        total_pages = (total_results + per_page - 1) // per_page if total_results > 0 else 0
        
        # Limit pages if specified
        if max_pages is not None:
            total_pages = min(total_pages, max_pages)
            
        # Add results from first page
        all_results.extend(first_response.get("results", []))
        
        # Fetch remaining pages
        for page in range(1, total_pages):
            print(f"Fetching page {page+1} of {total_pages}")
            page_response = self.get_schools(
                state=state,
                fields=fields,
                page=page,
                per_page=per_page,
                **additional_filters
            )
            all_results.extend(page_response.get("results", []))
            
        return all_results
    
    def save_results_to_json(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Save API results to a JSON file.
        
        Args:
            data: List of data dictionaries to save
            filename: Name of the file (without extension)
            
        Returns:
            Path to the saved file
        """
        # Get the path to the current directory (where the script is located)
        current_dir = os.getcwd()

        # Navigate to the data directory (subfolder)
        root_dir = "data" 
        
        # Add .json extension if not present
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        output_path = os.path.join(root_dir, filename)
            
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=4)
            
        print(f"JSON data written to '{filename}' successfully.")
        return filename


if __name__ == "__main__":
    # Create API service
    api = CollegeScorecardAPI()
    
    # Define fields to retrieve
    fields = [
        'id',
        'school.name',
        'school.state',
        'latest.cost.tuition.in_state',
        'latest.cost.tuition.out_of_state',
        'latest.completion.rate'
    ]
    
    # Get all schools in Massachusetts
    ma_schools = api.get_all_schools(
        state='MA',
        fields=fields,
        per_page=100
    )

    # Save results to file
    api.save_results_to_json(ma_schools, 'MA_school_data.json')