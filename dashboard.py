import pandas as pd
import numpy as np
import plotly.express as px
import panel as pn
from categorise_expenses import categorize_transactions
import os

if os.path.exists(os.path.join(os.getcwd(), "transactions_2022_2023_categorized.csv")):
    print("categorised expenses file already exists in the working directory...reading that file")
    df = pd.read_csv(os.path.join(os.getcwd(), "transactions_2022_2023_categorized.csv"))
else:
    # Read the transactions_2022_2023.csv file 
    df = pd.read_csv("transactions_2022_2023.csv")

    # add the category column using llm
    df = categorize_transactions(df)

# Add year and month columns
df['Year'] = pd.to_datetime(df['Date']).dt.year
df['Month'] = pd.to_datetime(df['Date']).dt.month
df['Month Name'] = pd.to_datetime(df['Date']).dt.strftime("%b")

# For Income rows, assign Name / Description to Category
df['category'] = np.where(df['Expense/Income'] == 'Income', df['Name / Description'], df['category'])

### Make pie charts - Income/ Expense breakdown
def make_pie_chart(df, year, label):
    # Filter the dataset for expense transactions
    sub_df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]

    color_scale = px.colors.qualitative.Set2
    
    pie_fig = px.pie(sub_df, values='Amount (EUR)', names='category', color_discrete_sequence = color_scale)
    pie_fig.update_traces(textposition='inside', direction ='clockwise', hole=0.3, textinfo="label+percent")

    total_expense = df[(df['Expense/Income'] == 'Expense') & (df['Year'] == year)]['Amount (EUR)'].sum() 
    total_income = df[(df['Expense/Income'] == 'Income') & (df['Year'] == year)]['Amount (EUR)'].sum()
    
    if label == 'Expense':
        total_text = "€ " + str(round(total_expense))

        # Saving rate:
        saving_rate = round((total_income - total_expense)/total_income*100)
        saving_rate_text = ": Saving rate " + str(saving_rate) + "%"
    else:
        saving_rate_text = ""
        total_text = "€ " + str(round(total_income))

    pie_fig.update_layout(uniformtext_minsize=10, 
                        uniformtext_mode='hide',
                        title=dict(text=label+" Breakdown " + str(year) + saving_rate_text),
                        # Add annotations in the center of the donut.
                        annotations=[
                            dict(
                                text=total_text, 
                                # Square unit grid starting at bottom left of page
                                x=0.5, y=0.5, font_size=12,
                                # Hide the arrow that points to the [x,y] coordinate
                                showarrow=False
                            )
                        ]
                    )
    return pie_fig

income_pie_fig_2022 = make_pie_chart(df, 2022, 'Income')

### Make bar charts over months in a year
def make_monthly_bar_chart(df, year, label):
    df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
    total_by_month = (df.groupby(['Month', 'Month Name'])['Amount (EUR)'].sum()
                        .to_frame()
                        .reset_index()
                        .sort_values(by='Month')  
                        .reset_index(drop=True))
    if label == "Income":
        color_scale = px.colors.sequential.YlGn
    if label == "Expense":
        color_scale = px.colors.sequential.OrRd
    
    bar_fig = px.bar(total_by_month, x='Month Name', y='Amount (EUR)', text_auto='.2s', title=label+" per month", color='Amount (EUR)', color_continuous_scale=color_scale)
    # bar_fig.update_traces(marker_color='lightslategrey')
    
    return bar_fig

income_monthly_2022 = make_monthly_bar_chart(df, 2022, 'Income')

### Putting all charts together into tabs for 2022/2023
# Pie charts
income_pie_fig_2022 = make_pie_chart(df, 2022, 'Income')
expense_pie_fig_2022 = make_pie_chart(df, 2022, 'Expense')  
income_pie_fig_2023 = make_pie_chart(df, 2023, 'Income')
expense_pie_fig_2023 = make_pie_chart(df, 2023, 'Expense')

# Bar charts
income_monthly_2022 = make_monthly_bar_chart(df, 2022, 'Income')
expense_monthly_2022 = make_monthly_bar_chart(df, 2022, 'Expense')
income_monthly_2023 = make_monthly_bar_chart(df, 2023, 'Income')
expense_monthly_2023 = make_monthly_bar_chart(df, 2023, 'Expense')

# Create tabs
tabs = pn.Tabs(
                        ('2022', pn.Column(pn.Row(income_pie_fig_2022, expense_pie_fig_2022),
                                                pn.Row(income_monthly_2022, expense_monthly_2022))),
                        ('2023', pn.Column(pn.Row(income_pie_fig_2023, expense_pie_fig_2023),
                                                pn.Row(income_monthly_2023, expense_monthly_2023))
                        )
                )

### Create dashboard

# Dashboard template
template = pn.template.FastListTemplate(
    title='Personal Finance Dashboard',
    sidebar=[pn.pane.Markdown("# Income Expense analysis"), 
             pn.pane.Markdown("Overview of income and expense based on my bank transactions. Categories are obtained using local LLMs."),
             pn.pane.PNG("picture.png", sizing_mode="scale_both")
             ],
    main=[pn.Row(pn.Column(pn.Row(tabs)
                           )
                ),
                ],
    # accent_base_color="#88d8b0",
    header_background="#c0b9dd",
)

if __name__ == "__main__":
    template.servable()
    pn.serve(template, host="0.0.0.0", port=8888, show=False, allow_websocket_origin=["localhost:8888"])