import interface
from department import Department
from interface import init_department

# Initialize national statistics without prompts (For department comparisons)
national_statistics = Department("National Statistics", False)

# Main
print("Welcome to the fire department apparatus recommendation and call volume prediction program!")
close_program = False
while close_program is False:
    # Initialize department
    department = init_department()
    # If valid login credentials, open main menu. If not, restart loop
    if department.login_success is True:
        # If "close" is triggered in main menu, loop breaks and program closes. If "reset department" is triggered, loop
        #   repeats and initializes department again
        close_program = interface.main_menu(department, national_statistics.history, national_statistics)

