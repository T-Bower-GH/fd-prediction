import csv
import sqlite3

from utility import check_valid_int

# Connect to database
conn = sqlite3.connect('database.db')

# Create cursor to execute SQL commands
cursor = conn.cursor()


# Close connection to database
def database_close():
    conn.close()
    print("\nDatabase connection closed.")


# Queries all data from a table in database
def get_all_data(table):
    # Create query
    cursor.execute("SELECT * FROM " + str(table))
    data = cursor.fetchall()
    return list(data)


# Get fire call volume for each year
def get_yearly_data(table, call_type):
    result = []
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

    for entry in table:
        # print(entry)
        result.append((entry[0], entry[column]))
    return result


# Print contents of a non-database table, adding column names
def print_call_volume_data(table_name, table):
    print("All call volume values for", table_name + ":")
    column_names = ["Year", "Total", "Fires", "Medical Aid", "False Alarms", "Mutual Aid",
                    "Haz. Mat.", "Other Haz. Cond.", "Other"]
    column_width = 17  # Adjust the width as needed

    # Print column names
    header = "|".join(name.ljust(column_width) for name in column_names)
    print(header)

    # Print data rows
    for row in table:
        row_values = [str(value).ljust(column_width) for value in row]
        row_string = "|".join(row_values)
        print(row_string)


# Get department settings from database
def get_department_settings(department_name):
    # Define the SQL query to select the row based on the primary key value
    sql_query = f"SELECT * FROM department_settings WHERE department_name = ?"

    # Execute the query with the primary key value as a parameter
    cursor.execute(sql_query, (department_name,))

    # Fetch the result (should be a single row)
    row = cursor.fetchone()

    return row


def get_department_password(department_name):
    # Define the SQL query to select the row based on the primary key value
    sql_query = f"SELECT department_password FROM department_settings WHERE department_name = ?"

    # Execute the query with the primary key value as a parameter
    cursor.execute(sql_query, (department_name,))

    # Fetch the result (should be a single row)
    row = cursor.fetchone()

    # Unpack the single-element tuple to get the string value
    password = row[0] if row else None

    return password


# Imports a csv file and saves to database as a new table
def csv_to_sqlite(csv_file, table_name, database_file):
    try:
        # Create the table using column names from the CSV file
        with open(csv_file, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            column_names = next(csv_reader)
            columns = ", ".join(
                f"{col} INTEGER NOT NULL" for col in column_names)  # Set all columns to INTEGER NOT NULL

            # Create table if it does not exist with Year as the Primary Key
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns}, PRIMARY KEY(Year))"
            cursor.execute(create_table_query)

            # Delete existing rows in the table
            delete_query = f"DELETE FROM {table_name}"
            cursor.execute(delete_query)

            # Insert data from the CSV file into the table
            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(column_names))})"
            for row in csv_reader:
                # Check if all values (except for column names) are positive integers
                if all(check_valid_int(value) for value in row[1:]):
                    cursor.execute(insert_query, row)
                else:
                    print("Error: Invalid data in the CSV file. All values (except for column names) must be positive "
                          "integers.")
                    return False

            conn.commit()
            print("Successfully updated '" + table_name + "' table in '" + database_file + "'.")
            return True
    except PermissionError:
        print("Error: CSV file is currently open. Please close the CSV file and try again.")
    except FileNotFoundError:
        print("Error: CSV file '" + csv_file + "' not found.")
        return False
    except Exception as e:
        print("An error occurred: " + str(e))
        return False


# Updates multiple values in a database table
def update_records(table_name, updates, primary_key_column, database_file):
    # Build the REPLACE INTO query to insert or update the record
    columns = ", ".join(updates.keys())
    placeholders = ":" + ", :".join(updates.keys())
    replace_query = f"REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Execute the REPLACE INTO query with parameters
    cursor.execute(replace_query, updates)

    conn.commit()

    print("Successfully added or updated row in '" + table_name + "' table in '" + database_file + "'.")


# Get units per call for all call types by department
def get_all_units_per_call(department_name):
    # Define SQL queries for checking and retrieving data
    select_query = "SELECT * FROM units_per_call WHERE department_name = ?"

    # Execute the query with the parameters
    cursor.execute(select_query, (department_name,))

    # Fetch the row
    rows = cursor.fetchall()

    # Return all values except the first column (department_name)
    return [row[1:] for row in rows]


# Saves number of units required for each call to appropriate table in database
def save_units_per_call(department_name, call_type, engines_needed, ladders_needed, air_units_needed,
                        tankers_needed, brush_units_needed, hazmat_units_needed, heavy_rescues_needed,
                        water_rescues_needed):
    # Define SQL queries for checking and updating/inserting data
    check_query = "SELECT COUNT(*) FROM units_per_call WHERE department_name = ? AND call_type = ?"
    update_query = f"UPDATE units_per_call SET engines_needed = ?, ladders_needed = ?, air_units_needed = ?, " \
                   f"tankers_needed = ?, brush_units_needed = ?, hazmat_units_needed = ?, " \
                   f"heavy_rescues_needed = ?, water_rescues_needed = ? " \
                   f"WHERE department_name = ? AND call_type = ?"
    insert_query = f"INSERT INTO units_per_call (department_name, call_type, engines_needed, ladders_needed, " \
                   f"air_units_needed, tankers_needed, brush_units_needed, hazmat_units_needed, " \
                   f"heavy_rescues_needed, water_rescues_needed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    # Check if a row with the given department_name and call_type exists
    cursor.execute(check_query, (department_name, call_type))
    row_count = cursor.fetchone()[0]

    if row_count > 0:
        # Update the existing row
        cursor.execute(update_query, (engines_needed, ladders_needed, air_units_needed,
                                      tankers_needed, brush_units_needed, hazmat_units_needed,
                                      heavy_rescues_needed, water_rescues_needed,
                                      department_name, call_type))
    else:
        # Insert a new row
        cursor.execute(insert_query, (department_name, call_type, engines_needed, ladders_needed,
                                      air_units_needed, tankers_needed, brush_units_needed,
                                      hazmat_units_needed, heavy_rescues_needed, water_rescues_needed))

    # Commit the changes
    conn.commit()
