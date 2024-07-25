# There is currently an issue with horizontal axis - it's fine right now but when benchmark age changes, the plot changes but the horizontal axis doesn't

from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QLabel, QComboBox, QScrollArea, QFrame, QCheckBox, QPushButton, QSizePolicy, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from calcs import simulate_annual_investment_balances
import config
import os
import numpy as np
import pandas as pd
from viz_widgets import init_input_widget



###### TRY USING THESE FOR VIZ STYLING??? #########
qwidget_background_colour = '#F2EFE9'  # Light grayish beige
qsplitter_background_colour = '#ECE7E3'  # Soft gray
qscrollarea_background_colour = '#F7F5F2'  # Very light beige
init_plot_widget_facecolor = '#F7F5F2'  # Very light beige (same as QScrollArea)
init_plot_widget_stylesheet_background_color = '#F7F5F2'  # Very light beige (same as Plot Widget Facecolor)




def currency_formatter(x, pos):
    return "${:,.0f}".format(x)


def on_save_variables_button_clicked():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Define BASE_DIR before using it
    csv_path = os.path.join(BASE_DIR, 'default.csv')  # Change the file extension to .csv
    save_config_to_excel(config, csv_path)




def save_config_to_excel(config_module, csv_path):
    # Create a DataFrame with two columns: Variable and Value
    data = {
        'Variable': [],
        'Value': []
    }

    # Add the configuration variables and their values to the DataFrame
    for var in dir(config_module):
        # Filter out built-in attributes and methods
        if not var.startswith('__') and not callable(getattr(config_module, var)):
            data['Variable'].append(var)
            data['Value'].append(getattr(config_module, var))

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Convert the 'Variable' column to the title case and replace underscores with spaces
    df['Variable'] = df['Variable'].str.replace('_', ' ').str.title()

    # Write the DataFrame to a CSV file
    df.to_csv(csv_path, index=False)

    print(f"Configuration saved to {csv_path}")



class MyWindow(QMainWindow):
    plot_needs_update = pyqtSignal()  # Create a signal to update plot
    
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Flawcastr")
        self.setWindowState(Qt.WindowMaximized)

        self.saved_scenarios = []  # Attribute to store saved scenarios
        self.validation_labels = {}
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.setStyleSheet(f"QWidget {{ background-color: {qwidget_background_colour}; }}")
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {qsplitter_background_colour}; }}")

        self.config_var_format = {}
        
        init_input_widget(self)  # Initialize input widgets

        self.input_widget.setStyleSheet("font-size: 11pt;")


        # Initialize this attribute before calling update_plot
        self.last_deterministic_balances = None

        self.init_plot_widget()  # Initialize plot widget
        self.init_table_widget()  # Initialize table widget


        scroll = QScrollArea()  # Existing line

        scroll.setStyleSheet(f"""
        QScrollArea {{ border: none; background-color: {qscrollarea_background_colour}; }}
        QScrollBar:vertical {{
            border: none;
            background: lightgrey;
            width: 5px;
            opacity: 0.25;
        }}
        QScrollBar::handle:vertical {{
            background: lightgrey;
            min-height: 10px;
        }}
        """)


        scroll.setWidgetResizable(True)  # Existing line
        scroll.setWidget(self.input_widget)  # Existing line

        self.splitter.addWidget(scroll)  # Add the scroll area to the splitter instead of self.input_widget
        self.splitter.addWidget(self.canvas)
        self.splitter.addWidget(self.table_widget)

        self.splitter.setSizes([500, 800, 50])  # Adjust these values as needed

        self.setCentralWidget(self.splitter)
       
        
        self.plot_needs_update.connect(self.update_plot)  # Connect the signal to update the plot
        self.update_plot()  # Initial call to update the plot after all widgets are initialized


    def init_plot_widget(self):
        self.fig = Figure(facecolor=init_plot_widget_facecolor)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet(f"background-color: {init_plot_widget_stylesheet_background_color};")

        self.update_plot()

    def init_table_widget(self):
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)

        self.table_widget.setStyleSheet("font-size: 11pt;")

        # Place Save and Clear buttons at the top
        save_button = QPushButton("Save scenario for comparison")
        save_button.clicked.connect(self.on_save_scenario_clicked)
        table_layout.addWidget(save_button)

        clear_button = QPushButton("Clear saved scenarios")
        clear_button.clicked.connect(self.on_clear_scenarios_clicked)
        table_layout.addWidget(clear_button)

        background_text = f"""
        <p></p>
        <p></p>
        <p>This is a beta version of Flawcastr, made available by Sonnie Bailey for feedback only. This version of Flawcastr will stop operating on 1 October 2024.</p>
        <p>Note that <strong>this tool is called Flawcastr. This is because all "forecasts" are "flawcasts", in the sense that they will be wrong.</strong> For one thing, no variable or assumption will hold exactly over time. On top of this, calculations in this beta version have not been extensively validated. Use Flawcastr in conjunction with other tools and professional advice.</p>
        <p>Information about this tool can be found here: www.sonniebailey.com/flawcastr. It is designed for New Zealanders. It doesn't provide recommendations relating to financial products, nor does it represent a financial plan.</p>
        <p>The future of Flawcastr, including whether it remains available beyond 1 October 2024 and whether functionality improves, will depend on whether I receive feedback and the type of feedback I receive.</p>
        """

        info_label = QLabel(background_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.RichText)  # Set text format to RichText
        info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Allow label to expand
        info_label.setAlignment(Qt.AlignTop)  # Align text to the top
        info_label.setStyleSheet("padding: 16pt;")  # Add 16 pt padding on all sides

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(info_label)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow scroll area to expand
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remove the border

        # Add the scroll area to the layout
        table_layout.addWidget(scroll_area)

        # save_variables_button = QPushButton("MAKE THESE VARIABLES THE DEFAULT")
        # save_variables_button.clicked.connect(on_save_variables_button_clicked)
        # table_layout.addWidget(save_variables_button)

        feedback_button = QPushButton("Leave feedback")
        feedback_button.clicked.connect(self.open_email_client)
        table_layout.addWidget(feedback_button)

        self.table_widget.setLayout(table_layout)

    def open_email_client(self):
        email = 'sonnie.bailey@outlook.com'
        subject = 'Flawcastr feedback'
        body = ''

        QDesktopServices.openUrl(QUrl(f'mailto:{email}?subject={subject}&body={body}', QUrl.TolerantMode))



    def on_save_scenario_clicked(self):
        # Open a dialog box for the user to input the scenario name
        scenario_name, ok = QInputDialog.getText(self, "Save Scenario", "Enter scenario name:")
        if ok:
            # Save the current deterministic balances as a scenario
            try:
                deterministic_balances, _, _ = simulate_annual_investment_balances()
                self.saved_scenarios.append(deterministic_balances)
                self.validation_labels[scenario_name] = deterministic_balances
                self.update_plot()
                # Update the scenario name label
                self.scenario_name_label.setText(f"Scenario Name: {scenario_name}")  # Include "Scenario Name: "
            except Exception as e:
                print(f"Error")



    def on_clear_scenarios_clicked(self):
        # Clear the saved scenarios and update the plot
        self.saved_scenarios.clear()
        self.validation_labels.clear()
        self.update_plot()

    def update_plot(self):
        try:
            years = self.calculate_years()  # Recalculate the years
            self.clear_and_plot_previous_balances(years)
            self.plot_saved_scenarios(years)
            self.plot_probabilistic_balances(years)
            self.plot_deterministic_balances(years)
            self.set_plot_aesthetics()
        except Exception as e:
            # Handle or log the exception
            print(f"Error updating the plot: {e}")
            # Optionally, clear the plot or display an error message on the plot
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Error: Unable to update the plot', transform=self.ax.transAxes, ha="center", va="center")
        finally:
            self.canvas.draw()  # Ensure the canvas is updated


    def calculate_years(self):
        years_to_model = config.age_to_follow_to - config.client1_age
        return np.arange(config.client1_age, config.client1_age + years_to_model + 1, 1)

    def clear_and_plot_previous_balances(self, years):
        self.ax.clear()
        if self.last_deterministic_balances:
            # Adjust 'years' to match the length of 'last_deterministic_balances'
            if len(years) != len(self.last_deterministic_balances):
                # If 'years' is shorter, assume it's missing the final year and extend it
                if len(years) < len(self.last_deterministic_balances):
                    years = np.arange(len(self.last_deterministic_balances))
                # If 'years' is longer, truncate it to match 'last_deterministic_balances'
                else:
                    years = years[:len(self.last_deterministic_balances)]

            # Add config.client1_age to 'years' for plotting
            adjusted_years = years + config.client1_age

            try:
                self.ax.plot(adjusted_years, self.last_deterministic_balances, color='green', linewidth=1, label='Previous Deterministic')
            except Exception as e:
                self.ax.text(0.5, 0.5, 'Error: Invalid data for plotting', transform=self.ax.transAxes, ha="center", va="center")

        self.canvas.draw()  # Ensure the canvas is updated even if there's an error


    def plot_deterministic_balances(self, years):
        try:
            deterministic_balances, _, _ = simulate_annual_investment_balances()
            if len(years) != len(deterministic_balances):
                adjusted_years = np.arange(len(deterministic_balances)) + config.client1_age
            else:
                adjusted_years = years + config.client1_age

            self.ax.plot(adjusted_years, deterministic_balances, color='black', linewidth=3, label='Deterministic')
            self.last_deterministic_balances = deterministic_balances

            # Store the maximum deterministic balance
            self.max_deterministic_balance = max(deterministic_balances)

        except Exception as e:
            print(f"Error: {e}")
            self.ax.text(0.5, 0.5, 'Error: Unable to simulate balances', transform=self.ax.transAxes, ha="center", va="center")
        finally:
            self.canvas.draw()

    def plot_saved_scenarios(self, years):

        if self.validation_labels:

            for name, scenario in self.validation_labels.items():

                if len(years) != len(scenario):
                    adjusted_years = np.arange(len(scenario)) + config.client1_age
                else:
                    adjusted_years = years + config.client1_age

                self.ax.plot(adjusted_years, scenario, 
                            color='pink', linewidth=2, alpha=0.7)

                # Position text label 
                last_x = adjusted_years[-1]  
                last_y = scenario[-1]   
                x_pos = last_x   
                y_pos = last_y

                self.ax.text(x_pos, y_pos, name, fontsize=11)

    def plot_probabilistic_balances(self, years=None):
        if getattr(config, 'investment_probabilistic_approach_yes_or_no', 'no') == 'no':
            return
        _, _, probabilistic_scenarios = simulate_annual_investment_balances()

        # If years is None or its length doesn't match the probabilistic scenario length, create it.
        if years is None or len(years) != len(probabilistic_scenarios[0]):
            years = np.arange(len(probabilistic_scenarios[0]))

        adjusted_years = years + config.client1_age


        try:
            for scenario_balances in probabilistic_scenarios:
                self.ax.plot(adjusted_years, scenario_balances, color='gray', linewidth=1, alpha=0.25)
        except ValueError as e:
            print(f"Error")
            self.ax.text(0.5, 0.5, 'Error: Invalid data for plotting', transform=self.ax.transAxes, ha="center", va="center")
        except Exception as e:
            print(f"Error")
            self.ax.text(0.5, 0.5, 'Error: Unexpected plotting error', transform=self.ax.transAxes, ha="center", va="center")
        finally:
            self.canvas.draw()  # Update the canvas even if there's an error

    def set_plot_aesthetics(self):
        self.ax.set_xlabel(f"{config.client1_name}'s age")
        self.ax.set_ylabel('Investment assets')
        self.ax.set_ylim(bottom=0)

        # Set the maximum limit of the vertical axis to be twice the maximum deterministic balance
        max_vertical_limit = 2 * self.max_deterministic_balance if hasattr(self, 'max_deterministic_balance') else None
        if max_vertical_limit is not None:
            self.ax.set_ylim(top=max_vertical_limit)

        left_limit = config.client1_age
        right_limit = config.age_to_follow_to
        self.ax.set_xlim(left=left_limit, right=right_limit)

        self.ax.grid(True, which='both', linestyle='--', linewidth=0.25, color='gray', alpha=0.5)
        self.ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()