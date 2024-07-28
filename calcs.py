import config
import random
import inspect
import numpy as np
from prettytable import PrettyTable

update_needed = False


def display_results(years, result_data):
    table = PrettyTable()
    table.field_names = ["Year", "Age1", "Age2", "Returns", "Savings", "NZ Super", "Retirement Spend", "Educ Assistance", "One-off Help", "One-off Items", "Periodic Expenditure", "Deterministic Balance"]
    
    for i in range(years):
        client1_age = config.client1_age + i
        client2_age = config.client2_age + i if config.individual_or_couple == "couple" else "-"
        table.add_row([
            i, 
            round(client1_age),
            round(client2_age) if isinstance(client2_age, (int, float)) else client2_age,
            round(result_data["annual_deterministic_investment_returns"][i]),
            round(result_data["calculate_savings"][i]), 
            round(result_data["calculate_nz_super"][i]),
            round(result_data["calculate_retirement_expenditures"][i]), 
            round(result_data["children_educational_assistance"][i]), 
            round(result_data["children_one_off_assistance"][i]),
            round(result_data["calculate_one_off_items"][i]),
            round(result_data["calculate_periodic_expenditure"][i]),
            round(result_data["deterministic_balances"][i])
        ])
    print(table)

def simulate_annual_investment_balances():
    deterministic_balances = calculate_deterministic_balances()
    annual_deterministic_investment_returns = calculate_annual_returns(deterministic_balances)
    probabilistic_balances = calculate_probabilistic_balances() if config.investment_probabilistic_approach_yes_or_no == "yes" else []
    
    return deterministic_balances, annual_deterministic_investment_returns, probabilistic_balances

def update_and_display_results():
    result_data = {}
    for func in feeder_functions:
        result_data[func.__name__] = func()
    deterministic_balances, annual_deterministic_investment_returns, _ = simulate_annual_investment_balances()
    result_data["deterministic_balances"] = deterministic_balances
    result_data["annual_deterministic_investment_returns"] = annual_deterministic_investment_returns
    display_results(config.years_to_model + 1, result_data)
    return result_data



def display_balance_scenarios(years, deterministic_balances, probabilistic_balances):
    table = PrettyTable()

    num_scenarios_to_show = min(1, len(probabilistic_balances))

    # Updated field names to include ages
    field_names = ["Year", "Age1", "Deterministic Balance"]
    for i in range(1, num_scenarios_to_show + 1):
        field_names.append(f"Prob Scenario {i}")

    table.field_names = field_names

    for i in range(years):
        client1_age = config.client1_age + i  # Calculate client1_age for each year

        # Updated row to include client1_age
        row = [
            i,
            round(client1_age),  # Add client1_age here
            round(deterministic_balances[i])
        ]

        # Add probabilistic scenarios
        for scenario in probabilistic_balances[:num_scenarios_to_show]:
            row.append(round(scenario[i]))

        table.add_row(row)

    print(table)


def calculate_retirement_expenditures():
    retirement_expenditures = []
    for year in range(config.years_to_model + 1):
        current_year_age = config.benchmark_age + year
        client1_current_age = config.client1_age + year
        client2_current_age = config.client2_age + year if config.individual_or_couple == "couple" else float('inf')

        # Determine initial retirement expenditure
        if client1_current_age >= config.client1_retirement_age or client2_current_age >= config.client2_retirement_age:
            if config.individual_or_couple == "couple":
                if current_year_age >= config.age_when_one_passes_away:
                    expenditure = config.retirement_expenditure_individual
                else:
                    expenditure = config.retirement_expenditure_couple
            else:
                expenditure = config.retirement_expenditure_individual
        else:
            expenditure = 0

        # Adjust for reduction in expenditure
        if current_year_age >= config.age_retirement_expenditure_starts_reducing:
            years_since_reduction_started = current_year_age - config.age_retirement_expenditure_starts_reducing
            reduction_multiplier = (1 - config.retirement_expenditure_annual_reduction) ** years_since_reduction_started

            if config.individual_or_couple == "couple":
                min_expenditure = config.retirement_expenditure_minimum_couple
            else:
                min_expenditure = config.retirement_expenditure_minimum_individual

            expenditure = max(expenditure * reduction_multiplier, min_expenditure)

        retirement_expenditures.append(expenditure)

    return retirement_expenditures

def calculate_savings():
    savings = []  # Initialize an empty list to store savings values for each year

    for year in range(config.years_to_model + 1):
        current_age = config.benchmark_age + year

        # Determine savings rate before retirement
        if current_age < config.client1_retirement_age:
            if current_age < config.savings_rate_change_age:
                result = config.current_savings_rate
            elif current_age < config.savings_rate_change2_age:
                result = config.updated_savings_rate
            else:
                result = config.updated_savings_rate2
        # Handle post-retirement income
        elif year < config.post_retirement_years_of_earned_income:
            result = config.post_retirement_earned_income
        else:
            result = 0

        savings.append(result)

    return savings


def calculate_nz_super():
    nz_super = []
    for year in range(config.years_to_model + 1):
        current_year_age = config.benchmark_age + year
        client1_current_age = config.client1_age + year
        client2_current_age = config.client2_age + year if config.individual_or_couple == "couple" else 0

        if client1_current_age >= config.nz_super_age_eligibility or client2_current_age >= config.nz_super_age_eligibility:
            if config.individual_or_couple == "couple":
                if current_year_age >= config.age_when_one_passes_away:
                    result = config.nz_super_individual
                elif client1_current_age >= config.nz_super_age_eligibility and client2_current_age >= config.nz_super_age_eligibility:
                    result = config.nz_super_couple_both
                else:
                    result = config.nz_super_couple_one_of_two
            else:
                result = config.nz_super_individual
        else:
            result = 0
        nz_super.append(result)
    return nz_super


def calculate_periodic_expenditure():
    periodic_expenditures = []
    for year in range(config.years_to_model + 1):
        current_age = config.benchmark_age + year
        if (current_age >= config.age_periodic_expenditure_begins and
            current_age <= config.age_periodic_expenditure_ends and
            (current_age - config.age_periodic_expenditure_begins) % config.periodic_expenditure_frequency == 0):
            periodic_expenditures.append(config.periodic_expenditure)
        else:
            periodic_expenditures.append(0)
    return periodic_expenditures


def calculate_one_off_items(): # CHECKED MANUALLY, HAPPY WITH
    one_off_items = [] # initialise an empty list
    if config.allow_for_one_off_items_yes_or_no == "yes":
        # the following two sets of variables represent one-off items. The first is the age of the benchmarked client at which the one-off item is to be received. The second is the amount of the one-off item. The two lists are linked by index, ie the first age corresponds to the first amount, the second age corresponds to the second amount, etc.
        one_off_item_ages = [config.one_off_item1_age, config.one_off_item2_age, config.one_off_item3_age, config.one_off_item4_age, config.one_off_item5_age]
        one_off_item_amounts = [config.one_off_item1, config.one_off_item2, config.one_off_item3, config.one_off_item4, config.one_off_item5] 
        for year in range(config.years_to_model + 1):
            current_age = config.benchmark_age + year
            result = 0 
            for i, age in enumerate(one_off_item_ages):
                if current_age == age:
                    result = one_off_item_amounts[i]
                    break
            one_off_items.append(result)
    else:
        for year in range(config.years_to_model + 1):
            one_off_items.append(0)
    return one_off_items  

def calculate_one_off_item_impact():
    one_off_item_impact = []
    for year in range(config.years_to_model + 1):
        current_year_age = config.benchmark_age + year
        if current_year_age == config.age_one_off_item_purchased:
            # Subtract the purchase price
            result = -config.one_off_item_purchase_price
        elif config.age_one_off_item_purchased < current_year_age < config.age_one_off_item_sold:
            # Add ongoing costs for each year the item is owned
            result = -config.one_off_item_ongoing_costs
        elif current_year_age == config.age_one_off_item_sold:
            # Add the sale price
            result = config.one_off_item_sale_price
        else:
            result = 0
        one_off_item_impact.append(result)
    return one_off_item_impact

def children_one_off_assistance():
    annual_one_off_assistance = []
    if (config.providing_substantial_assistance_to_children_yes_or_no == "yes" and
        config.providing_one_off_assistance_to_children_yes_or_no == "yes"):
        number_of_children = int(getattr(config, 'number_of_children', 0))
        # Calculate the year when each child reaches the age for one-off assistance
        assistance_years = [config.age_of_one_off_assistance_to_children - getattr(config, f'child{i}_age') for i in range(1, number_of_children + 1)]

        for year in range(config.years_to_model + 1):
            result = 0
            for assistance_year in assistance_years:
                # Check if the current simulation year matches the year for assistance
                if year == assistance_year:
                    result += config.amount_of_one_off_assistance_to_children
                    break  # Assuming assistance is provided once per child at a specific year
            annual_one_off_assistance.append(result)
    else:
        annual_one_off_assistance = [0] * (config.years_to_model + 1)

    return annual_one_off_assistance

def children_educational_assistance():
    annual_educational_assistance = []
    if (config.providing_substantial_assistance_to_children_yes_or_no == "yes" and
        config.assisting_with_education_for_children_yes_or_no == "yes"):
        number_of_children = int(getattr(config, 'number_of_children', 0))
        education_start_years = [getattr(config, f'education_start_year_child{i}') for i in range(1, number_of_children + 1)]

        for year in range(config.years_to_model + 1):
            result = 0
            for start in education_start_years:
                end = start + config.years_of_providing_educational_assistance - 1
                if year >= start and year <= end:
                    result += config.annual_amount_of_educational_assistance
            annual_educational_assistance.append(result)
    else:
        annual_educational_assistance = [0] * (config.years_to_model + 1)

    return annual_educational_assistance


def _validation(functions_to_validate):
    # This function is to ensure that all functions that feed into simulate_investment_balances are in the correct format. Specifically, a list of values, and that the list is the correct length, ie config.years_to_model + 1. This is to ensure that the simulation function can be run without error.
    expected_length = config.years_to_model + 1
    for func in functions_to_validate:
        result = func()  # Call the function to get its output
        if not isinstance(result, list) or len(result) != expected_length:
            # Perform validation checks and raise an error if needed
            print(f"Validation failed for function {func.__name__}.")
            print(f"Result: {result}")
            print(f"Expected length: {expected_length}")
            if not isinstance(result, list):
                print(f"Result is not a list.")
            else:
                print(f"Actual length: {len(result)}")
            raise ValueError(f"Validation failed for function {func.__name__}.")

feeder_functions = [calculate_retirement_expenditures, calculate_savings, calculate_one_off_item_impact, calculate_nz_super, calculate_one_off_items, children_one_off_assistance, children_educational_assistance, calculate_periodic_expenditure]

_validation(feeder_functions)

def get_rate(balance): # This function will calculate the rate of return for a given balance
    if balance <= config.investment_threshold:
        return config.investment_returns_under_threshold
    else:
        under_amount = config.investment_threshold
        over_amount = balance - config.investment_threshold
        under_rate = config.investment_returns_under_threshold
        over_rate = config.investment_returns_over_threshold
        return (under_amount * under_rate + over_amount * over_rate) / balance

def calculate_deterministic_annual_returns(initial_balance):
    years = config.years_to_model + 1
    annual_returns_in_dollars = []
    balance = initial_balance
    for _ in range(years):
        rate = get_rate(balance)
        annual_return_in_dollars = round(balance * rate)
        annual_returns_in_dollars.append(annual_return_in_dollars)
        balance += annual_return_in_dollars  # Update balance for next year
    
    # Call update_and_display_results after all calculations are done
    update_and_display_results()
    
    return annual_returns_in_dollars






def calculate_annual_returns(deterministic_balances):
    annual_returns = []

    for year_balance in deterministic_balances[:-1]:  # Exclude the last balance as it has no return following it
        rate = get_rate(year_balance)
        annual_returns.append(year_balance * rate)

    return annual_returns


def calculate_deterministic_balances():
    deterministic_balances = [config.opening_investment_balance]
    
    function_results = {func.__name__: func() for func in feeder_functions}

    for year in range(config.years_to_model + 1):
        # Apply yearly changes without the investment return
        year_balance = apply_yearly_changes(deterministic_balances[-1], year, function_results)
        # Apply the deterministic rate of return here
        rate = get_rate(year_balance)
        year_balance += year_balance * rate
        deterministic_balances.append(year_balance)
    
    # Display results after calculations
    display_results(config.years_to_model + 1, {
        "deterministic_balances": deterministic_balances,
        "annual_deterministic_investment_returns": calculate_annual_returns(deterministic_balances),
        **function_results
    })
    
    return deterministic_balances


def calculate_probabilistic_balances():
    # Initialize the probabilistic balances with the opening balance for each scenario
    probabilistic_balances = [[config.opening_investment_balance] for _ in range(config.investment_probabilistic_number_of_scenarios)]
    # Pre-calculate results from feeder functions for use within the loop
    function_results = {func.__name__: func() for func in feeder_functions}

    # Log the configuration value for years_to_model
    # Log the initial length of the first scenario
 
    # Iterate over each year to model
    for year in range(config.years_to_model + 1):
        for scenario in probabilistic_balances:
            # Apply yearly changes without the investment return
            scenario_balance = apply_yearly_changes(scenario[-1], year, function_results)
            
            # Get the rate for the current balance to apply probabilistic changes
            current_rate = get_rate(scenario_balance)
            # Generate a random rate based on the current rate and the standard deviation multiplier
            # Generate a random rate based on the current rate and the standard deviation multiplier
            random_rate = np.random.normal(current_rate, abs(current_rate) * config.investment_probabilistic_methodology_normal_sd_multiplier)
            
            # Apply the probabilistic rate of return
            scenario_balance += scenario_balance * random_rate
            # Append the updated balance to the scenario
            scenario.append(scenario_balance)

        # Log the length of the first scenario after processing each year

    # Return the list of probabilistic balance scenarios
    return probabilistic_balances



def apply_yearly_changes(last_balance, year, function_results):
    # Assume feeder_functions is a list of actual function objects provided elsewhere
    additions_names = ['calculate_savings', 'calculate_nz_super', 'calculate_one_off_items', 'calculate_one_off_item_impact']
    feeder_function_names = [func.__name__ for func in feeder_functions]
    subtractions_names = list(set(feeder_function_names) - set(additions_names))
    yearly_additions = sum(function_results[func_name][year] for func_name in additions_names if func_name in function_results)
    yearly_subtractions = sum(function_results[func_name][year] for func_name in subtractions_names if func_name in function_results)
    year_balance_change = yearly_additions - yearly_subtractions
    return last_balance + year_balance_change



def apply_probabilistic_changes(last_balance, year):
    rate = get_rate(last_balance)
    random_rate = np.random.normal(rate, rate * config.investment_probabilistic_methodology_normal_sd_multiplier)
    return last_balance * (1 + random_rate)

update_and_display_results()