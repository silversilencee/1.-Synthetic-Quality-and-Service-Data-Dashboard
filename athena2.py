import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the dataset
file_path = 'Malawi_SRWB FY2324-FY2425 (Aggregated).xlsx'  # Adjust this path to your local setup
df = pd.read_excel(file_path)

# Display initial information about the dataset
print("Dataset Info:")
print(df.info())
print("\nFirst few rows of the dataset:")
print(df.head())

# Drop columns with mostly NaN values or irrelevant columns
df = df.drop(columns=['Unnamed: 224'], errors='ignore')  # Drop irrelevant columns as an example

# Convert 'Months' column to datetime, specifying a format if possible
date_column = 'Months'  # Replace with actual date column name if different
if date_column in df.columns:
    try:
        df[date_column] = pd.to_datetime(df[date_column], format="%Y-%m", errors='coerce')
        print(f"\nConverted '{date_column}' to datetime format.")
    except ValueError:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
else:
    print(f"\nDate column '{date_column}' not found in the dataset. Please verify the correct column name.")

# Only keep monthly data (remove quarterly, midyear, and annual data)
# Assuming 'Schemes' column identifies quarterly/midyear/annual entries with terms like 'Qtr', 'Ann', or 'Mid'
if 'Schemes' in df.columns:
    # Select only numeric columns to sum
    numeric_columns = df.select_dtypes(include='number').columns
    # Exclude rows containing "Qtr," "Ann," or "Mid" in the 'Schemes' column
    monthly_data = df[~df['Schemes'].str.contains('Qtr|Ann|Mid', na=False)].reset_index(drop=True)

    # Sum monthly data for comparison
    monthly_totals = monthly_data.groupby(date_column)[numeric_columns].sum()
    print("\nMonthly Totals (Summed by Date):")
    print(monthly_totals)
else:
    print("'Schemes' column not found for filtering quarterly/midyear/annual data.")
    monthly_data = df.copy()

# Replace all 0 values with "-"
monthly_data = monthly_data.replace(0, "-")

# Replace all NaN values (empty cells) with "NaN"
monthly_data = monthly_data.fillna("NaN")

# Display final DataFrame info to confirm changes
print("\nFinal Data with Changes (0 replaced with '-' and empty cells with 'NaN'):")
print(monthly_data.head())

# Save the cleaned monthly-only data to a new CSV file
cleaned_file_path = 'cleaned_monthly_data(2).csv'
monthly_data.to_csv(cleaned_file_path, index=False)
print(f"Monthly-only data saved to {cleaned_file_path}")



# Load the cleaned data
file_path = 'cleaned_monthly_data(2).csv'
monthly_data = pd.read_csv(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Water Utility Dashboard"

app.layout = html.Div([
    html.H1("Water Utility Dashboard"),
    dcc.Tabs(id="tabs", value='production_billing', children=[
        dcc.Tab(label='Production & Billing', value='production_billing'),
        dcc.Tab(label='Customer & Connection Management', value='customer_management'),
        dcc.Tab(label='Service Quality & Response', value='service_quality'),
        dcc.Tab(label='Operational Efficiency', value='operational_efficiency'),
        dcc.Tab(label='Water Quality & Treatment', value='water_quality'),
        dcc.Tab(label='Infrastructure & Maintenance', value='infrastructure'),
        dcc.Tab(label='Financial Metrics', value='financial_metrics')
    ]),
    html.Div(id='tab-content')
])

# Define callbacks to update content based on the selected tab
@app.callback(Output('tab-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    # Render content for each tab
    if tab == 'production_billing':
        fig = px.line(monthly_data, x='Months', y='Volume Produced', title='Production & Billing Trends')
        return html.Div([html.H3('Production & Billing EDA'), dcc.Graph(figure=fig)])

    elif tab == 'customer_management':
        fig = px.line(monthly_data, x='Months', y='Total number of customers applied for new connection', title='New Connections Trends')
        return html.Div([html.H3('Customer & Connection Management EDA'), dcc.Graph(figure=fig)])

    elif tab == 'service_quality':
        fig = px.line(monthly_data, x='Months', y='Response time to queries', title='Service Quality & Response Trends')
        return html.Div([html.H3('Service Quality & Response EDA'), dcc.Graph(figure=fig)])

    elif tab == 'operational_efficiency':
        fig = px.line(monthly_data, x='Months', y='Power Usage', title='Operational Efficiency Trends')
        return html.Div([html.H3('Operational Efficiency EDA'), dcc.Graph(figure=fig)])

    elif tab == 'water_quality':
        if 'Chlorine (kg)' in monthly_data.columns:
            fig = px.line(monthly_data, x='Months', y='Chlorine (kg)', title='Water Quality & Treatment Trends')
            return html.Div([html.H3('Water Quality & Treatment EDA'), dcc.Graph(figure=fig)])
        else:
            return html.Div("Data for 'Chlorine (kg)' not found in this dataset.")

    elif tab == 'infrastructure':
        fig = px.line(monthly_data, x='Months', y='Total Breakdowns', title='Infrastructure & Maintenance Trends')
        return html.Div([html.H3('Infrastructure & Maintenance EDA'), dcc.Graph(figure=fig)])

    elif tab == 'financial_metrics':
        fig = px.line(monthly_data, x='Months', y='Total Cash Collected', title='Financial Metrics Trends')
        return html.Div([html.H3('Financial Metrics EDA'), dcc.Graph(figure=fig)])

if __name__ == '__main__':
    app.run_server(debug=True)


