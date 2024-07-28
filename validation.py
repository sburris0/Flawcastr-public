import config
import calcs
import random
from prettytable import PrettyTable
import datetime
import sys
import io
import pandas as pd

def generate_base_table():
    # Generate the base table using default config values
    return calcs.update_and_display_results()

def modify_variable(var_name, original_value):
    # Modify a variable randomly
    if isinstance(original_value, bool):
        return not original_value
    elif isinstance(original_value, int):
        new_value = original_value + random.randint(-10, 10)
        return new_value if new_value != 0 else original_value + 1  # Ensure new_value is not zero
    elif isinstance(original_value, float):
        new_value = original_value * random.uniform(0.5, 1.5)
        return new_value if new_value != 0 else original_value * 1.1  # Ensure new_value is not zero
    elif isinstance(original_value, str):
        return original_value  # For now, we don't modify string values
    else:
        return original_value

def adjust_year_column(dataframe, base_year_col='Age1'):
    # Adjust 'Year' to start from the first value in 'base_year_col'
    opening_year = dataframe[base_year_col].iloc[0]
    dataframe['Adjusted_Year'] = dataframe['Year'] + opening_year

    # Ensure 'Adjusted_Year' has unique values
    dataframe['Adjusted_Year'] = dataframe['Adjusted_Year'].astype(int)
    dataframe = dataframe.drop_duplicates(subset=['Adjusted_Year'])

    return dataframe

def run_validation():
    # Create a filename with the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"validation_{current_time}.txt"
    
    # Redirect stdout to capture print output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    base_results = generate_base_table()
    print("Base scenario:")
    calcs.display_results(config.years_to_model + 1, base_results)

    config_vars = {attr: getattr(config, attr) for attr in dir(config) 
                   if not callable(getattr(config, attr)) and not attr.startswith("__")}
    
    var_names = list(config_vars.keys())
    random.shuffle(var_names)

    modifications_per_var = 2

    for var_name in var_names:
        original_value = config_vars[var_name]
        
        for _ in range(modifications_per_var):
            temp_config_vars = config_vars.copy()
            
            new_value = modify_variable(var_name, original_value)
            temp_config_vars[var_name] = new_value
            
            for attr, value in temp_config_vars.items():
                setattr(config, attr, value)
            
            modified_results = calcs.update_and_display_results()
            
            print(f"\nModified scenario: {var_name} changed from {original_value} to {new_value}")
            calcs.display_results(config.years_to_model + 1, modified_results)
            
            for attr, value in config_vars.items():
                setattr(config, attr, value)

    # Get the captured output
    output = sys.stdout.getvalue()

    # Restore stdout
    sys.stdout = old_stdout

    # Write the captured output to a file
    with open(filename, 'w') as f:
        f.write(output)

    print(f"Validation results saved to {filename}")

if __name__ == "__main__":
    run_validation()
