import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("database/2024-10.csv")

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x="time", y="amount", hue="group")

plt.show()
