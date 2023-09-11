import copy
import sqlite3

import database
import utility
from database import database_close
from department import Department
from machine_learning import predict_all_actual_call_volume
from visuals import plot_call_volume_predictions, plot_call_volume_data


# Create or retrieve department by name based on input
def init_department():
    # Get department name from user
    name = input("\nPlease enter department name (Note that this is case sensitive): ")

    # Init Department. If department exists, use that data; if not, create new (See Department init).
    department = Department(name, True)
    if department.login_success is True:
        print("Department: " + department.name + " successfully initialized. Please make sure to save applicable "
                                                 "settings and values before closing the program to prevent losing data.")
    return department


# Initializes CLI menu to present prompt for user input and compare input to available options. If appropriate option
#   is selected, perform corresponding action for department using option, action pairs
def menu_prompt(prompt, option_action_pairs, parameter):
    while True:
        valid_input = False
        user_input = input(prompt + " (" + ", ".join(option for option, _ in option_action_pairs) + "): ")

        # If user inputs "back", return to previous menu
        if user_input.lower().strip() == "back":
            valid_input = True
            break

        for option, action in option_action_pairs:
            if user_input.lower().strip() == option.lower().strip():
                valid_input = True
                action(parameter)
                break
        if not valid_input:
            print("Invalid input. Please check input and available options and try again.")


# MENUS

# Main Menu
def main_menu(department, national_statistics_table, national_statistics):
    while True:
        print("\nMain Menu - Please enter a command based on the following choices, or enter 'close' "
              "to close the program.")
        user_input = input("(Department Configuration, Call Volume Visuals, Apparatus Recommendations, Reset "
                           "Department): ")

        # If user inputs "close", close the program
        if user_input.lower().strip() == "close":
            database_close()
            print("\nThe program will now close. Have a wonderful day!")
            close_program = True
            return close_program

        elif user_input.lower().strip() == "department configuration":
            department_config_menu(department)
        elif user_input.lower().strip() == "call volume visuals":
            call_volume_visuals_menu(national_statistics_table, department, national_statistics)
        elif user_input.lower().strip() == "apparatus recommendations":
            apparatus_recommendations_menu(national_statistics_table, department)
        elif "reset" in user_input.lower().strip():
            # Confirm with user
            confirm = input("\nAre you sure you would like to reset department? This will not delete database data,"
                            " but unsaved department data will be lost! (Yes/No): ")
            if confirm.lower().strip() == "yes":
                print("Resetting department...")
                return False  # Break out of main menu loop, which resets program at init_department()
        else:
            print("Invalid input. Please check input and available options and try again.")


# Department Configuration
def department_config_menu(department):
    menu_prompt("\nDepartment Configuration - Please enter a command based on the following choices, or enter 'Back' "
                "to return to previous menu:",
                [["Call Volume History", call_volume_history_submenu], ["Units Per Call", units_per_call_submenu],
                 ["Department Settings", department_settings_submenu]],
                department)


# Call Volume Visuals
def call_volume_visuals_menu(national_statistics_table, department, national_statistics):
    if department.history is None:
        print("\nNo department call volume history found. Please go the Department Configuration to configure call "
              "volume history.")
    else:
        while True:
            user_input = input("\nCall Volume Visuals - Please enter a command based on the following choices, or enter "
                               "'Back' to return to previous menu: (Department Graphs, National Statistics Graphs): ")
            if user_input.lower().strip() == "back":
                break
            elif "department" in user_input.lower().strip():
                department_call_volume_visuals(national_statistics_table, department)
            elif "national" in user_input.lower().strip():
                national_statistics_call_volume_visuals(national_statistics_table, national_statistics)
            else:
                print("Invalid input. Please check input and available options and try again.")


# Apparatus Recommendations
def apparatus_recommendations_menu(national_statistics_table, department):
    if department.history is None:
        print("\nNo department call volume history found. Please go the Department Configuration to configure call "
              "volume history.")
    else:
        print("\nApparatus Recommendations:\nApparatus recommendations will be tailored to department needs based on "
              "established department minimum requirements, department square mileage, environmental conditions, and "
              "department call volume.\nPlease see 'Department Configuration' menu to adjust these details.\nCall volume "
              "predictions will be made based on previous department call volume history if available, or national "
              "statistics data if department data is insufficient.\nComments will be displayed with factors affecting "
              "prediction accuracy as well as recommendations to improve it.")
        while True:
            user_input = input("\nPlease enter the year for apparatus recommendations, or 'back' to  return to previous "
                               "menu: ")
            try:
                lower_strip_input = user_input.lower().strip()
                if lower_strip_input == "back":
                    return
                else:
                    raise AttributeError
            except AttributeError:
                valid_int = utility.check_valid_int(user_input)
                if valid_int:
                    user_input = int(user_input)
                    prediction_year = copy.copy(user_input)
                    number_of_preceding_years = \
                        utility.get_valid_int_input("Please enter the number of preceding years to be used in predictions "
                                                    "(It is recommended to use as many years as call volume history is "
                                                    "reliably available). At least 5 years must be used: ")
                    if number_of_preceding_years < 5:
                        print("Invalid input. Number of preceding years must be at least 5.")

                    else:
                        print("\nCalculating recommendations...\n")
                        # Update department.temp_history to current department.history values
                        department.temp_history = copy.copy(department.history)

                        # Make call volume predictions as needed
                        end_year = copy.copy(prediction_year)
                        prediction_year -= number_of_preceding_years
                        prediction_number_of_preceding_years = 5
                        start_predictions = False  # Boolean to keep from making predictions on years prior to present department data
                        matches_found = False  # Boolean to track if there were any matches in department.temp_history
                        prediction_made = False
                        first_logic_description = None
                        first_prior_year_logic = None

                        while prediction_year <= end_year:
                            if matches_found is False:
                                for year in department.temp_history:
                                    if prediction_year == year[0]:
                                        start_predictions = True
                                        matches_found = True
                                        break

                            # If there are no matches in department.temp_history, initiate predictions manually
                            if matches_found is False and start_predictions is False and prediction_made is False:
                                call_volume_data, logic_description, prior_year_logic = \
                                    predict_all_actual_call_volume(national_statistics_table, department,
                                                                   prediction_year,
                                                                   prediction_number_of_preceding_years)
                                department.temp_history.append(call_volume_data)
                                # Save the first logic description
                                first_logic_description = copy.copy(logic_description)
                                first_prior_year_logic = copy.copy(prior_year_logic)
                                prediction_made = True

                            # If data not available for year but previous data is, make predictions
                            if start_predictions is True:
                                call_volume_data, logic_description, prior_year_logic = \
                                    predict_all_actual_call_volume(national_statistics_table, department,
                                                                   prediction_year,
                                                                   prediction_number_of_preceding_years)
                                department.temp_history.append(call_volume_data)
                                if prediction_made is False:
                                    # Save the first logic description
                                    first_logic_description = copy.copy(logic_description)
                                    first_prior_year_logic = copy.copy(prior_year_logic)
                                    prediction_made = True

                            prediction_year += 1

                        # Calculate recommendations
                        recommendations, logic_description, prior_year_logic = department.get_final_recommendations(national_statistics_table, prediction_year,
                                                                               number_of_preceding_years)
                        # Print prediction logic
                        if first_logic_description is not None and first_prior_year_logic is not None:
                            print("\nLogic for predictions: ")
                            print(first_logic_description)
                            print(first_prior_year_logic)
                        # Print recommendations
                        print("\nRecommended apparatus:\nEngines: " + str(recommendations[0][0]) + ". Reason: '" + str(
                            recommendations[0][1]) +
                              "' | Ladders: " + str(recommendations[1][0]) + ". Reason: '" + str(recommendations[1][1]) +
                              "' | Air Units: " + str(recommendations[2][0]) + ". Reason: '" + str(recommendations[2][1]) +
                              "' | Heavy Rescues: " + str(recommendations[3][0]) + ". Reason: '" + str(recommendations[3][1]) +
                              "' | \nHazmat Units: " + str(recommendations[4][0]) + ". Reason: '" + str(recommendations[4][1]) +
                              "' | Tankers: " + str(recommendations[5][0]) + ". Reason: '" + str(recommendations[5][1]) +
                              "' | Brush Units: " + str(recommendations[6][0]) + ". Reason: '" + str(recommendations[6][1]) +
                              "' | Water Rescue: " + str(recommendations[7][0]) + ". Reason: '" + str(
                            recommendations[7][1]) + "'")

                        # Reset temp history values after recommendations have been made
                        department.temp_history = copy.copy(department.history)
                        return


# SUBMENUS

# Department Configuration:

# Call Volume History submenu in CLI
def call_volume_history_submenu(department):
    menu_prompt("\nCall Volume History - Please enter a command based on the following choices, or enter 'Back' to "
                "return to previous menu:",
                [["Display", print_all_yearly_call_volume], ["Add", add_yearly_call_volume],
                 ["Remove", remove_yearly_call_volume], ["Import CSV", import_csv_to_sqlite],
                 ["Save", save_call_volume_history]],
                department)


# Units Per Call submenu in CLI
def units_per_call_submenu(department):
    menu_prompt("\nUnits Per Call - Please enter a command based on the following choices, or enter 'Back' to "
                "return to previous menu:",
                [["Display", print_all_units_per_call], ["Edit", edit_units_per_call], ["Save", save_units_per_call]],
                department)


# Department Settings submenu in CLI
def department_settings_submenu(department):
    menu_prompt("\nDepartment Settings - Please enter a command based on the following choices, or enter 'Back' to "
                "return to previous menu:",
                [["Display", print_department_settings], ["Edit", edit_department_settings],
                 ["Save", save_department_settings]],
                department)


# Call Volume Visuals:

# Department Call Volume Visuals
def department_call_volume_visuals(national_statistics_table, department):
    while True:
        user_input = input("\nDepartment Call Volume Visuals - Please enter a command based on the following choices, or enter "
                    "'Back' to return to previous menu: (With Predictions, Without Predictions): ")
        if user_input.lower().strip() == "back":
            break
        elif user_input.lower().strip() == "with predictions":
            plot_call_volume_predictions(national_statistics_table, department)
        elif user_input.lower().strip() == "without predictions":
            plot_call_volume_data(department)
        else:
            print("Invalid input. Please check input and available options and try again.")


# National Statistics Call Volume Visuals
def national_statistics_call_volume_visuals(national_statistics_table, national_statistics):
    while True:
        user_input = input("\nNational Statistics Call Volume Visuals - Please enter a command based on the following choices, or "
                "enter 'Back' to return to previous menu: (With Predictions, Without Predictions): ")
        if user_input.lower().strip() == "back":
            break
        elif user_input.lower().strip() == "with predictions":
            plot_call_volume_predictions(national_statistics_table, national_statistics)
        elif user_input.lower().strip() == "without predictions":
            plot_call_volume_data(national_statistics)
        else:
            print("Invalid input. Please check input and available options and try again.")


# SUBMENU FUNCTIONS

# Call Volume History:

# CLI command to print all yearly call volume for department (Call Volume History > Display)
def print_all_yearly_call_volume(department):
    if department.history:  # If history exists, print it
        print("\nDisplaying call volume history for " + department.name + ":")
        print("(Year, Total Call Volume, Fires, Medical Aid, False Alarms, Mutual Aid, "
              "Hazardous Materials, Other Hazardous Conditions, Other)")
        for row in department.history:
            print(row)
    else:  # If no history exists, notify user and return to Call Volume History menu
        print("No existing department history found.")


# CLI command to add yearly call volume for department (Call Volume History > Add)
def add_yearly_call_volume(department):
    exit_submenu = False
    while exit_submenu is False:
        print("\nPlease note that it is recommended to edit and import department call volume "
              "history via CSV file. Please see instructions for details.")
        valid_input = False
        while valid_input is False:
            year_history_input = input("\nPlease enter yearly call volume data in the format: year,"
                                       " fires, medical aid, false alarms, mutual aid, hazardous "
                                       "materials, other hazardous conditions, other. DO NOT "
                                       "include total call volume. Input 'back' to return to "
                                       "previous menu.\nEnter list here: ")

            # If "back" input, return to previous menu
            if year_history_input.lower().strip() == "back":
                exit_submenu = True
                break

            # Check if the input is a valid list
            try:
                year_history_list = [value.strip() for value in year_history_input.split(',')]

                # Check if the list contains all integers
                all_ints = False
                try:
                    all_ints = all(utility.check_valid_int(value) for value in
                                       year_history_list)  # Returns true if all positive integers
                except ValueError:
                    print("Invalid input. Values must all be positive integers.")

                if all_ints is True:
                    # Check if list is the right number of values
                    if len(year_history_list) == 8:
                        valid_input = True
                        year_found = False
                        if department.history is None:
                            # Calculate total call volume
                            # Convert values to ints before performing operations
                            for i in range(len(year_history_list)):
                                year_history_list[i] = int(year_history_list[i])

                            # Calculate total call volume for year by summing the values at indices 1 to 7
                            #   (skipping the year at index 0)
                            total_call_volume = sum(year_history_list[1:])

                            # Insert the calculated total value at index 1 in the list
                            year_history_list.insert(1, total_call_volume)

                            # Confirm with user
                            confirm = input("Yearly data to be added as follows: Year - " +
                                            str(year_history_list[0]) + " | Total Call Volume - " +
                                            str(year_history_list[1]) + " | Fires - " +
                                            str(year_history_list[2]) + " | Medical Aid - " +
                                            str(year_history_list[3]) + " | False Alarms - " +
                                            str(year_history_list[4]) + " | Mutual Aid - " +
                                            str(year_history_list[5]) + " | Hazardous Materials - " +
                                            str(year_history_list[6]) + " | Other Hazardous Conditions "
                                                                        "- " +
                                            str(year_history_list[7]) + " | Other - " +
                                            str(year_history_list[8]) +
                                            "\nAdd to department history? (Yes/No) ")
                            if confirm.lower().strip() == "yes":
                                department.history = []
                                department.history.append(tuple(year_history_list))
                                print(
                                    department.name + " values for year " + str(year_history_list[0]) +
                                    " successfully entered.")
                                exit_submenu = True
                            else:
                                print("Yearly call volume entry cancelled.")

                        else:
                            for index, row in enumerate(department.history):
                                if year_history_list[0] == row[0]:  # If year entered matches a year in department history
                                    year_found = True
                                    # Notify the user of the existing entry
                                    confirm = input(
                                        "Existing values found for entered year. Overwrite? (Yes/No): ")
                                    # Update department history values for the entered year
                                    if confirm.lower().strip() == "yes":
                                        # Calculate total call volume
                                        # Convert values to ints before performing operations
                                        for i in range(len(year_history_list)):
                                            year_history_list[i] = int(year_history_list[i])

                                        # Calculate total call volume for year by summing the values at indices 1 to 7
                                        #   (skipping the year at index 0)
                                        total_call_volume = sum(year_history_list[1:])

                                        # Insert the calculated total value at index 1 in the list
                                        year_history_list.insert(1, total_call_volume)

                                        # Convert list to tuple and set as appropriate department history
                                        department.history[index] = tuple(
                                            year_history_list)
                                        print(department.name + " values for year " + str(
                                            year_history_list[0]) + " successfully updated.")
                                        exit_submenu = True
                                    else:
                                        print("Yearly call volume update cancelled.")
                                    break
                            if year_found is False:
                                # Calculate total call volume
                                # Convert values to ints before performing operations
                                for i in range(len(year_history_list)):
                                    year_history_list[i] = int(year_history_list[i])

                                # Calculate total call volume for year by summing the values at indices 1 to 7
                                #   (skipping the year at index 0)
                                total_call_volume = sum(year_history_list[1:])

                                # Insert the calculated total value at index 1 in the list
                                year_history_list.insert(1, total_call_volume)

                                # Confirm with user
                                confirm = input("Yearly data to be added as follows: Year - " +
                                                str(year_history_list[0]) + " | Total Call Volume - " +
                                                str(year_history_list[1]) + " | Fires - " +
                                                str(year_history_list[2]) + " | Medical Aid - " +
                                                str(year_history_list[3]) + " | False Alarms - " +
                                                str(year_history_list[4]) + " | Mutual Aid - " +
                                                str(year_history_list[5]) + " | Hazardous Materials - " +
                                                str(year_history_list[6]) + " | Other Hazardous Conditions "
                                                                            "- " +
                                                str(year_history_list[7]) + " | Other - " +
                                                str(year_history_list[8]) +
                                                "\nAdd to department history? (Yes/No) ")
                                if confirm.lower().strip() == "yes":
                                    # Add entered values to department.history
                                    department.history.append(tuple(year_history_list))
                                    print(
                                        department.name + " values for year " + str(year_history_list[0]) +
                                        " successfully entered.")
                                    exit_submenu = True
                                else:
                                    print("Yearly call volume entry cancelled.")
                    else:
                        print("Invalid input. List is not the appropriate amount of values.")

            except ValueError:
                print("Invalid input. Please enter the data as a valid comma-separated list of "
                      "integers.")


# CLI command to remove call volume for input year for department (Call Volume History > Remove)
def remove_yearly_call_volume(department):
    if department.history is None:
        print("No department call volume history found. Please go the Department Configuration to configure call "
              "volume history.")
    else:
        exit_submenu = False
        print("\nPlease note that it is recommended to edit and import department call volume "
              "history via CSV file. Please see User Guide for details.")
        print("Note that it is not recommended to leave gaps in department call volume history, as it will lead to "
              "inconsistent data. Please make sure to double-check all department call volume data after editing.")
        while exit_submenu is False:
            valid_input = False
            while valid_input is False:
                year_input = input("\nPlease enter the year of department history you would like to remove, or "
                                   "enter 'back' to return to previous menu: ")

                # If "back" input, return to previous menu
                if year_input.lower().strip() == "back":
                    exit_submenu = True
                    break

                # Check if the input is an integer
                is_int = False
                try:
                    is_int = utility.check_valid_int(year_input)  # Try converting value to int

                except ValueError:
                    print("Invalid input. Year must be an integer.")

                if is_int:
                    year_input = int(year_input)
                    valid_input = True
                    year_found = False
                    for row in department.history:
                        if year_input == row[0]:  # If year entered matches a year in department history
                            year_found = True
                            # Notify the user of the existing entry and confirm removal
                            confirm = input(
                                "\nExisting values found for entered year:"
                                " Year - " + str(row[0]) +
                                " | Total Call Volume - " + str(row[1]) +
                                " | Fires - " + str(row[2]) +
                                " | Medical Aid - " + str(row[3]) +
                                " | False Alarms - " + str(row[4]) +
                                " | Mutual Aid - " + str(row[5]) +
                                " | Hazardous Materials - " + str(row[6]) +
                                " | Other Hazardous Conditions - " + str(row[7]) +
                                " | Other - " + str(row[8]) +
                                "\nRemove? (Yes/No): ")
                            # Remove department history values for the entered year
                            if confirm.lower().strip() == "yes":
                                department.history.remove(row)
                                print("Year: " + str(year_input) + " call volume data successfully removed.")
                                exit_submenu = True
                            else:
                                print("Yearly call volume removal cancelled.")
                            break
                    if year_found is False:
                        print("\nCall volume data for entered year not found.")


# Copy CSV file content to department.history and update database
def import_csv_to_sqlite(department):
    # Prompt user
    confirm = input("\nCopy '" + department.history_csv + "' contents to department call volume history and update "
                                                          "database? Note: This will replace any previous values. "
                                                          "(Yes/No): ")
    if confirm.lower().strip() == "yes":
        # Transfer CSV values to database
        print("Attempting to access '" + department.history_csv + "' for call volume history...")
        # If CSV exists, copy CSV values to database
        success = database.csv_to_sqlite(department.history_csv, department.table_name, "database.db")
        if success:
            print("Database successfully updated.")
            try:
                # Update department.history with new database values
                department.history = database.get_all_data(department.table_name)
                print("Department history successfully updated.")
            except sqlite3.OperationalError:
                print("Department history update from database failed.")
        else:
            print("Database update failed.")
    else:
        print("CSV import cancelled.")


# CLI command to take active department class (temporary) call volume history and save to department call volume table
#   in database (Call Volume History > Save)
def save_call_volume_history(department):
    # Print all yearly call volume history to confirm values with user
    print_all_yearly_call_volume(department)
    # Confirm user wants to save
    confirm = input("\nSave current call volume history values to '" + department.history_csv + "' and update '" +
                    department.table_name + "' (" + department.name + ") in database? (Yes/No): ")
    # If user confirms, save department history
    if confirm.lower().strip() == "yes":
        department.save_department_history("database.db")
    else:
        print("Call volume history save operation cancelled.")


# Units Per Call:

# CLI command to print all units per call for department (temporary department values, not database ones)
#   (Units Per Call > Display)
def print_all_units_per_call(department):
    print("\nAll current units per call for department: " + department.name)
    call_types = ("Urban Fire", "Suburban Fire", "Rural Fire", "Medical Aid", "False Alarm", "Urban Mutual Aid",
                  "Suburban Mutual Aid", "Rural Mutual Aid", "Hazardous Materials", "Other Hazardous Conditions",
                  "Other")
    units_per_call = [department.units_per_urban_fire, department.units_per_suburban_fire,
                      department.units_per_rural_fire, department.units_per_medical_aid,
                      department.units_per_false_alarm, department.units_per_urban_mutual_aid,
                      department.units_per_suburban_mutual_aid, department.units_per_rural_mutual_aid,
                      department.units_per_hazardous_materials, department.units_per_other_hazardous_conditions,
                      department.units_per_other]
    i = 0
    while i < len(call_types):
        print(call_types[i] + ": Engines - " + str(units_per_call[i][0]) + " | Ladders - " + str(units_per_call[i][1]) +
              " | Air Units - " + str(units_per_call[i][2]) + " | Tankers - " + str(units_per_call[i][3]) +
              " | Brush Units - " + str(units_per_call[i][4]) + " | Hazmat Units - " + str(units_per_call[i][5]) +
              " | Heavy Rescues - " + str(units_per_call[i][6]) + " | Water Rescues - " + str(units_per_call[i][7]))
        i += 1


# CLI command to edit units per call for department (temporary department values, not database ones)
#   (Units Per Call > Edit)
def edit_units_per_call(department):
    while True:
        # Get call type from user input
        call_prompt = "\nPlease enter call type of the units per call to edit, or enter 'Back' to return " \
                      "to previous menu\n"
        call_options = "Urban Fire, Suburban Fire, Rural Fire, Medical Aid, False Alarm, Urban Mutual Aid, Suburban " \
                       "Mutual Aid, Rural Mutual Aid, Hazardous Materials, Other Hazardous Conditions, Other"
        call_selection = utility.get_input(call_prompt, call_options)

        # If selection is 'back', return to previous menu
        if call_selection.lower().strip() == "back":
            break

        # If selection is valid call type...
        elif call_selection.lower().strip() == "urban fire" or call_selection.lower().strip() == "suburban fire" or \
                call_selection.lower().strip() == "rural fire" or call_selection.lower().strip() == "medical aid" or \
                call_selection.lower().strip() == "false alarm" or call_selection.lower().strip() == "urban mutual aid" or \
                call_selection.lower().strip() == "suburban mutual aid" or \
                call_selection.lower().strip() == "rural mutual aid" or \
                call_selection.lower().strip() == "hazardous materials" or \
                call_selection.lower().strip() == "other hazardous conditions" or \
                call_selection.lower().strip() == "other":

            # Get unit to edit based on entered call type
            unit_prompt = "\n" + call_selection + ": Please enter unit type to edit, or enter 'Back' to return to " \
                                                  "previous menu"
            unit_options = "Engines, Ladders, Air Units, Tankers, Brush Units, Hazmat Units, Heavy Rescues, " \
                           "Water Rescues"

            while True:
                unit_selection = utility.get_input(unit_prompt, unit_options)

                # If selection is 'back', return to previous menu
                if call_selection.lower().strip() == "back":
                    break

                elif "engine" in unit_selection.lower().strip():
                    unit = "Engines"
                    unit_element = 0
                    break
                elif "ladder" in unit_selection.lower().strip():
                    unit = "Ladders"
                    unit_element = 1
                    break
                elif "air" in unit_selection.lower().strip():
                    unit = "Air Units"
                    unit_element = 2
                    break
                elif "tanker" in unit_selection.lower().strip():
                    unit = "Tankers"
                    unit_element = 3
                    break
                elif "brush" in unit_selection.lower().strip():
                    unit = "Brush Units"
                    unit_element = 4
                    break
                elif "hazmat" in unit_selection.lower().strip():
                    unit = "Hazmat Units"
                    unit_element = 5
                    break
                elif "heavy" in unit_selection.lower().strip():
                    unit = "Heavy Rescues"
                    unit_element = 6
                    break
                elif "water" in unit_selection.lower().strip():
                    unit = "Water Rescues"
                    unit_element = 7
                    break
                else:
                    print("Invalid unit input. Please check options and try again.")

            # If valid unit is selected...
            if unit_element:
                # Get appropriate variable for selected call type
                call_name = utility.convert_to_sql_name(call_selection)
                units_per_call_list = list(getattr(department, "units_per_" + call_name, None))
                # Get appropriate value from units_per_call based on selected unit
                units_per_call = units_per_call_list[unit_element]

                # Display current value of unit per call type
                print("\nCurrent average number of " + unit + " per " + call_selection + ": " +
                      str(units_per_call))

                # Request new value from user
                new_value_str = input("Enter new average number of " + unit + " per " + call_selection + ": ")
                try:
                    # Check the type of the current value
                    current_type = type(units_per_call)

                    # Convert the new value based on the current type
                    if current_type is int:
                        new_value = int(new_value_str)
                    elif current_type is float:
                        new_value = float(new_value_str)
                    else:
                        raise ValueError("Invalid type for current value.")

                    if new_value < 0:
                        print("Invalid input. Value must be positive.")
                    else:
                        # Set new value for appropriate variable
                        units_per_call_list[unit_element] = new_value

                        # Convert units_per_call_list back to a tuple before setting it back to the appropriate variable
                        units_per_call_tuple = tuple(units_per_call_list)
                        setattr(department, "units_per_" + call_name, units_per_call_tuple)
                        print("Average number of " + unit + " per " + call_selection + " updated successfully.")
                        break
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")

        else:
            print("Invalid call type input. Please check options and try again.")


# CLI command to save units per call for department (temporary) to database (Units Per Call > Save)
def save_units_per_call(department):
    # Print values to confirm with user
    print_all_units_per_call(department)
    # Confirm user wants to save
    confirm = input("\nUpdate current units per call values to database? (Yes/No): ")
    # If user confirms, save units per call to database
    if confirm.lower().strip() == "yes":
        department.save_all_units_per_call()
    else:
        print("Units per call save operation cancelled cancelled.")


# Department Settings:

# CLI command to print all department settings (Department Settings > Display)
def print_department_settings(department):
    print("\nCurrent Department Settings for department: " + department.name)
    settings = [
        "department_name: " + str(department.name),
        "urban_square_miles: " + str(department.urban_square_miles),
        "suburban_square_miles: " + str(department.suburban_square_miles),
        "rural_square_miles: " + str(department.rural_square_miles),
        "aquatic_square_miles: " + str(department.aquatic_square_miles),
        "min_engines: " + str(department.min_engines),
        "min_ladders: " + str(department.min_ladders),
        "min_air_units: " + str(department.min_air_units),
        "min_heavy_rescue_units: " + str(department.min_heavy_rescue_units),
        "min_hazmat_units: " + str(department.min_hazmat_units),
        "min_tankers: " + str(department.min_tankers),
        "min_brush_units: " + str(department.min_brush_units),
        "min_water_rescue_units: " + str(department.min_water_rescue_units),
        "square_miles_per_engine: " + str(department.square_miles_per_engine),
        "square_miles_per_ladder: " + str(department.square_miles_per_ladder),
        "square_miles_per_air_unit: " + str(department.square_miles_per_air_unit),
        "square_miles_per_tanker: " + str(department.square_miles_per_tanker),
        "rural_square_miles_per_tanker: " + str(department.rural_square_miles_per_tanker),
        "square_miles_per_brush: " + str(department.square_miles_per_brush),
        "rural_square_miles_per_brush: " + str(department.rural_square_miles_per_brush),
        "square_miles_per_hazmat: " + str(department.square_miles_per_hazmat),
        "square_miles_per_heavy_rescue: " + str(department.square_miles_per_heavy_rescue),
        "aquatic_square_miles_per_water_rescue: " + str(department.aquatic_square_miles_per_water_rescue),
        "calls_per_engine: " + str(department.calls_per_engine),
        "calls_per_ladder: " + str(department.calls_per_ladder),
        "calls_per_air_unit: " + str(department.calls_per_air_unit),
        "calls_per_tanker: " + str(department.calls_per_tanker),
        "calls_per_brush: " + str(department.calls_per_brush),
        "calls_per_hazmat: " + str(department.calls_per_hazmat),
        "calls_per_heavy_rescue: " + str(department.calls_per_heavy_rescue),
        "calls_per_water_rescue: " + str(department.calls_per_water_rescue)
    ]
    for setting in settings:
        print(setting)


# CLI command to edit department settings (Department Settings > Edit)
def edit_department_settings(department):
    while True:
        print("\nPlease enter the name of the setting you would like to change. It is recommended to copy and "
              "paste variable names to avoid errors. Enter 'back' to return to previous menu.")
        print("(Login options:) name, password")
        print("(Environment options:) urban_square_miles, suburban_square_miles, rural_square_miles, "
              "aquatic_square_miles")
        print("(Minimum apparatus requirements:) min_engines, min_ladders, min_air_units, min_heavy_rescue_units, "
              "min_hazmat_units, min_tankers, min_brush_units, min_water_rescue_units")
        print("(Square miles per unit:) square_miles_per_engine, square_miles_per_ladder, square_miles_per_air_unit,"
              "square_miles_per_tanker, rural_square_miles_per_tanker, square_miles_per_brush, "
              "rural_square_miles_per_brush, square_miles_per_hazmat, square_miles_per_heavy_rescue, "
              "aquatic_square_miles_per_water_rescue")
        print("(Annual call capabilities per apparatus:) calls_per_engine, calls_per_ladder, calls_per_air_unit,"
              "calls_per_tanker, calls_per_brush, calls_per_hazmat, calls_per_heavy_rescue, calls_per_water_rescue")
        user_input = input("Please enter your choice here: ")
        if user_input.lower().strip() == "back":
            break
        # Check if the entered variable name exists and is allowed to be edited
        elif hasattr(department, user_input) and not user_input.startswith("__"):
            if user_input.lower().strip() == "name":
                new_value = input("Please enter new department name (Note that this updates department name and does "
                                  "not create a new department): ")
                # Check to make sure the potential new table name does not already exist in database
                try:
                    # Convert potential department name to sql table name
                    table_name = utility.convert_to_sql_name(new_value)
                    # Try to get data from potential table name
                    existing_data_values = database.get_all_data(table_name)
                    no_existing_data = True
                    if existing_data_values:
                        print("Error: Existing table found for entered name. Please try a different name.")
                        no_existing_data = False
                except sqlite3:
                    no_existing_data = True
                if no_existing_data is True:
                    # Confirm with user, then update appropriate values
                    confirm = input("\nUpdate department name to '" + str(new_value) + "'? (Yes/No): ")
                    if confirm.lower().strip() == "yes":
                        department.name = new_value
                        department.table_name = utility.convert_to_sql_name(department.name)
                        department.history_csv = department.table_name + "history.csv"
                        print(
                            "department.table_name and department.history_csv updated accordingly. Please note that this "
                            "will not delete previous tables and CSV files associated with previous department name.")
                        again = input("\nWould you like to update more department settings? (Yes/No): ")
                        if again.lower().strip() == "no":
                            break
                    else:
                        print("Department name update cancelled.")
            elif user_input.lower().strip() == "password":
                login = input("\nPlease enter current department password for " + department.name + ": ")
                if login == department.password:
                    new_value = input("Please enter new password: ")
                    confirm = input("Change " + department.name + " password to ' " + new_value + " ' ? (Yes/No): ")
                    if confirm.lower().strip() == "yes":
                        department.password = new_value
                        print(department.name + " password successfully updated. Please note that Department Settings "
                                                "must be saved for this to be permanent.")
                    else:
                        print("Password update cancelled.")
                else:
                    print("Incorrect department password.")
            else:  # If changing value besides department name...
                variable_value = getattr(department, user_input)

                # Display value to be changed and get new int value from user
                print("\nCurrent value of " + user_input + ": " + str(variable_value))
                new_value = utility.get_valid_int_input("Please enter the new value for " + user_input + ": ")

                # Confirm with user, then update value
                confirm = input("\nUpdate " + user_input + " value to " + str(new_value) + "? (Yes/No): ")
                if confirm.lower().strip() == "yes":
                    setattr(department, user_input, new_value)
                    print(user_input + " successfully updated.")
                    again = input("\nWould you like to update more department settings? (Yes/No): ")
                    if again.lower().strip() == "no":
                        break

                else:
                    print(user_input + " value update canceled.")
        else:
            print("Invalid input. Please check input and available options and try again.")


# CLI command to save department settings to database (Department Settings > Save)
def save_department_settings(department):
    # Print all department settings to confirm values with user
    print_department_settings(department)
    # Confirm user wants to save
    confirm = input("\nSave current department settings to database? (Yes/No): ")
    # If user confirms, save department settings to database
    if confirm.lower().strip() == "yes":
        department.save_department_settings()
    else:
        print("Department settings save operation cancelled.")
