import copy

import matplotlib.pyplot as pyplot
from datetime import datetime

from machine_learning import predict_all_actual_call_volume


# Plot department call volumes for current year, past 10 years, and 5 years into the future
def plot_call_volume_predictions(national_statistics_table, department):
    # Update department.temp_history to current department.history values
    department.temp_history = copy.copy(department.history)

    print("\nGenerating predictions. Please wait...")
    # Get current year datetime and convert to int
    current_year = int(datetime.now().year)
    start_year = current_year - 10
    end_year = current_year + 5

    # Get data for applicable years or make predictions as needed
    plot_history = []  # List to store plot values
    prediction_year = start_year
    prediction_number_of_preceding_years = 5
    start_predictions = False  # Boolean to keep from making predictions on years prior to present department data
    prediction_made = False
    logic_description = None
    first_logic_description = None
    first_prior_year_logic = None
    while prediction_year <= end_year:
        year_total_call_volume = None
        for year in department.temp_history:
            if prediction_year == year[0]:
                year_total_call_volume = (year[0], year[1])
                start_predictions = True
                plot_history.append(year_total_call_volume)
                break
        # If data not available for year but previous data is, make predictions
        if year_total_call_volume is None:
            if start_predictions is True:
                call_volume_data, logic_description, prior_year_logic = \
                    predict_all_actual_call_volume(national_statistics_table, department,  prediction_year,
                                                   prediction_number_of_preceding_years)
                year_total_call_volume = (call_volume_data[0], call_volume_data[1])
                plot_history.append(year_total_call_volume)
                if prediction_made is False:
                    # Save the first logic description
                    first_logic_description = copy.copy(logic_description)
                    first_prior_year_logic = copy.copy(prior_year_logic)
                    prediction_made = True
                    prediction_start_year = call_volume_data[0]

        prediction_year += 1

    # Reset temp history values after predictions have been made
    department.temp_history = copy.copy(department.history)

    # Use extracted data to create plots
    years = []
    for value_pair in plot_history:
        years.append(value_pair[0])
    call_volumes = []
    for value_pair in plot_history:
        call_volumes.append(value_pair[1])

    # Plot the data
    pyplot.plot(years, call_volumes, marker='o')

    # Add vertical line for the start of predictions
    if start_predictions:
        pyplot.axvline(x=prediction_start_year, color='r', linestyle='--', label='Start of Predictions')

    pyplot.xlabel('Year')
    pyplot.ylabel('Total Call Volume')
    pyplot.title('Call Volumes by Year with Predictions: ' + department.name)
    pyplot.grid(True)
    pyplot.legend()

    # Print prediction logic
    if first_logic_description is not None and first_prior_year_logic is not None:
        print("\nLogic for predictions: ")
        print(first_logic_description)
        print(first_prior_year_logic)
    print("\nDisplaying call volume graph with predictions.")

    pyplot.show()


# Plot all call volume data for department without predictions (national_statistics_table not required but used for
#   menu_prompt() parameters)
def plot_call_volume_data(department):
    plot_history = []  # List to store plot values

    # Get data for total call volume by year
    for year in department.history:
        year_total_call_volume = (year[0], year[1])
        plot_history.append(year_total_call_volume)

    # Use extracted data to create plots
    years = []
    for value_pair in plot_history:
        years.append(value_pair[0])
    call_volumes = []
    for value_pair in plot_history:
        call_volumes.append(value_pair[1])

    # Plot the data with labels
    pyplot.plot(years, call_volumes, marker='o', label=department.name)

    pyplot.xlabel('Year')
    pyplot.ylabel('Total Call Volume')
    pyplot.title('Call Volumes by Year: ' + department.name)
    pyplot.grid(True)
    pyplot.legend()  # Show the legend
    print("\nDisplaying call volume graph without predictions.")
    pyplot.show()

