import warnings

from sklearn.exceptions import UndefinedMetricWarning
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from database import get_yearly_data

# Ignore the specific warning related to the R^2 score (Custom logic messages are supplied instead)
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# Use linear regression machine learning model to predict call volume of a specific type for a specific year
def predict_calls_by_year(table, call_type, prediction_year):
    # Prepare data
    data = get_yearly_data(table, call_type)
    years = [entry[0] for entry in data]
    call_volume = [entry[1] for entry in data]

    # Split data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(years, call_volume, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit([[year] for year in x_train], y_train)

    # Make prediction
    predicted_call_volume = model.predict([[prediction_year]])

    # Evaluate the model to ensure accuracy of data
    y_prediction_test = model.predict([[year] for year in x_test])
    r2_score_result = r2_score(y_test, y_prediction_test)

    return predicted_call_volume[0], r2_score_result


# Predict call volume for all types for specified year
def predict_all_calls_by_year(table, prediction_year):
    # Make predictions
    fire_prediction, r2_score_result = predict_calls_by_year(table, "fires", prediction_year)
    medical_aid_prediction, r2_score_result = predict_calls_by_year(table, "medical_aid", prediction_year)
    false_alarms_prediction, r2_score_result = predict_calls_by_year(table, "false_alarms", prediction_year)
    mutual_aid_prediction, r2_score_result = predict_calls_by_year(table, "mutual_aid", prediction_year)
    hazardous_materials_prediction, r2_score_result = predict_calls_by_year(table, "hazardous_materials",
                                                                            prediction_year)
    other_hazardous_conditions_prediction, r2_score_result = predict_calls_by_year(table, "other_hazardous_conditions",
                                                                                   prediction_year)
    other_prediction, r2_score_result = predict_calls_by_year(table, "other", prediction_year)
    total_prediction = fire_prediction + medical_aid_prediction + false_alarms_prediction + mutual_aid_prediction + \
                       hazardous_materials_prediction + other_hazardous_conditions_prediction + other_prediction

    # Return predictions
    predictions = [prediction_year, total_prediction, fire_prediction, medical_aid_prediction, false_alarms_prediction,
                   mutual_aid_prediction, hazardous_materials_prediction, other_hazardous_conditions_prediction,
                   other_prediction]

    return predictions


# Take call volume values from preceding year data and convert to growth ratio
def calculate_call_growth_ratio(call_type, preceding_year_data):
    call_type_data = []
    if call_type == "total_call_volume":
        column = 1
    elif call_type == "fires":
        column = 2
    elif call_type == "medical_aid":
        column = 3
    elif call_type == "false_alarms":
        column = 4
    elif call_type == "mutual_aid":
        column = 5
    elif call_type == "hazardous_materials":
        column = 6
    elif call_type == "other_hazardous_conditions":
        column = 7
    elif call_type == "other":
        column = 8
    else:
        return "Error: Invalid call type."

    # Append only applicable call type data
    for entry in preceding_year_data:
        call_type_data.append(entry[column])

    # Calculate call growth ratios per year
    yearly_growth_ratios = []
    for i in range(1, len(call_type_data)):
        yearly_growth = call_type_data[i] - call_type_data[i - 1]
        growth_ratio = (yearly_growth / call_type_data[i - 1])
        yearly_growth_ratios.append(growth_ratio)

    # Calculate average call growth across all years in data set
    if len(yearly_growth_ratios) > 0:
        average_call_growth = sum(yearly_growth_ratios) / len(yearly_growth_ratios)
        return average_call_growth
    else:
        print("Error: Not enough data to calculate call growth")
        return 0  # No differences calculated, return 0 as the average


# Predict call growth ratio for a specific call type based on input number of preceding years
def predict_call_growth_ratio(table_name, table, call_type, prediction_year, number_of_preceding_years, announce):
    predicted_preceding_years = []
    preceding_year_data = []
    preceding_year = prediction_year - number_of_preceding_years
    years_available_count = 0  # Counts how many years were already in the database to pull from for prediction

    while preceding_year < prediction_year:
        data_available = False  # Boolean to track if data for preceding year is already in the database
        for entry in table:
            if preceding_year == entry[0]:
                preceding_year_data.append(list(entry))  # Appends as list for consistency of data (Originally tuple)
                data_available = True  # Data is available, so no prediction must be made
                years_available_count += 1  # Increment years available
                break
        if not data_available:  # If no data for preceding year is available, make a prediction
            prediction = predict_all_calls_by_year(table, preceding_year)
            preceding_year_data.append(prediction)
            predicted_preceding_years.append(preceding_year)  # Note the year that a prediction was made
        preceding_year += 1

    predictions_made = "No predictions necessary for target year."
    if announce is True:  # Boolean included to prevent announcing predictions multiple times
        if predicted_preceding_years:
            preceding_years_string = ', '.join(str(year) for year in predicted_preceding_years)
            predictions_made = table_name + " predictions have been made for the following years: " + preceding_years_string
    call_growth_ratio = calculate_call_growth_ratio(call_type, preceding_year_data)
    return call_growth_ratio, years_available_count, predictions_made


# Predict call growth ratios for all call types
def predict_all_call_growth_ratios(table_name, table, prediction_year, number_of_preceding_years):
    # Predict call growth ratios by type
    fires_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table, "fires", prediction_year,
                                                                       number_of_preceding_years, False)
    medical_aid_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table, "medical_aid",
                                                                             prediction_year,
                                                                             number_of_preceding_years, False)
    false_alarms_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table, "false_alarms",
                                                                              prediction_year,
                                                                              number_of_preceding_years, False)
    mutual_aid_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table, "mutual_aid",
                                                                            prediction_year,
                                                                            number_of_preceding_years, False)
    hazardous_materials_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table,
                                                                                     "hazardous_materials",
                                                                                     prediction_year,
                                                                                     number_of_preceding_years, False)
    other_hazardous_conditions_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table,
                                                                                            "other_hazardous_conditions",
                                                                                            prediction_year,
                                                                                            number_of_preceding_years,
                                                                                            False)
    other_ratio, years_available_count, predictions_made = predict_call_growth_ratio(table_name, table, "other", prediction_year,
                                                                       number_of_preceding_years, True)

    ratios = [fires_ratio, medical_aid_ratio, false_alarms_ratio, mutual_aid_ratio, hazardous_materials_ratio,
              other_hazardous_conditions_ratio, other_ratio]
    return ratios, years_available_count, predictions_made  # Ensures ratios is returned as an array


# Weigh national call growth ratio against department growth ratio based on how much department history is available
def weigh_call_growth_ratio(call_type, national_statistics_table, department, prediction_year,
                            number_of_preceding_years):
    department_name = department.name
    department_table = department.temp_history
    # Get call growth ratios from national statistics and local department
    national_statistics_growth_ratios, national_history, predictions_made = predict_all_call_growth_ratios(
        "National Statistics",
        national_statistics_table,
        prediction_year,
        number_of_preceding_years)
    department_growth_ratios, years_available_count, predictions_made = \
        predict_all_call_growth_ratios(department_name, department_table, prediction_year, number_of_preceding_years)

    # Find appropriate call growth ratio element
    if call_type == "fires":
        element = 0
    elif call_type == "medical_aid":
        element = 1
    elif call_type == "false_alarms":
        element = 2
    elif call_type == "mutual_aid":
        element = 3
    elif call_type == "hazardous_materials":
        element = 4
    elif call_type == "other_hazardous_conditions":
        element = 5
    elif call_type == "other":
        element = 6
    else:
        return "Error: Invalid call type."

    # Assign variables for ratios
    national_call_type_ratio = national_statistics_growth_ratios[element]
    department_call_type_ratio = department_growth_ratios[element]
    # Configure weights for ratios based on available department history and description of logic
    if years_available_count >= 5:  # 5+ year history
        national_ratio_weight = 0
        department_ratio_weight = 1
        logic_description = "5+ years of department history available for initial prediction. Only department " \
                            "values will be used, leading to the most accurate prediction."
    elif 5 > years_available_count >= 3:  # 3-4 year history
        national_ratio_weight = 0.3
        department_ratio_weight = 0.7
        logic_description = "3-4 years of department history available for initial prediction. Department data " \
                            "will mainly be used, leading to a more accurate prediction."
    elif 3 > years_available_count >= 2:  # 2 year history
        national_ratio_weight = 0.6
        department_ratio_weight = 0.4
        logic_description = "2 years of department history available for initial prediction. Predictions and/or " \
                            "National data will mainly be used, leading to a less accurate prediction."
    else:  # < 2 year history
        national_ratio_weight = 1
        department_ratio_weight = 0
        logic_description = "Insufficient department history available for initial prediction. Only national data " \
                            "will be used. Please note that solely national-statistics-based data is much less " \
                            "accurate than department values and should be used as a rule of thumb."

    # Flag discrepancy between national and department growth
    direction_discrepancy = False
    if national_ratio_weight != 0 and department_ratio_weight != 0:  # If not only one data source is being used
        if (national_call_type_ratio > 0 > department_call_type_ratio) or (
                national_call_type_ratio < 0 < department_call_type_ratio):  # If one growth is positive and one is negative
            direction_discrepancy = True

        if direction_discrepancy:
            print("Discrepancy in data noted for " +
                  str(prediction_year) + ": National and department growth ratios in opposite directions.")

    # Calculate weighted growth ratio
    weighted_growth_ratio = (national_call_type_ratio * national_ratio_weight) + (
            department_call_type_ratio * department_ratio_weight)
    return weighted_growth_ratio, logic_description, predictions_made


# Calculate weighted growth ratio and apply to prior year of prediction to predict actual expected call volume
def predict_actual_call_volume(call_type, national_statistics_table, department, prediction_year,
                               number_of_preceding_years):
    prior_year = prediction_year - 1
    weighted_ratio, logic_description, predictions_made = weigh_call_growth_ratio(call_type, national_statistics_table,
                                                                                  department, prediction_year,
                                                                                  number_of_preceding_years)

    # Find call type element
    if call_type == "total_call_volume":
        element = 1
    elif call_type == "fires":
        element = 2
    elif call_type == "medical_aid":
        element = 3
    elif call_type == "false_alarms":
        element = 4
    elif call_type == "mutual_aid":
        element = 5
    elif call_type == "hazardous_materials":
        element = 6
    elif call_type == "other_hazardous_conditions":
        element = 7
    elif call_type == "other":
        element = 8
    else:
        return "Error: Invalid call type."

    # See if prior year data is available. If not, make prediction.
    data_available = False  # Boolean to track if data for preceding year is already in the database
    for entry in department.temp_history:
        if prior_year == entry[0]:
            data_available = True  # Data is available, so no prediction must be made
            prior_year_call_volume = entry[element]  # Find appropriate call type volume
            break
    prior_year_logic = "Prior year data for prediction available, leading to more accurate data."
    if not data_available:  # If no data for preceding year is available, make a prediction
        prior_year_call_volume, r2_score_result = predict_calls_by_year(department.temp_history, call_type, prior_year)
        prior_year_logic = "Prior year data for year prediction not available. Compounded prediction made, which may " \
                           "affect data accuracy."

    # Make prediction and return value
    prediction = prior_year_call_volume + (prior_year_call_volume * weighted_ratio)
    return prediction, logic_description, prior_year_logic, predictions_made


def predict_all_actual_call_volume(national_statistics_table, department, prediction_year,
                                   number_of_preceding_years):
    fires_prediction, logic_description, prior_year_logic, predictions_made = \
        predict_actual_call_volume("fires", national_statistics_table, department,
                                   prediction_year, number_of_preceding_years)
    medical_aid_prediction, logic_description, prior_year_logic, predictions_made = predict_actual_call_volume(
        "medical_aid", national_statistics_table, department, prediction_year, number_of_preceding_years)
    false_alarms_prediction, logic_description, prior_year_logic, predictions_made = predict_actual_call_volume(
        "false_alarms", national_statistics_table, department, prediction_year, number_of_preceding_years)
    mutual_aid_prediction, logic_description, prior_year_logic, predictions_made = predict_actual_call_volume(
        "mutual_aid", national_statistics_table, department, prediction_year, number_of_preceding_years)
    hazardous_materials_prediction, logic_description, prior_year_logic, predictions_made = predict_actual_call_volume(
        "hazardous_materials", national_statistics_table,
        department, prediction_year,
        number_of_preceding_years)
    other_hazardous_conditions_prediction, logic_description, prior_year_logic, predictions_made = \
        predict_actual_call_volume(
            "other_hazardous_conditions",
            national_statistics_table, department, prediction_year,
            number_of_preceding_years)
    other_prediction, logic_description, prior_year_logic, predictions_made = \
        predict_actual_call_volume("other", national_statistics_table, department,
                                   prediction_year, number_of_preceding_years)
    total_call_volume_prediction = fires_prediction + medical_aid_prediction + false_alarms_prediction + \
                                   mutual_aid_prediction + hazardous_materials_prediction + \
                                   other_hazardous_conditions_prediction + other_prediction
    yearly_prediction_values = [prediction_year, total_call_volume_prediction, fires_prediction, medical_aid_prediction,
            false_alarms_prediction, mutual_aid_prediction, hazardous_materials_prediction,
            other_hazardous_conditions_prediction, other_prediction]
    department.temp_history.append(yearly_prediction_values)
    return yearly_prediction_values, logic_description, prior_year_logic
