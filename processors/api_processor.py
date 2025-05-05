import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union

class CollegeDataProcessor:
    """Processes college data from JSON files into pandas DataFrames."""
    
    def __init__(self):
        """Initialize the data processor."""
        pass
    
    def load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load college data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of college data dictionaries
        
        Raises:
            FileNotFoundError: If the specified file doesn't exist
        """
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File not found: {file_path}")
    
    def process_data(self, 
                     data: List[Dict[str, Any]], 
                     selected_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Process college data into a pandas DataFrame.
        
        Args:
            data: List of college data dictionaries
            selected_fields: List of fields to include in the DataFrame (None for all fields)
            
        Returns:
            Processed DataFrame with requested fields
        """
        # Handle empty data
        if not data:
            return pd.DataFrame()
        
        # Convert list of dictionaries directly to DataFrame
        df = pd.DataFrame(data)
        
        # Rename columns for better readability
        column_mapping = {
            'school.name': 'school_name',
            'latest.cost.tuition.in_state': 'tuition_in_state',
            'latest.cost.tuition.out_of_state': 'tuition_out_of_state',
            'latest.completion.rate_suppressed.overall': 'completion_rate'
        }
        
        # Only rename columns that exist in the DataFrame
        rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=rename_dict)
        
        # Filter to selected fields if specified
        if selected_fields:
            # Map any field names to their renamed versions
            mapped_fields = [column_mapping.get(field, field) for field in selected_fields]
            available_fields = [field for field in mapped_fields if field in df.columns]
            df = df[available_fields]
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the college data DataFrame.
        
        Args:
            df: Raw college DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Create a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Fill missing values appropriately
        numeric_columns = cleaned_df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            cleaned_df[col] = cleaned_df[col].fillna(-1)  # Use -1 to indicate missing numeric data
        
        # For non-numeric columns
        string_columns = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            cleaned_df[col] = cleaned_df[col].fillna("Unavailable")
            
        return cleaned_df
    
    def filter_by_value(self, 
                       df: pd.DataFrame, 
                       column: str, 
                       value: Any, 
                       comparison: str = '==') -> pd.DataFrame:
        """
        Filter DataFrame by a column value.
        
        Args:
            df: DataFrame to filter
            column: Column name to filter on
            value: Value to filter by
            comparison: Comparison operator ('==', '>', '<', '>=', '<=', '!=')
            
        Returns:
            Filtered DataFrame
        """


        if comparison == '==':
            return df[df[column] == value]
        elif comparison == '>':
            return df[df[column] > value]
        elif comparison == '<':
            return df[df[column] < value]
        elif comparison == '>=':
            return df[df[column] >= value]
        elif comparison == '<=':
            return df[df[column] <= value]
        elif comparison == '!=':
            return df[df[column] != value]
        else:
            raise ValueError(f"Unsupported comparison operator: {comparison}")
    
    def get_school_by_name(self, df: pd.DataFrame, school_name: str) -> pd.DataFrame:
        """
        Get data for a specific school by name.
        
        Args:
            df: DataFrame containing school data
            school_name: Name of the school to find
            
        Returns:
            DataFrame row for the requested school (empty if not found)
        """
        name_column = 'school_name' if 'school_name' in df.columns else 'school.name'
        return self.filter_by_value(df, name_column, school_name)
    
    def get_basic_stats(self, df: pd.DataFrame, column: str) -> Dict[str, float]:
        """
        Calculate basic statistics for a numeric column.
        
        Args:
            df: DataFrame containing the data
            column: Column to calculate statistics for
            
        Returns:
            Dictionary of statistics
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
            
        # Handle non-numeric columns
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError(f"Column '{column}' is not numeric")
            
        # Calculate statistics
        stats = {
            'mean': df[column].mean(),
            'median': df[column].median(),
            'min': df[column].min(),
            'max': df[column].max(),
            'std': df[column].std()
        }
        
        return stats
    
if __name__ == "__main__":
    processor = CollegeDataProcessor()
    
    try:
        # Get the path to the current directory (where the script is located)
        current_dir = os.getcwd()

        # Navigate to the data directory (subfolder)
        root_dir = "data"

        # Load data
        data = processor.load_data(f"{root_dir}/MA_school_data.json")
        
        # Process into DataFrame
        df = processor.process_data(data)
        
        # Clean data
        clean_df = processor.clean_data(df)
        
        # Display basic info
        print(clean_df)
        # print(f"Loaded {len(clean_df)} schools")
        # print("\nColumns available:")
        # for col in clean_df.columns:
        #     print(f"- {col}")
            
        # Get stats for in-state tuition
        # if 'tuition_in_state' in clean_df.columns:
        #     stats = processor.get_basic_stats(clean_df, 'tuition_in_state')
        #     print("\nIn-State Tuition Statistics:")
        #     for stat, value in stats.items():
        #         print(f"{stat}: ${value:,.2f}")
                
        # Find a specific school
        amherst = processor.get_school_by_name(clean_df, "Amherst College")
        if not amherst.empty:
            print("\nAmherst College:")
            for col in ['school_name', 'tuition_in_state', 'tuition_out_of_state', 'completion_rate']:
                if col in amherst.columns:
                    print(f"{col}: {amherst.iloc[0][col]}")
                    
    except Exception as e:
        print(f"Error: {e}")