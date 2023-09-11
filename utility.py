import re

# Inverts ratio (Such as turning miles-per-truck to trucks-per-mile)
def invert_ratio(ratio):
    return 1 / ratio


# Take a name and converts to name following sqlite3 table naming conventions
def convert_to_sql_name(name):
    # Remove leading and trailing whitespaces and replace spaces with underscores
    table_name = name.strip().replace(" ", "_")

    # Insert underscores before capital letters (without adding an underscore if one exists) and convert to lowercase
    table_name = re.sub(r'(?<!_)([a-z])([A-Z])', r'\1_\2', table_name).lower()

    # Remove any characters that are not allowed in SQL table names
    allowed_characters = "abcdefghijklmnopqrstuvwxyz0123456789_"
    table_name = "".join(c for c in table_name if c in allowed_characters)

    return table_name


# Checks a value to confirm it is a positive int
def check_valid_int(value):
        try:
            int_value = int(value)
            if int_value < 0:
                print("Error: Value cannot be negative.")
                return False
            else:
                return True
        except ValueError:
            print("Error: Value is not an integer.")
            return False


# Checks input to confirm it is a positive integer. If invalid input is given, user is notified and loop repeats
def get_valid_int_input(prompt):
    while True:
        try:
            user_input = int(input(prompt))
            if user_input < 0:
                print("Invalid input. Please enter a non-negative number.")
            else:
                return user_input
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


# Create final recommendation for department by choosing the highest of all requirements/recommendations and include
#   which recommendation was chosen
def get_recommendation_and_source(minimum_requirement, square_mileage_recommendation, call_volume_recommendation):
    final_recommendation = max(minimum_requirement, square_mileage_recommendation, call_volume_recommendation)
    if max(minimum_requirement, square_mileage_recommendation, call_volume_recommendation) == minimum_requirement:
        recommendation_source = "minimum requirement"
    elif max(minimum_requirement, square_mileage_recommendation,
             call_volume_recommendation) == square_mileage_recommendation:
        recommendation_source = "square mileage"
    elif max(minimum_requirement, square_mileage_recommendation,
             call_volume_recommendation) == call_volume_recommendation:
        recommendation_source = "call volume"
    return final_recommendation, recommendation_source


# Template to get input from user based on prompt and available options
def get_input(prompt, options):
    selection = input(prompt + " (" + options + "): ")
    return selection


