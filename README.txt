TABLE OF CONTENTS:
INTRODUCTION
STARTING THE PROGRAM
MENU OPTIONS & FEATURES
CREDITS

INTRODUCTION:
Welcome to the Fire Department Predictor Application! This program is designed to assist fire departments in managing
their resources, making call volume predictions, and providing apparatus recommendations based on historical data and
department-specific settings. Please be sure to consult this README to ensure proper operation.


STARTING THE PROGRAM:
(Using the Windows operating system is recommended.)
To start the program, use the included batch file: "RunFireDepartmentApp.bat". This will open a new terminal, and
you will be prompted to access a department.
A sample department is available to use with the program. Department name: “Dummy Department” (without quotes,
case sensitive), password: “BigDummy” (without quotes, case-sensitive). If you want to test program functionality
with pre-populated department history and settings, it is recommended to use this department.


MENU OPTIONS & FEATURES:
Accessing a Department:
1.	*National Statistics is an available department to edit its yearly call volume history values through the interface;
    however, is it not recommended to change other settings. The password for National Statistics is ‘ns’ without quotes.
2.	On program startup, you will be prompted to enter your department name.
    a.	If you are trying to initialize a new department:
        i.	Enter department name. If department name already exists and you do not know the password, make any input to
            return to department name input.
        ii.	If department name is not taken, you will be prompted to confirm and then enter a password for the new
            department
        iii.You will then be prompted to enter certain necessary information pertaining to the department. Upon
            initialization, several additional values will be set to defaults and can be changed in ‘Department
            Configuration’
    b.	If you are trying to access an existing department:
        i.	Please make sure to check your spelling and that your case matches that of the existing department you are
            trying to access
        ii.	If an existing department name is entered, you will be prompted for the department password
        iii.Upon successful login, logic regarding access to existing data will appear, and you will be brought to
            the main menu (See ‘Main Menu’ below)

Main Menu:
1.	After successful department login, you will be prompted with command options from the main menu. To access a command,
    simply type the name of the command into the input prompt (For quicker entry, you can copy + paste the command name
    from the prompt) and press enter. Available commands:
    a.	Department Configuration Menu
        i.	(See ‘Department Configuration’ below)
    b.	Call Volume Visuals
        i.	(See ‘Department Configuration’ below)
    c.	Apparatus Recommendations
        i.	(See ‘Department Configuration’ below)
    d.	Reset Department
        i.	Resets department and returns to department login prompt. Note that this does not delete values from the
        department being reset, but any unsaved changes will be lost!
    e.	Close
        i.	Close the connection to the database and close the program
2.	Note that certain options will not be available until department history values are entered. Therefore, it is
    recommended to begin with ‘Department Configuration’ and ensure accurate department yearly call volume history is
    present

Department Configuration Menu (Note that all values are temporary until saved to database using the appropriate command!):
1.	Call Volume History Submenu (Call volume history is used for making call volume predictions, displaying visuals, and
    making call-volume-based apparatus recommendations for a department. The higher a department’s call volume, the
    higher demand for apparatus resources)
    a.	Display: Prints all call volume history entries for department
        i.	Call volume values are based on year and number of calls by type and follow the format: Year, Total Call
            Volume, Fires, Medical Aid, False Alarms, Mutual Aid, Hazardous Materials, Other Hazardous Conditions, Other
    b.	Add: Provides information on how to properly format yearly call volume values and allows manual entry of new
        yearly values
        i.	Checks are in place to ensure only proper values are entered and in the correct format; however, all manual
            entries should be double-checked, as putting values in the wrong order will lead to inaccurate results
        ii.	If values for an existing year are entered, the existing entry will be updated after confirmation
        iii.Note that total call volume is calculated by the program and should not be manually entered
    c.	Remove: Removes a yearly entry from department history
        i.	Enter the year to be removed and follow the resulting prompts
    d.	Import CSV: Allows call volume history data to be directly imported via user-supplied CSV file
        i.	The interface will provide the appropriate CSV file name in the confirmation prompt. The CSV file name MUST
            match in order for the operation to perform correctly
        ii.	You have the option to supply your own CSV file or have the program create a pre-formatted CSV file with the
            appropriate name and settings
            1.	If you are supplying a CSV file, save it directly into the Capstone Project folder. You should see other
                CSV files already saved, such as ‘national_statistics_history.csv’. Ensure that the name of the file
                matches the prompt and has the .csv extension. If you are unsure of how to format the CSV values, use
                ‘national_statistics_history.csv’ as a reference
            2.	If you are creating a new CSV file through the interface, go back to the Call Volume History submenu and
                complete the Save operation (it is ok to Save even if there is no department history). This will
                automatically create the appropriately named CSV file for the department, add the appropriately
                formatted column names to the file, and add any existing department call volume history records in the
                proper format. You can now directly edit and save this file for future use with the Import CSV command
        iii.However you choose to prepare the CSV file, be sure to confirm the CSV file and department names are
            correct, then confirm in the interface prompt to update department history values from the CSV file
            1.	To avoid errors, be sure to have your CSV file closed (be sure to save it first!), properly formatted,
                and have the correct values (aside from column names, values must be positive integers)
            2.	You will be notified in the interface whether the operation succeeded or not (and why, in the case it
                was unsuccessful)
    e.	Save: Saves current department call volume history values to database and appropriate CSV file. If no CSV file
        exists, one will be created and populated with the proper formatting.
    f.	Back: Returns to the previous menu
2.	Units Per Call Submenu (Units per call are used in call-volume-based apparatus predictions. The higher units per
    call, the more apparatus are required to handle each call)
    a.	Display: Prints all units per call values for department by call type
    b.	Edit: Allows editing of specific unit per call by call type (For example, if engines per call for fires is set
        to 3, that means an average of 3 engines is required for every fire)
        i.	Enter the desired call type in interface prompt
        ii.	Enter the desired unit type to edit in interface prompt
        iii.	The current value will then be displayed. Enter the new desired value, and the value will be updated
        iv.	Values can be entered as integers or floats but must be positive
        v.	After editing values, it is recommended to Display all values to ensure correctness
    c.	Save: Save current department units per call values to database
    d.	Back: Returns to the previous menu
3.	Department Settings Submenu
    a.	Display: Prints all department settings for department
    b.	Edit: Allows editing of department settings to suit the department’s needs
        i.	Choose the setting you would like to change from the listed prompt (Note that certain values, namely ‘name’
        and ‘password’ have different restrictions; however, this will be indicated including extra instructions as
        needed in the interface)
        ii.	The current value will then be displayed. Enter the new desired value, and after confirmation, the value
        (and other related applicable values, in certain cases) will be updated
        iii.	Most values must be positive integers; however, if an improper value is entered, it will be indicated
        with instructions in the interface
    c.	Save: Save current department settings to database
    d.	Back: Returns to the previous menu
4.	Back: Returns to the main menu

Call Volume Visuals:
1.	Department Graphs: Displays visual graphs based on department values (National statistics data may still be factored
    in predictions if not enough department data is available)
    a.	With Predictions: Plots a visual graph based on department total call volume by year including predictions (the
        year predictions begin is indicated by a dotted red line)
    b.	Without Predictions: Plots a visual graph based on department total call volume by year without using any
        predictions
    c.	Back: Returns to the previous menu
2.	National Statistics Graphs: Displays visual graphs based on national statistics values
    a.	With Predictions: Plots a visual graph based on national total call volume by year including predictions (the
        year predictions begin is indicated by a dotted red line)
    b.	Without Predictions: Plots a visual graph based on national total call volume by year without using any
        predictions
    c.	Back: Returns to the previous menu
3.	Back: Returns to the main menu

Apparatus Recommendations: Calculates apparatus recommendations and displays with logic
1.	Before requesting recommendations, it is recommended to verify and edit applicable department history, settings, and
    variables as needed in ‘Department Configuration’ (accessed through the Main Menu)
2.	Enter the desired year for apparatus recommendations. This value must be a positive integer.
3.	Enter the number of preceding years you would like to use (This is mainly used for call volume predictions). It is
    recommended to use as much available history as possible to ensure the most accurate results. This value must be a
    positive integer.
4.	The program will perform predictions and calculations and then display apparatus recommendations, call volume
    prediction logic, and apparatus recommendation logic


CREDITS:
This program would not have been possible without the invaluable contributions of the following libraries and tools:
-SQLite3: The embedded database used for storing department-specific data and historical records.
-Matplotlib.pyplot: This library provided essential functionality for creating visual graphs and charts, enhancing the
 program's data visualization capabilities.
-Scikit-Learn (SKLearn): SKLearn played a pivotal role in implementing machine learning models for call volume
 predictions, ensuring the accuracy of our apparatus recommendations.

Thank you to the developers and maintainers of these open-source projects for their dedication and commitment to making
these tools available to the community.

Please consider checking out the documentation and contributing to these projects to support their ongoing development.
Matplotlib.pyplot Documentation: https://matplotlib.org/stable/users/index.html
Scikit-Learn (SKLearn) Documentation: https://scikit-learn.org/stable/index.html

Thank you to the communities behind these libraries for their hard work and for making the program more powerful and
efficient.