"""
Author: Alex Khinno
Filename: panel_car.py

Purpose: It creates an interactive holoviz panel using a
sankey and line plot diagram in order to illustrate the
used car market.
"""



import panel as pn
from car_proj import CAR
import pandas as pd
import sankey as sk
import matplotlib.pyplot as plt

# Loads javascript dependencies and configures Panel (required)
pn.extension()

# INITIALIZE API
api = CAR()
api.data_open('car_prices.csv')
columns = api.columns()
models, avg_price = api.car_models()

# WIDGET DECLARATIONS

# Search Widgets
car_col1 = pn.widgets.Select(name="Source Column", options=columns, value=columns[0])
car_col2 = pn.widgets.Select(name="Middle Column", options=columns, value =columns[1])
car_col3 = pn.widgets.Select(name="Target Column", options=columns, value=columns[2])
car_vals = pn.widgets.Select(name="Value Column", options=columns, value=columns[14])

model_selector = pn.widgets.Select(name="Car", options=models, value=models[0])

# Plotting widgets
width = pn.widgets.IntSlider(name="Width", start=250, end=2000, step=250, value=1500)
height = pn.widgets.IntSlider(name="Height", start=200, end=2500, step=100, value=800)
allowance = pn.widgets.IntSlider(name= 'Min Flow Value',
                                 start=5000, end=200000, step=10000, value=100000)
year_slider = pn.widgets.IntSlider(name='Year Slider',
                                   start=1900, end=2500, step=3, value=10)

# CALLBACK FUNCTIONS

def sankey_get_plot(car_col1, car_col2, car_col3, car_vals, allowance, height, width):
    """ This function plots a 3 level sankey diagram
    in which variables are selectable with a default
    comparison already established
    """
    col1_val = car_col1.value if hasattr(car_col1, 'value') else car_col1
    col2_val = car_col2.value if hasattr(car_col2, 'value') else car_col2
    col3_val = car_col3.value if hasattr(car_col3, 'value') else car_col3
    vals_val = car_vals.value if hasattr(car_vals, 'value') else car_vals
    allowance_val = allowance.value if hasattr(allowance, 'value') else allowance
    df = api.car[[car_col1, car_col2, car_col3, car_vals]].dropna()

    # Stage 1 transition
    ng = df[[col1_val, col2_val, vals_val]]
    ng.columns = ['srs', 'targ', 'vals']

    # Stage 2 transition
    gd = df[[col2_val, col3_val, vals_val]]
    gd.columns = ['srs', 'targ', 'vals']

    stacked = pd.concat([ng, gd])
    stacked = stacked[stacked['vals'] > allowance]

    fig = sk.show_sankey(stacked, 'srs', 'targ', vals='vals', width=width, height=height)
    return fig

def line_get_plot(brand, year, price):
    """ This function creates a line plot
    that allows the user to choose a brand and
    follow its selling price through the years of
    production
    """
    df = api.car.copy()
    df = df[df['make'] == brand]
    price_by_year = df.groupby('year')['sellingprice'].mean().sort_index()

    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(price_by_year.index, price_by_year.values, label = f'{brand} Average price')
    if year in price_by_year.index:
        price = price_by_year.loc[year]
        ax.plot(year, price, 'ro', label=f'{year} Price: ${price:,.0f}')
        ax.annotate(f"${price:,.0f}", xy=(year, price),
                    xytext=(year + 1, price + 1000),
                    arrowprops=dict(arrowstyle="->", color='red'))

    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Selling Price (USD)")
    ax.set_title(f"{brand} Price Trend Over Time")
    ax.legend()
    ax.grid(True)

    return fig

# CALLBACK BINDINGS (Connecting widgets to callback functions)

plot = pn.bind(sankey_get_plot, car_col1, car_col2,
               car_col3, car_vals, allowance, height, width
               )
line = pn.bind(line_get_plot, model_selector, year_slider, avg_price)

# DASHBOARD WIDGET CONTAINERS ("CARDS")

card_width = 320

search_card = pn.Card(
    pn.Column(
        # Widget 1
        car_col1,
        # Widget 2
        car_col2,
        # Widget 3
        car_col3,
        # Widget 4
        car_vals,
        #Widget 5
        model_selector
    ),
    title="Search", width=card_width, collapsed=False
)


plot_card = pn.Card(
    pn.Column(
        # Widget 1
        width,
        # Widget 2
        height,
        # Widget 3
        allowance
    ),

    title="Plot", width=card_width, collapsed=True
)


# LAYOUT

layout = pn.template.FastListTemplate(
    title="Used Car Sales",
    sidebar=[
        search_card,
        plot_card,
    ],
    theme_toggle=False,
    main=[
        pn.Tabs(
            ("Sankey", plot),  # Replace None with callback binding
            ("Line", line),  # Replace None with callback binding
            active=1  # Which tab is active by default?
        )

    ],
    header_background='#a93226'

).servable()

layout.show()