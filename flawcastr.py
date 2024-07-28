from datetime import datetime
from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
import config  # Importing the config module
import os
import csv
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
default_csv_path = os.path.join(BASE_DIR, 'default.csv')


def update_config_from_csv(csv_path, config_module, initial_load=False, skip_vars=[]):
    loaded_vars = []
    if os.path.exists(csv_path):
        with open(csv_path, mode='r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                var_name = row['Variable'].replace(' ', '_').lower()
                value = row['Value']
                # Skip variables set by user input
                if var_name in skip_vars:
                    continue

                # Continue with existing logic...
                if (initial_load and var_name in ['individual_or_couple', 'client1_name', 'client1_age', 'client2_name', 'client2_age', 'age_to_follow_to']) or not initial_load:
                    if hasattr(config_module, var_name):
                        # Determine the type of the current attribute in config
                        attr_type = type(getattr(config_module, var_name))
                        # Convert to the appropriate type before setting
                        try:
                            if attr_type is int:
                                # Handle int conversion, considering possible float representation in CSV
                                if '.' in value:
                                    float_value = float(value)
                                    if float_value.is_integer():
                                        setattr(config_module, var_name, int(float_value))
                                    else:
                                        print(f"Value {value} for variable '{var_name}' is not a clean integer.")
                                else:
                                    setattr(config_module, var_name, int(value))
                            elif attr_type is float:
                                setattr(config_module, var_name, float(value))
                            elif attr_type is date:
                                # Adjust here for date format in CSV
                                try:
                                    setattr(config_module, var_name, datetime.strptime(value, '%d/%m/%Y').date())
                                except ValueError as e:
                                    print(f"Date conversion error for variable '{var_name}': {e}. Check the date format in your CSV.")
                            else:
                                setattr(config_module, var_name, value)
                            loaded_vars.append(var_name)
                        except ValueError as e:
                            print(f"Value conversion error for variable '{var_name}': {e}")
    return loaded_vars


# Ensure this function is defined in your script
def load_initial_configuration():
    # Load only the relevant variables for the initial window
    loaded_vars = update_config_from_csv(default_csv_path, config, initial_load=True)
    # Additional logic could be added here to handle defaults if needed


# Check if default.csv exists and update config
update_config_from_csv(default_csv_path, config)

# def initialize_simulation():
#     valid_balance = False
#     iteration_count = 0  # Add a counter to track the number of iterations

#     while not valid_balance:
#         iteration_count += 1
#         logging.debug(f"Iteration: {iteration_count}")

#         deterministic_balances = calcs.calculate_deterministic_balances()

#         final_balance = deterministic_balances[-1]
#         min_balance = min(deterministic_balances)

#         # Check if the final balance is within the desired range and no balance is negative
#         if 0 <= final_balance <= 1000000 and all(balance >= 0 for balance in deterministic_balances):
#             valid_balance = True
#         else:
#             logging.debug("Valid balance not found, continuing loop.")

#         if iteration_count > 100:  # Add a failsafe to avoid infinite loops
#             logging.warning("Maximum iterations reached, breaking loop.")
#             break

#     return deterministic_balances

class ClientInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.resize(900, 850)  # Adjust width and height as needed


        self.setWindowTitle("Welcome to Flawcastr!")
        layout = QFormLayout()
        self.setLayout(layout)



        # Set font for the dialog
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)

        # Add logo image
        logo = QLabel()
        image_path = os.path.join(BASE_DIR, 'flawcastr_logo.jpeg')
        pixmap = QPixmap(image_path)
        logo.setPixmap(pixmap)
        layout.addRow(logo)


        welcome_label = QLabel("Welcome to Flawcastr! Before we begin, please enter some basic information about what you want to model.")
        welcome_label.setWordWrap(True)
        age_label = QLabel("")
        age_label.setWordWrap(True)
        

        # Add introductory text
        layout.addRow(welcome_label)

        # Dropdown for individual or couple
        self.individual_or_couple = QComboBox()
        self.individual_or_couple.addItems(["individual", "couple"])
        self.individual_or_couple.currentIndexChanged.connect(self.update_client2_visibility)
        layout.addRow("Individual or couple:", self.individual_or_couple)

        # Fields for client names and ages
        self.client1_name_label = QLabel("Name:")
        self.client1_name = QLineEdit(config.client1_name)
        self.client1_age_label = QLabel("Age:")
        self.client1_age = QLineEdit(str(config.client1_age))

        layout.addRow(self.client1_name_label, self.client1_name)
        layout.addRow(self.client1_age_label, self.client1_age)

        # Client 2 fields
        self.client2_name_label = QLabel("Name:")
        self.client2_name = QLineEdit(config.client2_name)
        self.client2_age_label = QLabel("Age:")
        self.client2_age = QLineEdit(str(config.client2_age))

        layout.addRow(self.client2_name_label, self.client2_name)
        layout.addRow(self.client2_age_label, self.client2_age)

        # Field for age to follow to
        self.age_to_follow_to_label = QLabel("Maximum age to model: ")
        self.age_to_follow_to = QLineEdit(str(config.age_to_follow_to)) # this needs to change another variable, as well: years_to_model
        layout.addRow(self.age_to_follow_to_label, self.age_to_follow_to)

        # Add conclusion text
        layout.addRow(age_label)

        # Submit button
        submit_button = QPushButton("Get started!")
        submit_button.clicked.connect(self.accept)
        layout.addRow(submit_button)

        # Set default values and update visibility based on 'individual_or_couple'
        self.individual_or_couple.setCurrentText(config.individual_or_couple)
        self.update_client2_visibility()

    def get_data(self):
        return {
            "individual_or_couple": self.individual_or_couple.currentText(),
            "client1_name": self.client1_name.text(),
            "client1_age": int(self.client1_age.text()),
            "client2_name": self.client2_name.text(),
            "client2_age": int(self.client2_age.text()) if self.client2_age.text() else 0,
            "age_to_follow_to": int(self.age_to_follow_to.text())
        }

    def update_client2_visibility(self):
        is_couple = self.individual_or_couple.currentText() == "couple"
        self.client2_name.setVisible(is_couple)
        self.client2_name_label.setVisible(is_couple)
        self.client2_age.setVisible(is_couple)
        self.client2_age_label.setVisible(is_couple)

def check_expiry():
    current_date = datetime.now().date()  # Get only the date part
    # Convert config.expiry_date to a datetime.date object if it's a string
    if isinstance(config.expiry_date, str):
        expiry_date = datetime.strptime(config.expiry_date, "%Y-%m-%d").date()
    else:
        expiry_date = config.expiry_date

    if current_date > expiry_date:
        formatted_date = expiry_date.strftime("%d %B %Y")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Sorry - this version of Flawcastr stopped operating on {formatted_date}.")
        msg.setWindowTitle("Program Expired")
        msg.exec_()
        return False
    return True

def apply_initial_window_data_to_config(client_info):
    config.individual_or_couple = client_info["individual_or_couple"]
    config.client1_name = client_info["client1_name"]
    config.client1_age = int(client_info["client1_age"])
    config.benchmark_age = config.client1_age
    config.client2_name = client_info.get("client2_name", "")
    config.client2_age = int(client_info.get("client2_age", 0))
    config.age_to_follow_to = int(client_info["age_to_follow_to"])

    # Update child ages
    config.child1_age = config.client1_age - 28
    config.child2_age = config.client1_age - 30
    config.child3_age = config.client1_age - 32
    config.child4_age = config.client1_age - 34
    config.child5_age = config.client1_age - 36

    # Update education start years
    config.education_start_year_child1 = config.age_of_providing_initial_educational_assistance - config.child1_age
    config.education_start_year_child2 = config.age_of_providing_initial_educational_assistance - config.child2_age
    config.education_start_year_child3 = config.age_of_providing_initial_educational_assistance - config.child3_age
    config.education_start_year_child4 = config.age_of_providing_initial_educational_assistance - config.child4_age
    config.education_start_year_child5 = config.age_of_providing_initial_educational_assistance - config.child5_age

    # Ensure all age-related variables are integers
    age_related_vars = ['client1_age', 'client2_age', 'benchmark_age', 'age_to_follow_to',
                        'child1_age', 'child2_age', 'child3_age', 'child4_age', 'child5_age',
                        'education_start_year_child1', 'education_start_year_child2', 
                        'education_start_year_child3', 'education_start_year_child4', 
                        'education_start_year_child5', 'client1_retirement_age', 'client2_retirement_age']
    
    for var in age_related_vars:
        if hasattr(config, var):
            setattr(config, var, int(getattr(config, var)))

    for key, value in client_info.items():
        setattr(config, key, value)

if __name__ == "__main__":
    app = QApplication([])

    # Load configuration relevant for the initial window
    load_initial_configuration()

    dialog = ClientInfoDialog()
    if dialog.exec_():
        client_info = dialog.get_data()
        
        # Update all relevant config variables
        config.individual_or_couple = client_info["individual_or_couple"]
        config.client1_name = client_info["client1_name"]
        config.client1_age = client_info["client1_age"]  # This is now an integer from get_data()
        config.client2_name = client_info["client2_name"]
        config.client2_age = client_info["client2_age"]  # This is now an integer from get_data()
        config.age_to_follow_to = client_info["age_to_follow_to"]  # This is now an integer from get_data()
        
        # Update dependent variables
        config.years_to_model = config.age_to_follow_to - config.client1_age

        # Call apply_initial_window_data_to_config here
        apply_initial_window_data_to_config(client_info)

        if check_expiry():
            # Only import viz and instantiate MyWindow after user input is processed
            from viz import MyWindow
            visualization_window = MyWindow()
            visualization_window.show()
            app.exec_()