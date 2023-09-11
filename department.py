import copy
import csv
import math
import sqlite3

import database
import machine_learning
from utility import invert_ratio, convert_to_sql_name, get_valid_int_input, get_recommendation_and_source


class Department:
    def __init__(self, name, prompts):
        self.name = name
        self.table_name = convert_to_sql_name(name)
        self.history_csv = self.table_name + "_history.csv"
        self.login_success = False  # Boolean to indicate if login was successful

        # Config department password "department_password": self.password
        try:
            self.password = database.get_department_password(self.name)
        except sqlite3.OperationalError:
            print("No login information detected for department.")
        if self.password:  # If previous password configured, ask for password
                if prompts is True:
                    login = input("\nPlease enter department password: ")
                    if login == self.password:
                        print("\nLogin successful.\n")
                        self.login_success = True
                    else:
                        print("Login failed: Incorrect password.")
                else:
                    self.login_success = True
        else:  # If no previous password, prompt user to create one
            confirm = input("\nNo existing department data found. Create new department? (Yes/No): ")
            if confirm.lower().strip() == "yes":
                self.password = input("Please enter a password to use for department (It is recommended to write this down "
                                      "or save it somewhere safe): ")
                self.login_success = True
        # If successful login, populate department values
        if self.login_success is True:
            # Config list to store department call volume history. If table exists in database, use that information
            try:
                self.history = database.get_all_data(self.table_name)
                if prompts is True:
                    print("Existing department call volume history found. Using previous department history.")
            except sqlite3.OperationalError:
                if prompts is True:
                    print("No department call volume history found.")
                self.history = None

            # Config list to store temporary department history for use in predictions (stores predicted yearly call
            #   volume values for use in compound predictions)
            self.temp_history = copy.copy(self.history)

            # Attempt to get existing department settings from database
            department_settings = database.get_department_settings(self.name)

            # Config distance variables. Aquatic square miles are not included in land_square_miles
            if department_settings is not None:
                if prompts is True:
                    print("Existing department settings found. Using previous settings.")
                self.urban_square_miles = department_settings[2]
                self.suburban_square_miles = department_settings[3]
                self.rural_square_miles = department_settings[4]
                self.aquatic_square_miles = department_settings[5]
            else:  # If no existing values, ask user
                if prompts is True:
                    print("No existing department settings found. Using default settings.")
                self.urban_square_miles = get_valid_int_input("Please enter " + self.name + " urban square miles: ")
                self.suburban_square_miles = get_valid_int_input("Please enter " + self.name + " suburban square miles: ")
                self.rural_square_miles = get_valid_int_input("Please enter " + self.name + " rural square miles: ")
                self.aquatic_square_miles = get_valid_int_input("Please enter " + self.name + " aquatic square miles: ")
            self.land_square_miles = self.urban_square_miles + self.suburban_square_miles + self.rural_square_miles  # Total non-aquatic SM

            # Config distance ratios
            self.urban_miles_ratio = 0
            if self.land_square_miles != 0:
                self.urban_miles_ratio = self.urban_square_miles / self.land_square_miles

            self.suburban_miles_ratio = 0
            if self.land_square_miles != 0:
                self.suburban_miles_ratio = self.suburban_square_miles / self.land_square_miles

            self.rural_miles_ratio = 0
            if self.land_square_miles != 0:
                self.rural_miles_ratio = self.rural_square_miles / self.land_square_miles

            # Environmental condition flags
            self.urban = False
            if self.urban_square_miles > 0:
                self.urban = True

            self.suburban = False
            if self.suburban_square_miles > 0:
                self.suburban = True

            self.rural = False
            if self.rural_square_miles > 0:
                self.rural = True

            self.aquatic = False
            if self.aquatic_square_miles > 0:
                self.aquatic = True

            # Minimum apparatus requirements
            if department_settings is not None:  # If existing settings found, use those
                self.min_engines = department_settings[6]
                self.min_ladders = department_settings[7]
                self.min_air_units = department_settings[8]
                self.min_heavy_rescue_units = department_settings[9]
                self.min_hazmat_units = department_settings[10]
                self.min_tankers = department_settings[11]
                self.min_brush_units = department_settings[12]
                self.min_water_rescue_units = department_settings[13]
            else:  # If no existing values, use defaults
                self.min_engines = 1
                self.min_ladders = 1
                self.min_air_units = 1
                self.min_heavy_rescue_units = 1
                self.min_hazmat_units = 1
                self.min_tankers = 0
                self.min_brush_units = 0
                if self.rural:  # Rural departments need a tanker and brush unit
                    self.min_tankers = 1
                    self.min_brush_units = 1
                self.min_water_rescue_units = 0
                if self.aquatic:  # Aquatic departments need a water rescue unit
                    self.min_water_rescue_units = 1

            # Square miles per apparatus (How much area each apparatus can reliably respond to)
            if department_settings is not None:  # If existing settings found, use those
                self.square_miles_per_engine = department_settings[14]
                self.square_miles_per_ladder = department_settings[15]
                self.square_miles_per_air_unit = department_settings[16]
                self.square_miles_per_tanker = department_settings[17]
                self.rural_square_miles_per_tanker = department_settings[18]
                self.square_miles_per_brush = department_settings[19]
                self.rural_square_miles_per_brush = department_settings[20]
                self.square_miles_per_hazmat = department_settings[21]
                self.square_miles_per_heavy_rescue = department_settings[22]
                self.aquatic_square_miles_per_water_rescue = department_settings[23]
            else:  # If no existing values, use defaults
                self.square_miles_per_engine = 15
                self.square_miles_per_ladder = 20  # Always needed, but more are necessary for high-rises and urban environments
                self.square_miles_per_air_unit = 50
                self.square_miles_per_tanker = 0
                self.rural_square_miles_per_tanker = 50  # Tankers only needed in rural areas
                self.square_miles_per_brush = 0  # Brush trucks are used for wildland fires
                self.rural_square_miles_per_brush = 20  # Brush trucks only needed in rural areas
                self.square_miles_per_hazmat = 100
                self.square_miles_per_heavy_rescue = 30
                self.aquatic_square_miles_per_water_rescue = 20

            # Default yearly call volume maximums per apparatus
            if department_settings is not None:  # If existing settings found, use those
                self.calls_per_engine = department_settings[24]
                self.calls_per_ladder = department_settings[25]
                self.calls_per_air_unit = department_settings[26]
                self.calls_per_tanker = department_settings[27]
                self.calls_per_brush = department_settings[28]
                self.calls_per_hazmat = department_settings[29]
                self.calls_per_heavy_rescue = department_settings[30]
                self.calls_per_water_rescue = department_settings[31]
            else:  # If no existing values, use defaults. Encourage user to verify for their department
                self.calls_per_engine = 365 * 20  # Each engine can handle up to 20 calls per day
                self.calls_per_ladder = 365 * 15  # Each ladder can handle up to 15 calls every day
                self.calls_per_air_unit = 365 * 10  # Each air unit can handle up to 10 calls every day
                self.calls_per_tanker = 365 * 10  # Each tanker can handle up to 10 calls every day
                self.calls_per_brush = 365 * 15  # Each brush unit can handle up to 15 calls every day
                self.calls_per_hazmat = 365 * 5  # Each hazmat unit can handle up to 5 calls every day
                self.calls_per_heavy_rescue = 365 * 15  # Each heavy rescue unit can handle up to 15 calls every day
                self.calls_per_water_rescue = 365 * 20  # Each water rescue unit can handle up to 20 calls every day

            # Attempt to get existing department units per call for all call type values from database
            all_units_per_call = database.get_all_units_per_call(self.name)

            # Units per call values (format: [engine, ladder, air, tanker, brush, hazmat, heavy rescue,
            #   water rescue]. Note that the format is different from other methods.)
            if all_units_per_call:  # If existing units per call values found, use those
                if prompts is True:
                    print("Existing department units per call found. Using previous values.")
                for row in all_units_per_call:
                    if str(row[0]) == "urban_fire":
                        self.units_per_urban_fire = row[1:]  # Use all values except for first row (call_type)
                    if str(row[0]) == "suburban_fire":
                        self.units_per_suburban_fire = row[1:]
                    if str(row[0]) == "rural_fire":
                        self.units_per_rural_fire = row[1:]
                    if str(row[0]) == "medical_aid":
                        self.units_per_medical_aid = row[1:]
                    if str(row[0]) == "false_alarm":
                        self.units_per_false_alarm = row[1:]
                    if str(row[0]) == "urban_mutual_aid":
                        self.units_per_urban_mutual_aid = row[1:]
                    if str(row[0]) == "suburban_mutual_aid":
                        self.units_per_suburban_mutual_aid = row[1:]
                    if str(row[0]) == "rural_mutual_aid":
                        self.units_per_rural_mutual_aid = row[1:]
                    if str(row[0]) == "hazardous_materials":
                        self.units_per_hazardous_materials = row[1:]
                    if str(row[0]) == "other_hazardous_conditions":
                        self.units_per_other_hazardous_conditions = row[1:]
                    if str(row[0]) == "other":
                        self.units_per_other = row[1:]

            else:  # If no existing values, use defaults
                if prompts is True:
                    print("No existing department units per call found. Using default values.")
                # Fires
                self.units_per_urban_fire = [2, 2, 1, 0, 0, 0, 1, 0]
                self.units_per_suburban_fire = [3, 1, 1, 0, 0, 0, 1, 0]
                self.units_per_rural_fire = [2, 1, 1, 1, 1, 0, 1, 0]

                # Medical aid
                self.units_per_medical_aid = [1, 0, 0, 0, 0, 0, 0, 0]

                # False alarms
                self.units_per_false_alarm = [1, 1, 0, 0, 0, 0, 0, 0]

                # Mutual aid: Note that this will vary widely depending on department and what mutual aid it provides
                self.units_per_urban_mutual_aid = [1, 0.5, 0.1, 0, 0, 0, 0.5, 0]
                self.units_per_suburban_mutual_aid = [1, 0.5, 0.1, 0, 0, 0, 0.5, 0]
                self.units_per_rural_mutual_aid = [1, 0.5, 0.1, 0.1, 0.1, 0.1, 0.5, 0]

                # Hazardous materials
                self.units_per_hazardous_materials = [0.5, 0, 0.2, 0, 0, 1, 0.2, 0]

                # Other hazardous conditions
                self.units_per_other_hazardous_conditions = [1, 0, 0, 0, 0.05, 0, 0.05, 0]
                if self.aquatic:
                    self.units_per_other_hazardous_conditions = [1, 0, 0, 0, 0.05, 0, 0.05, 0.05]

                # Other
                self.units_per_other = [1, 0, 0, 0, 0, 0, 0, 0]

            # Set appropriate environmental weights
            self.weighted_units_per_fire = [urban * self.urban_miles_ratio + suburban * self.suburban_miles_ratio +
                                            rural * self.rural_miles_ratio for urban, suburban, rural in
                                            zip(self.units_per_urban_fire, self.units_per_suburban_fire,
                                                self.units_per_rural_fire)]
            self.weighted_units_per_mutual_aid = [urban * self.urban_miles_ratio + suburban * self.suburban_miles_ratio +
                                                  rural * self.rural_miles_ratio for urban, suburban, rural in
                                                  zip(self.units_per_urban_mutual_aid, self.units_per_suburban_mutual_aid,
                                                      self.units_per_rural_mutual_aid)]

    # Add one year of history to department
    def add_year_history(self, year, fires, medical_aid, false_alarms, mutual_aid, hazardous_materials,
                         other_hazardous_conditions, other):
        row = [year, fires, medical_aid, false_alarms, mutual_aid, hazardous_materials,
               other_hazardous_conditions, other]
        self.history.append(row)

    # Manually add multiple years of history to department (Must already be properly formatted to work correctly)
    def add_formatted_bulk_history(self, *args):
        for data in args:
            self.history.append(data)

    # Update department CSV and database table with self.history (Deletes previous information)
    def save_department_history(self, database_file):
        # Add .csv extension if missing
        if not self.history_csv.endswith('.csv'):
            self.history_csv += '.csv'

        try:
            # Create CSV file to store the data
            with open(self.history_csv, "w", newline="", encoding="utf-8") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(["Year", "Total", "Fires", "MedicalAid", "FalseAlarms",
                                     "MutualAid", "HazardousMaterials", "OtherHazardousConditions", "Other"])
                csv_writer.writerows(self.history)

            print("Successfully updated department history values in '" + self.history_csv + "'.")

            # Use the csv_to_sqlite function to import data from CSV to the database
            try:
                database.csv_to_sqlite(self.history_csv, self.table_name, database_file)
            except sqlite3 as sql_error:
                print("Error in updating database: " + sql_error + "\nPlease check all values in " + self.name +
                      " call volume history and/or department CSV file ('" + self.history_csv +
                      "') and revise accordingly.")
        except PermissionError:
            print("Error: CSV file is currently open. Please close the CSV file and try again.")

    # Update department_settings row for department in database
    def save_department_settings(self):
        # Create a dictionary with column names as keys and their corresponding values
        updates = {
            "department_name": self.name,
            "department_password": self.password,
            "urban_square_miles": self.urban_square_miles,
            "suburban_square_miles": self.suburban_square_miles,
            "rural_square_miles": self.rural_square_miles,
            "aquatic_square_miles": self.aquatic_square_miles,
            "min_engines": self.min_engines,
            "min_ladders": self.min_ladders,
            "min_air_units": self.min_air_units,
            "min_heavy_rescue_units": self.min_heavy_rescue_units,
            "min_hazmat_units": self.min_hazmat_units,
            "min_tankers": self.min_tankers,
            "min_brush_units": self.min_brush_units,
            "min_water_rescue_units": self.min_water_rescue_units,
            "square_miles_per_engine": self.square_miles_per_engine,
            "square_miles_per_ladder": self.square_miles_per_ladder,
            "square_miles_per_air_unit": self.square_miles_per_air_unit,
            "square_miles_per_tanker": self.square_miles_per_tanker,
            "rural_square_miles_per_tanker": self.rural_square_miles_per_tanker,
            "square_miles_per_brush": self.square_miles_per_brush,
            "rural_square_miles_per_brush": self.rural_square_miles_per_brush,
            "square_miles_per_hazmat": self.square_miles_per_hazmat,
            "square_miles_per_heavy_rescue": self.square_miles_per_heavy_rescue,
            "aquatic_square_miles_per_water_rescue": self.aquatic_square_miles_per_water_rescue,
            "calls_per_engine": self.calls_per_engine,
            "calls_per_ladder": self.calls_per_ladder,
            "calls_per_air_unit": self.calls_per_air_unit,
            "calls_per_tanker": self.calls_per_tanker,
            "calls_per_brush": self.calls_per_brush,
            "calls_per_hazmat": self.calls_per_hazmat,
            "calls_per_heavy_rescue": self.calls_per_heavy_rescue,
            "calls_per_water_rescue": self.calls_per_water_rescue,
        }

        database.update_records("department_settings", updates, "department_name", "database.db")

    # Saves Department units for all call types to sql database
    def save_all_units_per_call(self):
        database.save_units_per_call(self.name, "urban_fire", self.units_per_urban_fire[0],
                                     self.units_per_urban_fire[1], self.units_per_urban_fire[2],
                                     self.units_per_urban_fire[3], self.units_per_urban_fire[4],
                                     self.units_per_urban_fire[5], self.units_per_urban_fire[6],
                                     self.units_per_urban_fire[7])
        database.save_units_per_call(self.name, "suburban_fire", self.units_per_suburban_fire[0],
                                     self.units_per_suburban_fire[1], self.units_per_suburban_fire[2],
                                     self.units_per_suburban_fire[3], self.units_per_suburban_fire[4],
                                     self.units_per_suburban_fire[5], self.units_per_suburban_fire[6],
                                     self.units_per_suburban_fire[7])
        database.save_units_per_call(self.name, "rural_fire", self.units_per_rural_fire[0],
                                     self.units_per_rural_fire[1], self.units_per_rural_fire[2],
                                     self.units_per_rural_fire[3], self.units_per_rural_fire[4],
                                     self.units_per_rural_fire[5], self.units_per_rural_fire[6],
                                     self.units_per_rural_fire[7])
        database.save_units_per_call(self.name, "medical_aid", self.units_per_medical_aid[0],
                                     self.units_per_medical_aid[1], self.units_per_medical_aid[2],
                                     self.units_per_medical_aid[3], self.units_per_medical_aid[4],
                                     self.units_per_medical_aid[5], self.units_per_medical_aid[6],
                                     self.units_per_medical_aid[7])
        database.save_units_per_call(self.name, "false_alarm", self.units_per_false_alarm[0],
                                     self.units_per_false_alarm[1], self.units_per_false_alarm[2],
                                     self.units_per_false_alarm[3], self.units_per_false_alarm[4],
                                     self.units_per_false_alarm[5], self.units_per_false_alarm[6],
                                     self.units_per_false_alarm[7])
        database.save_units_per_call(self.name, "urban_mutual_aid", self.units_per_urban_mutual_aid[0],
                                     self.units_per_urban_mutual_aid[1], self.units_per_urban_mutual_aid[2],
                                     self.units_per_urban_mutual_aid[3], self.units_per_urban_mutual_aid[4],
                                     self.units_per_urban_mutual_aid[5], self.units_per_urban_mutual_aid[6],
                                     self.units_per_urban_mutual_aid[7])
        database.save_units_per_call(self.name, "suburban_mutual_aid", self.units_per_suburban_mutual_aid[0],
                                     self.units_per_suburban_mutual_aid[1], self.units_per_suburban_mutual_aid[2],
                                     self.units_per_suburban_mutual_aid[3], self.units_per_suburban_mutual_aid[4],
                                     self.units_per_suburban_mutual_aid[5], self.units_per_suburban_mutual_aid[6],
                                     self.units_per_suburban_mutual_aid[7])
        database.save_units_per_call(self.name, "rural_mutual_aid", self.units_per_rural_mutual_aid[0],
                                     self.units_per_rural_mutual_aid[1], self.units_per_rural_mutual_aid[2],
                                     self.units_per_rural_mutual_aid[3], self.units_per_rural_mutual_aid[4],
                                     self.units_per_rural_mutual_aid[5], self.units_per_rural_mutual_aid[6],
                                     self.units_per_rural_mutual_aid[7])
        database.save_units_per_call(self.name, "hazardous_materials", self.units_per_hazardous_materials[0],
                                     self.units_per_hazardous_materials[1], self.units_per_hazardous_materials[2],
                                     self.units_per_hazardous_materials[3], self.units_per_hazardous_materials[4],
                                     self.units_per_hazardous_materials[5], self.units_per_hazardous_materials[6],
                                     self.units_per_hazardous_materials[7])
        database.save_units_per_call(self.name, "other_hazardous_conditions",
                                     self.units_per_other_hazardous_conditions[0],
                                     self.units_per_other_hazardous_conditions[1],
                                     self.units_per_other_hazardous_conditions[2],
                                     self.units_per_other_hazardous_conditions[3],
                                     self.units_per_other_hazardous_conditions[4],
                                     self.units_per_other_hazardous_conditions[5],
                                     self.units_per_other_hazardous_conditions[6],
                                     self.units_per_other_hazardous_conditions[7])
        database.save_units_per_call(self.name, "other", self.units_per_other[0], self.units_per_other[1],
                                     self.units_per_other[2], self.units_per_other[3], self.units_per_other[4],
                                     self.units_per_other[5], self.units_per_other[6], self.units_per_other[7])
        print("Successfully updated units per call for " + self.name + ".")

    # Calculate apparatus recommendations based on square mileage and square-miles-to-apparatus ratio
    def get_square_mileage_requirements(self):
        # Set per-square-mile ratios based on environment
        if self.urban:
            # Increase ladders per urban square mile
            per_urban_mile_ratio = 1.5  # Add 50% more ladder trucks per square mile in urban environment
            ladders_per_square_mile = invert_ratio(self.square_miles_per_ladder)  # Convert to apparatus per square mile
            ladders_per_urban_square_mile = ladders_per_square_mile * per_urban_mile_ratio
            urban_square_miles_per_ladder = invert_ratio(ladders_per_urban_square_mile)  # Convert back
            # Calculate new square miles per ladder
            self.square_miles_per_ladder = (urban_square_miles_per_ladder * self.urban_miles_ratio) + \
                                           (self.square_miles_per_ladder * self.suburban_miles_ratio) + \
                                           (self.square_miles_per_ladder * self.rural_miles_ratio)

        # Assign potentially unused environment-based recommendations
        sqm_tanker_recommendation = 0
        sqm_brush_recommendation = 0
        sqm_water_rescue_recommendation = 0

        # Set minimum requirements based on ratios and square mileage
        sqm_engine_recommendation = math.floor(self.land_square_miles / self.square_miles_per_engine)
        sqm_ladder_recommendation = math.floor(self.land_square_miles / self.square_miles_per_ladder)
        sqm_air_unit_recommendation = math.floor(self.land_square_miles / self.square_miles_per_air_unit)
        sqm_heavy_rescue_recommendation = math.floor(self.land_square_miles / self.square_miles_per_heavy_rescue)
        sqm_hazmat_unit_recommendation = math.floor(self.land_square_miles / self.square_miles_per_hazmat)
        if self.rural:
            sqm_tanker_recommendation = math.floor(self.rural_square_miles / self.rural_square_miles_per_tanker)
            sqm_brush_recommendation = math.floor(self.rural_square_miles / self.rural_square_miles_per_brush)
        if self.aquatic:
            sqm_water_rescue_recommendation = math.floor(self.aquatic_square_miles /
                                                         self.aquatic_square_miles_per_water_rescue)

        return sqm_engine_recommendation, sqm_ladder_recommendation, sqm_air_unit_recommendation, \
            sqm_heavy_rescue_recommendation, sqm_hazmat_unit_recommendation, sqm_tanker_recommendation, \
            sqm_brush_recommendation, sqm_water_rescue_recommendation

    def get_call_volume_requirements(self, national_statistics_table, prediction_year, number_of_preceding_years):
        predicted_call_volume, logic_description, prior_year_logic = \
            machine_learning.predict_all_actual_call_volume(national_statistics_table, self, prediction_year,
                                                            number_of_preceding_years)

        engines_needed = math.ceil(self.get_apparatus_number_needed_by_call_volume("engine", predicted_call_volume))
        ladders_needed = math.ceil(self.get_apparatus_number_needed_by_call_volume("ladder", predicted_call_volume))
        air_units_needed = math.ceil(self.get_apparatus_number_needed_by_call_volume("air_unit", predicted_call_volume))
        heavy_rescues_needed = math.ceil(
            self.get_apparatus_number_needed_by_call_volume("heavy_rescue", predicted_call_volume))
        hazmat_units_needed = math.ceil(
            self.get_apparatus_number_needed_by_call_volume("hazmat", predicted_call_volume))
        tankers_needed = math.ceil(self.get_apparatus_number_needed_by_call_volume("tanker", predicted_call_volume))
        brush_units_needed = math.ceil(self.get_apparatus_number_needed_by_call_volume("brush", predicted_call_volume))
        water_rescues_needed = math.ceil(
            self.get_apparatus_number_needed_by_call_volume("water_rescue", predicted_call_volume))

        return [engines_needed, ladders_needed, air_units_needed, heavy_rescues_needed, hazmat_units_needed,
            tankers_needed, brush_units_needed, water_rescues_needed], logic_description, prior_year_logic

    # Get the number of a type of apparatus needed based on call volume
    def get_apparatus_number_needed_by_call_volume(self, apparatus, call_volume_list):
        # Create list of calls per apparatus
        calls_per_apparatus = [self.calls_per_engine, self.calls_per_ladder, self.calls_per_air_unit,
                               self.calls_per_tanker, self.calls_per_brush, self.calls_per_hazmat,
                               self.calls_per_heavy_rescue, self.calls_per_water_rescue]

        # Determine appropriate element for apparatus information
        if apparatus == "engine":
            element = 0
        elif apparatus == "ladder":
            element = 1
        elif apparatus == "air_unit":
            element = 2
        elif apparatus == "tanker":
            element = 3
        elif apparatus == "brush":
            element = 4
        elif apparatus == "hazmat":
            element = 5
        elif apparatus == "heavy_rescue":
            element = 6
        elif apparatus == "water_rescue":
            element = 7
        else:
            print("Error: Invalid apparatus type.")
            return None

        # Fires
        fire_calls = self.weighted_units_per_fire[element] * call_volume_list[2]
        apparatus_needed_for_fires = fire_calls / calls_per_apparatus[element]
        # Medical aid
        medical_aid_calls = self.units_per_medical_aid[element] * call_volume_list[3]
        apparatus_needed_for_medical_aid = medical_aid_calls / calls_per_apparatus[element]
        # False alarms
        false_alarm_calls = self.units_per_false_alarm[element] * call_volume_list[4]
        apparatus_needed_for_false_alarms = false_alarm_calls / calls_per_apparatus[element]
        # Mutual aid
        mutual_aid_calls = self.weighted_units_per_mutual_aid[element] * call_volume_list[5]
        apparatus_needed_for_mutual_aid = mutual_aid_calls / calls_per_apparatus[element]
        # Hazardous materials
        hazmat_calls = self.units_per_hazardous_materials[element] * call_volume_list[6]
        apparatus_needed_for_hazmat = hazmat_calls / calls_per_apparatus[element]
        # Other hazardous conditions
        other_hazardous_conditions_calls = self.units_per_other_hazardous_conditions[element] * call_volume_list[
            7]
        apparatus_needed_for_other_hazardous_conditions = other_hazardous_conditions_calls / calls_per_apparatus[
            element]
        # Other
        other_calls = self.units_per_other[element] * call_volume_list[8]
        apparatus_needed_for_other = other_calls / calls_per_apparatus[element]
        # Total
        apparatus_needed_for_all_calls = apparatus_needed_for_fires + apparatus_needed_for_medical_aid + \
                                         apparatus_needed_for_false_alarms + apparatus_needed_for_mutual_aid + \
                                         apparatus_needed_for_hazmat + \
                                         apparatus_needed_for_other_hazardous_conditions + \
                                         apparatus_needed_for_other
        return apparatus_needed_for_all_calls

    # Get all recommendations by type and compare to determine final apparatus recommendations
    def get_final_recommendations(self, national_statistics_table, prediction_year, number_of_preceding_years):
        # Square-mileage-based recommendations
        sqm_engine_recommendation, sqm_ladder_recommendation, sqm_air_unit_recommendation, \
            sqm_heavy_rescue_recommendation, sqm_hazmat_unit_recommendation, sqm_tanker_recommendation, \
            sqm_brush_recommendation, sqm_water_rescue_recommendation = self.get_square_mileage_requirements()
        # Call-volume-based recommendations
        [vol_engine_recommendation, vol_ladder_recommendation, vol_air_unit_recommendation,
            vol_heavy_rescue_recommendation, vol_hazmat_recommendation, vol_tanker_recommendation,
            vol_brush_recommendation, vol_water_rescue_recommendation], logic_description, prior_year_logic = \
            self.get_call_volume_requirements(national_statistics_table, prediction_year, number_of_preceding_years)

        # Choose the highest recommendation based on minimum requirements, square mileage, or call volume
        engine_recommendation = get_recommendation_and_source(self.min_engines, sqm_engine_recommendation,
                                                              vol_engine_recommendation)
        ladder_recommendation = get_recommendation_and_source(self.min_ladders, sqm_ladder_recommendation,
                                                              vol_ladder_recommendation)
        air_unit_recommendation = get_recommendation_and_source(self.min_air_units, sqm_air_unit_recommendation,
                                                                vol_air_unit_recommendation)
        heavy_rescue_recommendation = get_recommendation_and_source(self.min_air_units, sqm_heavy_rescue_recommendation,
                                                                    vol_heavy_rescue_recommendation)
        hazmat_unit_recommendation = get_recommendation_and_source(self.min_air_units, sqm_hazmat_unit_recommendation,
                                                                   vol_hazmat_recommendation)
        tanker_recommendation = get_recommendation_and_source(self.min_tankers, sqm_tanker_recommendation,
                                                              vol_tanker_recommendation)
        brush_recommendation = get_recommendation_and_source(self.min_brush_units, sqm_brush_recommendation,
                                                             vol_brush_recommendation)
        water_rescue_recommendation = get_recommendation_and_source(self.min_water_rescue_units,
                                                                    sqm_water_rescue_recommendation,
                                                                    vol_water_rescue_recommendation)

        return [engine_recommendation, ladder_recommendation, air_unit_recommendation, heavy_rescue_recommendation,
            hazmat_unit_recommendation, tanker_recommendation, brush_recommendation, water_rescue_recommendation], \
            logic_description, prior_year_logic
