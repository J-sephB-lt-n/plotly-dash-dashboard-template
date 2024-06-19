import csv
import pandas as pd
import plotly.express as px

with open("database/2024-11.csv", "r", encoding="utf-8") as file:
    csv_reader = csv.DictReader(file)
    data = list(csv_reader)


# Convert the list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(data)

# Convert 'time' and 'amount' columns to numeric types if necessary
df["time"] = pd.to_numeric(df["time"])
df["amount"] = pd.to_numeric(df["amount"])

# Create the line plot
fig = px.line(
    data,
    # df,
    x="time",
    y="amount",
    color="group",
    title="Line Plot of Amount over Time by Group",
)

# Show the plot
fig.show()
