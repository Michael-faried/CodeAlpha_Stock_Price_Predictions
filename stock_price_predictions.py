# -*- coding: utf-8 -*-
"""Stock Price Predictions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IvmCXObN6vipcsBtfS3hnRv-vD4I4g7T

### Import Data
"""

# !pip install kaggle
# !mkdir ~/.kaggle
# !cp kaggle.json ~/.kaggle/
# !chmod 600 ~/.kaggle/kaggle.json
# !kaggle datasets download khushipitroda/stock-market-historical-data-of-top-10-companies
# !unzip stock-market-historical-data-of-top-10-companies.zip

"""### **Data PreProcessing**"""

import pandas as pd
stock_data = pd.read_csv("data.csv")
stock_data.head(10)

print(stock_data.describe())
stock_data.info()

stock_data.isnull().sum()

stock_data.dtypes

# Create DataFrame
Stock_data = pd.DataFrame(stock_data)

# Normalize the date column to the 'MM/DD/YYYY' format
Stock_data['Date'] = Stock_data['Date'].astype(str).str.replace('-', '/')
Stock_data['Date'] = pd.to_datetime(Stock_data['Date'], format='%m/%d/%Y')  # Corrected format to '%Y'


# Remove dollar signs and convert numeric columns to float
numeric_columns = ['Close/Last', 'Open', 'High', 'Low']
Stock_data[numeric_columns] = Stock_data[numeric_columns].replace('[\$,]', '', regex=True).astype(float)

# Create a mapping dictionary for company abbreviations to real names
company_mapping = {
    'AAPL': 'Apple',
    'AMZN': 'Amazon',
    'SBUX': 'Starbucks',
    'MSFT': 'Microsoft',
    'CSCO': 'Cisco Systems',
    'QCOM': 'Qualcomm',
    'META': 'META',
    'TSLA': 'Tesla',
    'NFLX' : 'Netflix'
}

# Replace the company abbreviations with real names
Stock_data['Company'] = Stock_data['Company'].replace(company_mapping)

# Display the updated DataFrame
print(Stock_data)
print(stock_data.dtypes)

"""## Stock Analysis"""

# !pip install dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Stock price analysis'),
    dcc.Graph(id="time-series-chart"),
    html.P("Select stock:"),
    dcc.Dropdown(
        id="ticker",
        options=["Amazon", "Tesla", "Netflix","META","Microsoft"],
        value="Amazon",
        clearable=False,
        style={'width': '150px'}
    ),
])

@app.callback(
    Output("time-series-chart", "figure"),
    Input("ticker", "value"))
def display_time_series(ticker):
    company_data = Stock_data[Stock_data['Company'] == ticker]
    fig = px.line(company_data, x='Date', y='Close/Last', title=f'{ticker} Stock Price')
    fig.update_layout(title_x=0.5,width=1000,height=500 )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

# Reshape the data into long-form format
melted_data = Stock_data.melt(id_vars=['Company', 'Date'], value_vars=['Close/Last'], var_name='Attribute', value_name='Value')
# Create the area plot with subplots
fig = px.area(melted_data, x='Date', y='Value', facet_col="Company", facet_col_wrap=2, line_shape="linear",color="Company")

# Customize the plot layout
fig.update_layout(title='Stock Prices for Different Companies', xaxis_title='Date', yaxis_title='Close/Last')
fig.update_layout(title_x=0.5)

# Show the plot
fig.show()

# Assuming your 'Date' column is in datetime format
Stock_data['Year'] = Stock_data['Date'].dt.year

# Group the data by year and calculate the mean 'Close/Last' value for each year
grouped_data = Stock_data.groupby(['Year', 'Company'])['Close/Last'].mean().reset_index()

fig = px.line(grouped_data, x="Year", y="Close/Last", color="Company",
              hover_data=["Year", "Company", "Close/Last"],
              title='Custom Tick Labels')
fig.update_layout(title_x=0.5,width=900,height=500 )
fig.update_xaxes(
    dtick="Y1",
    tickformat="%Y")  # Use "%Y" to display only the year

fig.show()

# Filter data for the year 2023
Stock_data_2023 = Stock_data[Stock_data['Date'].dt.year == 2023]
Stock_data_2023['Profit'] = Stock_data_2023['Close/Last'] - Stock_data_2023['Open']

# Group the data by 'Company' and calculate the sum of 'Profit' for each company
profit_data = Stock_data_2023.groupby('Company')['Profit'].sum().reset_index()

# Create a bar plot for company profits
fig = px.bar(profit_data, x='Company', y='Profit', title='Company Stock Market Share Prices profits (2023)',color='Company')

# Center the title
fig.update_layout(title_x=0.5)

fig.update_xaxes(title_text='Company')
fig.update_yaxes(title_text='Profit')
# Set custom width and height
fig.update_layout(
    title_x=0.5,  # Center the title
    xaxis_title_text='Company',
    yaxis_title_text='Profit',
    width=900,     # Set custom width
    height=500     # Set custom height
)
fig.show()

"""### **Annualized_Volatility**"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Convert 'Date' column to datetime
Stock_data['Date'] = pd.to_datetime(Stock_data['Date'])

# Filter data for the year 2023
Stock_data_2023 = Stock_data[Stock_data['Date'].dt.year == 2023].copy()  # Make a copy to avoid SettingWithCopyWarning

# Calculate daily returns for each company in 2023
Stock_data_2023['Daily_Return'] = Stock_data_2023.groupby('Company')['Close/Last'].pct_change()

# Calculate daily volatility for each company in 2023
Stock_data_2023['Daily_Volatility'] = Stock_data_2023.groupby('Company')['Daily_Return'].transform('std')

# Assuming 252 trading days in a year, annualize volatility for 2023
trading_days_per_year = 252
Stock_data_2023['Annualized_Volatility'] = Stock_data_2023['Daily_Volatility'] * np.sqrt(trading_days_per_year)

# Sort data by annualized volatility in descending order
Stock_data_2023.sort_values(by='Annualized_Volatility', ascending=False, inplace=True)  # Use inplace=True to modify the DataFrame in place

# Create a color palette with different colors for each company
palette = sns.color_palette('husl', n_colors=len(Stock_data_2023['Company'].unique()))

# Create a bar plot for each company and annualized volatility in 2023
plt.figure(figsize=(10, 5.5))
sns.barplot(data=Stock_data_2023, x='Company', y='Annualized_Volatility', palette=palette)
plt.xlabel('Company')
plt.ylabel('Annualized Volatility')
plt.title('Annualized Volatility for Each Company in 2023 (Sorted by Volatility)')
plt.xticks(rotation=45)
plt.tight_layout()

# Show the bar plot
plt.show()

"""### **correlation matrix**"""

# Calculate the correlation matrix between companies

# Pivot the DataFrame to have companies as columns and Date as the index
pivot_df = Stock_data.pivot(index='Date', columns='Company', values='Close/Last')

# Calculate the correlation matrix
correlation_matrix = pivot_df.corr()

# Create a correlation heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Heatmap between Companies')
plt.show()

"""## **Linear Regression Model**

### Model Selection and Training
"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

X = Stock_data[['Company','Volume','Open','High','Low']]  # Features
y = Stock_data['Close/Last']  # Target variable

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_train)

# Create a LabelEncoder object
label_encoder = LabelEncoder()

# Fit and transform the 'Company' column in X_train
X_train['Company'] = label_encoder.fit_transform(X_train['Company'])

# Apply the same encoding to X_test
X_test['Company'] = label_encoder.transform(X_test['Company'])

print(X_train)
# Initialize the model
model= LinearRegression()

# Train the model on the training data
model.fit(X_train, y_train)

"""### Model Evaluation"""

y_pred = model.predict(X_test)

"""### Visualize the predictions"""

# Display the predicted and true values for the test set with € sign 3l4an ana gamed awy
data = []
for  pred, true in zip( y_test , y_pred):
    data.append({ 'True Value': round(pred), 'Predicted Value': round(true)})
data = pd.DataFrame(data)

def convert_value(value):
    if value >= 1000000:
        return f'${value/1000000:.2f}M'
    elif value >= 1000:
        return f'${value/1000:.2f}K'
    else:
        return f'${value:.0f}'

data['Predicted Value'] = data['Predicted Value'].apply(convert_value)
data['True Value'] = data['True Value'].apply(convert_value)
print("The Length of testing data : " + str(len(data)))
data

"""### Evaluate the model's performance

"""

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R-squared (R2) Score: { round(r2*100,2)}%")

"""# THANKS :)"""