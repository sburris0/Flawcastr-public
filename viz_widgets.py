from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QLabel, QComboBox, QScrollArea, QFrame, QLineEdit, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QCheckBox
from PyQt5.QtCore import Qt
import config  # Import the config module to access the variable

line_edit_background_colour = '#F7F5F2' 

# Common style for [?] buttons
explanation_button_style = """
    QLabel {
        color: blue;
        font-weight: bold;
        font-size: 12px;
        border: 1px solid black;
        border-radius: 5px;
        padding: 2px;
        background-color: #f0f0f0;
    }
    QLabel:hover {
        background-color: #e1e1e1;
    }
"""


def update_client_details_label(window):
    if getattr(config, 'individual_or_couple', 'individual') == 'individual':
        # For an individual, use this format
        client1_name = getattr(config, 'client1_name', '')
        client1_age = getattr(config, 'client1_age', '')
        client_details_text = f"<b>Flawcast assumptions for {client1_name} ({client1_age}):</b>"
    else:
        # For a couple, use a different format
        client1_name = getattr(config, 'client1_name', '')
        client1_age = getattr(config, 'client1_age', '')
        client2_name = getattr(config, 'client2_name', '')
        client2_age = getattr(config, 'client2_age', '')
        client_details_text = f"<b>Flawcast assumptions for {client1_name} ({client1_age}) and {client2_name} ({client2_age}):</b>"

    additional_text = "<br></br><br>All figures below are in today's dollars.</b>"

    client_details_text += additional_text

    window.client_details_label.setText(client_details_text)

def add_combobox(window, var_name, options):
    h_layout = QHBoxLayout()
    label = QLabel(var_name.replace('_', ' ').capitalize() + ":")
    combobox = QComboBox()
    combobox.addItems(options)
    combobox.currentIndexChanged.connect(lambda index, var=var_name, cb=combobox: on_combobox_changed(window, var, cb))
    window.config_fields[var_name] = combobox

    h_layout.addWidget(label)
    h_layout.addWidget(combobox)
    window.input_layout.addLayout(h_layout)

    # Check the state of the 'explanations' variable
    explanations_enabled = getattr(config, 'explanations', 'yes') == 'yes'
    combobox.setVisible(explanations_enabled)
    label.setVisible(explanations_enabled)


def on_combobox_changed(window, var_name, combobox):
    new_value = combobox.currentText()
    setattr(config, var_name, new_value)
    window.plot_needs_update.emit()

def add_toggle(window, var_name, toggled_items, item_dict):
    h_layout = QHBoxLayout()
    label_text = item_dict.get('label', var_name.replace('_', ' ').capitalize())
    
    toggle = QCheckBox(label_text)
    window.config_fields[var_name] = toggle

    # Set the checkbox state based on the config value
    if var_name == 'individual_or_couple':
        initial_state = getattr(config, var_name) == 'couple'
    else:
        initial_state = getattr(config, var_name) == 'yes'
    toggle.setChecked(initial_state)


    h_layout.addWidget(toggle)
    window.input_layout.addLayout(h_layout)

    # Connect the signal to the on_toggle_changed function
    toggle.stateChanged.connect(lambda state, var=var_name, items=toggled_items: 
                                on_toggle_changed(window, var, state, items))

    # Set initial state and create fields if necessary
    on_toggle_changed(window, var_name, toggle.checkState(), toggled_items)

    # Add tooltip label for explanation if provided
    if 'explanation' in item_dict:
        tooltip_text = item_dict['explanation']
        tooltip_label = QLabel('?')
        tooltip_label.setStyleSheet("""
            QLabel {
                color: blue;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid black;
                border-radius: 5px;
                padding: 2px;
                background-color: #f0f0f0;
            }
            QLabel:hover {
                background-color: #e1e1e1;
            }
        """)
        tooltip_label.setToolTip(tooltip_text)
        h_layout.addWidget(tooltip_label)
        h_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))  

    # Check the state of the 'explanations' variable
    explanations_enabled = getattr(config, 'explanations', 'yes') == 'yes'
    toggle.setVisible(explanations_enabled)

def update_config_and_plot(window, var_name, state, items):
    new_value = 'yes' if state == Qt.Checked else 'no'
    setattr(config, var_name, new_value)  # Update the config variable
    window.plot_needs_update.emit()

def on_toggle_changed(window, var_name, state, items):
    if var_name == 'individual_or_couple':
        if state == Qt.Unchecked:
            new_value = 'individual'
        elif state == Qt.Checked:
            new_value = 'couple'
    else:
        new_value = 'yes' if state == Qt.Checked else 'no'

    setattr(config, var_name, new_value)

    update_field_visibility(window)

    window.plot_needs_update.emit()


def update_text_visibility(window, explanations_state):
    explanations_enabled = explanations_state == 'yes'
    for key, widget in window.config_fields.items():
        if key.startswith('text_'):
            widget.setVisible(explanations_enabled)



config_var_list = [
    # WANT THESE DICTIONARIES TO ALSO ALLOW FOR WHAT THIS WILL LOOK LIKE ON THE SCREEN - APPEARS BY DEFAULT IT IS BASED ON VARIABLE NAME, BUT REMOVING THE _ AND CAPITALS)
    

    {'type': 'divider'},
    {'type': 'input', 'var_name': 'opening_investment_balance', 'label': 'Opening investment balance ($)', 'explanation': 'This represents investment assets, EXCLUDING personal or lifestyle assets, such as the family home(s), vehicles, and the like. If you own a business that you will eventually sell, it is usually best to exclude the value of the business and include its eventual sale as one-off items below. If you have a mortgage repayment and want to include principal repayments on the mortgage as part of your savings (below), subtract your mortgage. If you treat savings (below) as being separate from mortgage repayments, ignore your mortgage.'},
    {'type': 'divider'},


    {'type': 'input', 'var_name': 'current_savings_rate', 'label': 'Current savings rate ($)'},

    {'type': 'input', 'var_name': 'savings_rate_change_age', 'label': 'Age savings rate changes', 'explanation': "Savings rate might change due to repayment of the mortgage (which should free up cash flow for investing; only factor this in if you haven't been including principal repayments on your mortgage as savings already) or children becoming independent."},
    {'type': 'input', 'var_name': 'updated_savings_rate', 'label': 'Updated savings rate after this age'},
    # {'type': 'input', 'var_name': 'savings_rate_change2_age', 'label': 'Age savings rate changes (after the previous change)'},
    # {'type': 'input', 'var_name': 'updated_savings_rate_2', 'label': 'Updated savings rate', 'explanation': 'Enter the updated savings rate after the second change age.'},
    # {'type': 'input', 'var_name': 'post_retirement_earned_income', 'label': 'Earned income in initial year(s) after retirement', 'explanation': 'This covers the possibility of generating an income after retirement. Note that this relates to INCOME, not savings. Once the retirement age has been hit, the presumption is that withdrawals will be made from inveetment assets (and/or returns generated by these assets). Any income generated beyond retirement will be considered as a contribution to invsetment assets (which is the same as going towards annual expenses).'},
    # {'type': 'input', 'var_name': 'post_retirement_years_of_earned_income'},


    {'type': 'divider'},
    {'type': 'input', 'var_name': 'investment_threshold', 'label': 'Investment threshold ($)', 'explanation': "This adds a small amount of nuance to investment returns. For example, if the investment threshold is 0.05 and the investment returns under threshold is 0.03, then the investment returns will be 0.03 if the investment balance is less than 5% of the opening investment balance, and 0.05 if the investment balance is greater than 5% of the opening investment balance."},
    {'type': 'input', 'var_name': 'investment_returns_under_threshold', 'label': 'Investment returns under the threshold (adjusted for inflation) (%)'},
    {'type': 'input', 'var_name': 'investment_returns_over_threshold', 'label': 'Investment returns over the threshold (adjusted for inflation) (%)'},
    {'type': 'text', 'text': "IMPORTANT: INVESTMENT RETURNS SHOULD BE IN REAL TERMS ", 'explanation': "Ie, investment returns should be adjusted for inflation. If nominal returns are 5%, for instance, and inflation is 2%, then the real return should be listed as 3%. If this adjustment is not made, then projections will be too optimistic."},
    {'type': 'text', 'text': "Also: Flawcastr does not consider leverage ", 'explanation': "DO NOT USE THIS MODEL TO ASSESS WHETHER TO BORROW TO INVEST. Flawcastr currently doesn't factor in the effect of leverage (for good or bad) on investment outcomes. To the extent this tool is useful for people who are considering whether to borrow to invest, it might help the user to inform whether it is necessary for them to do so in order to meet their financial objectives. If a user has a mortgage, for instance, the simplest way to treat this separately from investment assets, and treat mortgage repayments as expenditure. If and when they expect to repay their mortgage, they can then adjust savings levels to reflect their increased cash flow. If a user takes out a mortgage to buy a house and this requires a deposit that comes from investment assets, that would represent a withdrawal from investment assets (or for the amount they have initially saved, and any contributions to this amount to be ignored as savings for the purpose of this model)."},
    {'type': 'divider'},
    {'type': 'toggle', 'var_name': 'investment_probabilistic_approach_yes_or_no', 'label': 'Show Monte Carlo scenarios', 'explanation': "This shows 20 scenarios that are identical to the deterministic (dark black) scenario, with the one exception being that investment returns each year are randomly* generated. More specifically, each of the 20 scenarios assumes that investment returns follow a normal distribution, with the mean and standard deviation for under- and above-threshold returns being the same as what you haveve selected above. So if under-threshold returns are 1%, then the mean and standard deviation for under-threshold returns will be 1%. If above-threshold returns are 4%, then the mean and standard deviation for above-threshold returns will be 4%. Investment returns do not follow a normal distribution. The most important lesson to take out of this is that investment returns are not likely to be constant, and outcomes can vary significantly. (The same is true with all other variables, which is why this is a FLAWcast, not a forecast!"},
    {'type': 'divider'},
    {'type': 'input', 'var_name': 'client1_retirement_age', 'label': 'Age of retirement (age of first-listed user)'},
    {'type': 'input', 'var_name': 'retirement_expenditure_couple', 'label': 'Initial retirement expenditure (couple) ($)', 'conditional_on': lambda: config.individual_or_couple == 'couple'},
    {'type': 'input', 'var_name': 'age_when_one_passes_away', 'explanation': '(Only relevant for couples.) This morbid scenario is to factor in ongoing financial ramifications associated with one person in a couple passing away. For the purpose of this model, it impacts NZ Super levels and also expenditure.', 'conditional_on': lambda: config.individual_or_couple == 'couple'},
    {'type': 'input', 'var_name': 'retirement_expenditure_individual', 'label': 'Retirement expenditure (individual) ($)'},
    {'type': 'input', 'var_name': 'age_retirement_expenditure_starts_reducing', 'explanation': "At a certain point during retirement, expenditure tends to reduce. As people go through retirement they often has less energy and inclination to spend money they might have spent earlier in their retirement. This variable and the variables below consider the possibility that from a certain point, retirement expenditure will reduce (in real terms) by a certain percentage each year, down to a certain minimum level of expenditure."},
    {'type': 'input', 'var_name': 'retirement_expenditure_annual_reduction', 'label': 'Reduction in annual retirement expenditure (in real terms) (%)'},
    {'type': 'input', 'var_name': 'retirement_expenditure_minimum_couple', 'label': 'Minimum retirement expenditure - couple ($)', 'conditional_on': lambda: config.individual_or_couple == 'couple'},
    {'type': 'input', 'var_name': 'retirement_expenditure_minimum_individual', 'label': 'Minimum retirement expedniture - individual ($)'},

    
    {'type': 'divider'},
    {'type': 'input', 'var_name': 'nz_super_age_eligibility', 'label': 'NZ Super - age of eligibility', 'explanation': 'At the time of preparing this model, NZ Super is universal. With very limited exceptions, so long as you qualify for NZ Super you get the same amount, regardless of your asset position or other forms of income. There might be some nuances - for instance, for some people, NZ Super income might be taxed at a different level and there might be other benefits. To keep this model simple it assumes that NZ Super will remain the same level (adjusted for inflation) once the user becomes eligible for it.'},
    {'type': 'input', 'var_name': 'nz_super_couple_both', 'label': 'NZ Super - annual amount for a couple where both are eligible ($)', 'conditional_on': lambda: config.individual_or_couple == 'couple'},
    {'type': 'input', 'var_name': 'nz_super_couple_one_of_two', 'label': 'NZ Super - annual amount for a couple where only one is eligible ($)', 'conditional_on': lambda: config.individual_or_couple == 'couple'},
    {'type': 'input', 'var_name': 'nz_super_individual', 'label': 'NZ Super - annual amount for an individual ($)'},
    {'type': 'divider'},

    {'type': 'input', 'var_name': 'periodic_expenditure', 'label': 'Periodic expenditure ($)', 'explanation': "This represents periodic expenditure that might be incurred very few years, such as car purchases, house repairs and renovations, and/or overseas trips. It assumes the money spent on these one-off items will represent reduced savings during that year or will require withdrawing from investment assets. If you are likely to be able to continue investment savings at the same rate then you don't need to factor in these periodic expenditures."},
    {'type': 'input', 'var_name': 'age_periodic_expenditure_begins'},
    {'type': 'input', 'var_name': 'periodic_expenditure_frequency', 'label': 'Number of years from one set of periodic expenditure to the next'},
    {'type': 'input', 'var_name': 'age_periodic_expenditure_ends', 'label': 'Age periodic expenditure stops being incurred'},

    {'type': 'divider'},
    {'type': 'toggle', 'var_name': 'allow_for_one_off_items_yes_or_no', 'label': 'Allow for one-off items?', 'explanation': "*Put incomings as positive numbers and outgoings as negative numbers.* One-off items below represent items significant incomings or outgoings on specific years. This might include windfalls (such as a business sale or inheritance), capital freed up by downsizing/rightsizing your home (after repaying any debt), or outgoings such as house renovations."},

    {
        'type': 'multi_input', 
        'var_name1': 'one_off_item1_age', 'label_one_off_item1_age': 'One-off item 1 - Age:', 
        'var_name2': 'one_off_item1', 'label_one_off_item1': 'Amount ($)',
        'conditional_on': lambda: config.allow_for_one_off_items_yes_or_no == 'yes'
    },
    {
        'type': 'multi_input', 
        'var_name1': 'one_off_item2_age', 'label_one_off_item2_age': 'One-off item 2 - Age:', 
        'var_name2': 'one_off_item2', 'label_one_off_item2': 'Amount ($)',
        'conditional_on': lambda: config.allow_for_one_off_items_yes_or_no == 'yes'
    },
    {
        'type': 'multi_input', 
        'var_name1': 'one_off_item3_age', 'label_one_off_item3_age': 'One-off item 3 - Age:', 
        'var_name2': 'one_off_item3', 'label_one_off_item3': 'Amount ($)',
        'conditional_on': lambda: config.allow_for_one_off_items_yes_or_no == 'yes'
    },
    {
        'type': 'multi_input', 
        'var_name1': 'one_off_item4_age', 'label_one_off_item4_age': 'One-off item 4 - Age:', 
        'var_name2': 'one_off_item4', 'label_one_off_item4': 'Amount ($)',
        'conditional_on': lambda: config.allow_for_one_off_items_yes_or_no == 'yes'
    },
    {
        'type': 'multi_input', 
        'var_name1': 'one_off_item5_age', 'label_one_off_item5_age': 'One-off item 5 - Age:', 
        'var_name2': 'one_off_item5', 'label_one_off_item5': 'Amount ($)',
        'conditional_on': lambda: config.allow_for_one_off_items_yes_or_no == 'yes'
    },



    ### NEED TO ADD ONE OFF ITEMS, CONTINGENT ON WHETHER THE ABOVE IS TICKED YES (HIDDEN/NOT VISIBLE IF NOT)
    {'type': 'divider'},

    {'type': 'toggle', 'var_name': 'providing_substantial_assistance_to_children_yes_or_no', 'label': 'Provide for substantial assistance to children?'},
    {'type': 'input', 'var_name': 'number_of_children', 'conditional_on': lambda: config.providing_substantial_assistance_to_children_yes_or_no == 'yes'},
    {'type': 'input', 'var_name': 'child1_age', 'conditional_on': lambda: config.number_of_children >= 1 and config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of first child'},
    {'type': 'input', 'var_name': 'child2_age', 'conditional_on': lambda: config.number_of_children >= 2 and config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of second child'},
    {'type': 'input', 'var_name': 'child3_age', 'conditional_on': lambda: config.number_of_children >= 3 and config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of third child'},
    {'type': 'input', 'var_name': 'child4_age', 'conditional_on': lambda: config.number_of_children >= 4 and config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of fourth child'},
    {'type': 'input', 'var_name': 'child5_age', 'conditional_on': lambda: config.number_of_children >= 5 and config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of fifth child'},
    {'type': 'input', 'var_name': 'annual_amount_of_educational_assistance', 'conditional_on': lambda: config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Annual amount of educational assistance ($)'},
    {'type': 'input', 'var_name': 'age_of_providing_initial_educational_assistance', 'conditional_on': lambda: config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of child when first providing significant educational assistance'},
    {'type': 'input', 'var_name': 'years_of_providing_educational_assistance', 'conditional_on': lambda: config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Number of years of providing educational assistance'},
    {'type': 'input', 'var_name': 'amount_of_one_off_assistance_to_children', 'conditional_on': lambda: config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Amount of one-off assistance to children ($)'},
    {'type': 'input', 'var_name': 'age_of_one_off_assistance_to_children', 'conditional_on': lambda: config.providing_substantial_assistance_to_children_yes_or_no == 'yes', 'label': 'Age of child when providing one-off assistance to children'},



    #  {'type': 'toggle', 'var_name': 'investment_probabilistic_approach_yes_or_no', 'toggled_items': [
    #     'investment_probabilistic_methodology_normal_sd_multiplier', 'investment_probabilistic_number_of_scenarios'
    # ]},
    # {'type': 'text', 'text': "The main purpose of the above variables is to illustrate that this is a FLAWCAST. None of the variables above are going to hold. In particular, investment returns are not going to be constant and will vary from year to year. If you select yes for including the probabilistic approach, it will show as many ~random scenarios as you choose. This will help you appreciate that there are many different possible outcomes. These ~random scenarios are actually generated assuming that returns follow a normal distribution, with a mean for under- and above-threshold returns being the same as what you've selected above. The standard deviation for under- or above-threshold returns are a multiple of the mean. If, for example, the multiplier is 0.25 and under-threshold returns are 1% and above-threshold returns are 4%, this means that the ~random returns will ultimately distribute around a mean of 1% and 4% respesctively, with standard deviations of 0.25% and 4% respectively. If, on the other hand, the multiplier is 2, the means will be the same but standard deviations will be 2% and 4%."},    # The input fields for 'investment_probabilistic_methodology_normal_sd_multiplier' and
    # # 'investment_probabilistic_number_of_scenarios' will be added dynamically based on the toggle state,
    # so they do not need to be explicitly added to config_var_list here.

    ]

def add_client_info(window, client):
    h_layout = QHBoxLayout()
    label_name = QLabel("Name:")
    field_name = QLineEdit(str(getattr(config, f"{client}_name")))
    field_name.setStyleSheet(f"background-color: {line_edit_background_colour};")
    window.config_fields[f"{client}_name"] = field_name

    h_layout.addWidget(label_name)
    h_layout.addWidget(field_name)

    label_age = QLabel("Age:")
    field_age = QLineEdit(str(getattr(config, f"{client}_age")))
    field_age.setStyleSheet(f"background-color: {line_edit_background_colour};")
    window.config_fields[f"{client}_age"] = field_age

    h_layout.addWidget(label_age)
    h_layout.addWidget(field_age)
    window.input_layout.addLayout(h_layout)




# Helper function to add dividers
def add_divider(window):
    # Add spacing before the divider
    window.input_layout.insertSpacing(window.input_layout.count(), 20)
    # Create and add the divider
    divider = QFrame()
    divider.setFrameShape(QFrame.HLine)
    divider.setFrameShadow(QFrame.Sunken)
    window.input_layout.addWidget(divider)
    # Add spacing after the divider
    window.input_layout.insertSpacing(window.input_layout.count(), 20)

def add_input_field(window, var_name, item_dict):
    h_layout = QHBoxLayout()

    label_text = item_dict.get('label', var_name.replace('_', ' ').capitalize() + ":")
    label = QLabel(label_text)

    # label.setWordWrap(True)
    # label.setFixedWidth(150)  # You can adjust the width according to your needs

    field = QLineEdit()
    field.setStyleSheet(f"background-color: {line_edit_background_colour};")


    # Store references to the label and field using unique keys
    label_key = f"{var_name}_label"
    field_key = f"{var_name}_field"
    window.config_fields[label_key] = label
    window.config_fields[field_key] = field

    # Set the initial value for the field
    if var_name in ['investment_returns_under_threshold', 'investment_returns_over_threshold', 'retirement_expenditure_annual_reduction']:
        # Convert the decimal to a whole number percentage for display
        initial_value = str(round(getattr(config, var_name, 0) * 100, 2))
    else:
        initial_value = str(getattr(config, var_name, ''))
    field.setText(initial_value)

    h_layout.addWidget(label)
    h_layout.addWidget(field)

    # Add tooltip label if there's an explanation
    tooltip_text = item_dict.get('explanation', '')
    if tooltip_text:
        tooltip_label = QLabel('?')
        tooltip_label.setStyleSheet("""
            QLabel {
                color: blue;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid black;
                border-radius: 5px;
                padding: 2px;
                background-color: #f0f0f0;
            }
            QLabel:hover {
                background-color: #e1e1e1;
            }
        """)
        tooltip_label.setToolTip(tooltip_text)
        h_layout.addWidget(tooltip_label)

    window.input_layout.addLayout(h_layout)

    # Connect the editingFinished signal to the on_field_edit_finish function
    field.editingFinished.connect(lambda: on_field_edit_finish(window, var_name, field))

    # Set visibility for field and label
    set_field_and_label_visibility(window, var_name, item_dict)

def add_text_with_explanation(window, text, explanation=""):
    h_layout = QHBoxLayout()

    # Create a QLabel for the text
    text_label = QLabel(text)
    # text_label.setWordWrap(True)
    h_layout.addWidget(text_label)

    # If there's an explanation, add a [?] button with tooltip
    if explanation:
        explanation_button = QLabel('[?]')
        explanation_button.setToolTip(explanation)
        explanation_button.setStyleSheet(explanation_button_style)
        h_layout.addWidget(explanation_button)

        # Add a stretch element to ensure the button takes minimal space
        h_layout.addStretch(1)

    # Consistent spacing as in other widgets
    h_layout.setSpacing(5)  # Adjust the spacing as needed

    window.input_layout.addLayout(h_layout)



def add_multi_input_field(window, item_dict):
    h_layout = QHBoxLayout()

    for index in range(1, 3):  # Assuming two pairs of var_name and label
        var_name_key = f'var_name{index}'
        label_key = f'label_{item_dict[var_name_key]}'

        if var_name_key in item_dict:
            var_name = item_dict[var_name_key]
            label_text = item_dict.get(label_key, var_name.replace('_', ' ').capitalize() + ":")

            label = QLabel(label_text)
            field = QLineEdit(str(getattr(config, var_name, '')))
            field.setStyleSheet(f"background-color: {line_edit_background_colour};")

            window.config_fields[f"{var_name}_label"] = label
            window.config_fields[var_name] = field

            field.editingFinished.connect(lambda var=var_name, fld=field: on_field_edit_finish(window, var, fld))

            h_layout.addWidget(label)
            h_layout.addWidget(field)

    window.input_layout.addLayout(h_layout)



def set_field_and_label_visibility(window, var_name, item_dict):
    field_visible = True  # Default visibility
    label_key = f"{var_name}_label"
    field_key = f"{var_name}_field"

    # Check for conditional visibility
    if 'conditional_on' in item_dict and not item_dict['conditional_on']():
        field_visible = False

    if label_key in window.config_fields:
        window.config_fields[label_key].setVisible(field_visible)
    if field_key in window.config_fields:
        window.config_fields[field_key].setVisible(field_visible)


def init_input_widget(window):
    window.input_widget = QWidget()
    window.input_layout = QVBoxLayout()
    window.input_layout.setAlignment(Qt.AlignTop)
    window.config_fields = {}

    # Add spacing above the client details label
    window.input_layout.addSpacing(20)  # Adjust the value as needed

    # Create and add the client details label
    window.client_details_label = QLabel()
    window.input_layout.addWidget(window.client_details_label)
    update_client_details_label(window)  # Initial update of the label

    # Add spacing below the client details label
    window.input_layout.addSpacing(20)  # Adjust the value as needed

    # Rest of the initialization code...


    # Check the initial state of the 'explanations' variable from config.py
    explanations_enabled = getattr(config, 'explanations', 'yes') == 'yes'

    # Initialize other UI components based on the config_var_list
    for item_dict in config_var_list:
        item_type = item_dict.get('type')
        var_name = item_dict.get('var_name', f"text_{len(window.config_fields)}")

        if item_type == 'divider':
            add_divider(window)
        elif item_type == 'multi_input':
            add_multi_input_field(window, item_dict)
        elif item_type == 'toggle':
            toggled_items = item_dict.get('toggled_items', [])
            add_toggle(window, var_name, toggled_items, item_dict)
        elif item_type == 'text':
            text = item_dict.get('text', "")
            explanation = item_dict.get('explanation', "")
            add_text_with_explanation(window, text, explanation)

        elif item_type == 'combobox':
            add_combobox(window, var_name, item_dict['options'])
        elif item_type in 'input':
            # Add widgets based on type
            add_widget_based_on_type(window, item_type, var_name, item_dict)

    update_field_visibility(window)

    window.input_widget.setLayout(window.input_layout)

def add_widget_based_on_type(window, widget_type, var_name, item_dict):
    explanations_enabled = getattr(config, 'explanations', 'yes') == 'yes'

    field_key = f"{var_name}_field"
    label_key = f"{var_name}_label"

    if widget_type == 'toggle':
        toggled_items = item_dict.get('toggled_items', [])
        add_toggle(window, var_name, toggled_items)
    elif widget_type == 'combobox':
        options = item_dict.get('options', [])
        add_combobox(window, var_name, options)
    elif widget_type == 'multi_input':
        add_multi_input_field(window, item_dict)
    elif widget_type == 'input':
        add_input_field(window, var_name, item_dict)

        # Set initial visibility for input fields and labels
        if field_key in window.config_fields:
            window.config_fields[field_key].setVisible(explanations_enabled)
        if label_key in window.config_fields:
            window.config_fields[label_key].setVisible(explanations_enabled)


def on_field_edit_finish(window, var_name, field):
    new_value = field.text()

    # Inline validation for specific fields
    if var_name == 'savings_rate_change_age':
        client1_current_age = getattr(config, 'client1_age', 0)
        if int(new_value) <= client1_current_age:
            field.setText(str(getattr(config, var_name, '')))
            return

    if var_name == 'savings_rate_change2_age':
        savings_rate_change_age = getattr(config, 'savings_rate_change_age', 0)
        if int(new_value) <= int(savings_rate_change_age):
            field.setText(str(getattr(config, var_name, '')))
            return

    try:
        # Special handling for percentage fields
        if var_name in ['investment_returns_under_threshold', 'investment_returns_over_threshold', 'retirement_expenditure_annual_reduction']:
            # Convert user input percentage back to decimal
            updated_value = float(new_value) / 100
        elif var_name.endswith('_age') or var_name == 'number_of_children':
            # Update age-related fields and number of children as integers
            updated_value = int(new_value)
        else:
            # Update other fields as floats
            updated_value = float(new_value)

        # Update the configuration variable
        setattr(config, var_name, updated_value)
    except ValueError:
        # If invalid input, reset the field to its previous value
        field.setText(str(getattr(config, var_name, '')))

    field.setModified(False)  # Reset the modified state

    # Update field visibility if the number of children has changed
    if var_name == 'number_of_children':
        update_field_visibility(window)

    # Emit signal to update the plot
    window.plot_needs_update.emit()


def update_field_visibility(window):
    for item in config_var_list:
        if 'var_name' in item and 'conditional_on' in item:
            conditional_visibility_func = item['conditional_on']
            is_visible = conditional_visibility_func()

            field_key = f"{item['var_name']}_field"
            label_key = f"{item['var_name']}_label"
            if field_key in window.config_fields:
                window.config_fields[field_key].setVisible(is_visible)
            if label_key in window.config_fields:
                window.config_fields[label_key].setVisible(is_visible)

        elif item['type'] == 'multi_input' and 'conditional_on' in item:
            is_visible = item['conditional_on']()
            for index in range(1, 3):
                var_name_key = f'var_name{index}'
                if var_name_key in item:
                    var_name = item[var_name_key]
                    field_key = var_name
                    label_key = f"{var_name}_label"
                    if field_key in window.config_fields:
                        window.config_fields[field_key].setVisible(is_visible)
                    if label_key in window.config_fields:
                        window.config_fields[label_key].setVisible(is_visible)



def update_config_var(window, var_name, new_value):
    try:
        # If the variable is 'investment_probabilistic_number_of_scenarios', ensure it's an integer
        if var_name == 'investment_probabilistic_number_of_scenarios':
            new_value = int(new_value)
        else:
            new_value = float(new_value)

        setattr(config, var_name, new_value)
        window.plot_needs_update.emit()  
    except ValueError:
        # Handle the error for invalid input
        pass
