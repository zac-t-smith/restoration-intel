# Create and export a simplified LSTM-ready notebook with explanations
from nbformat import v4 as nbf
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from datetime import datetime, timedelta
import seaborn as sns

# Define notebook cells
cells = []

# Title and introduction
cells.append(nbf.new_markdown_cell("# Restoration Risk Forecasting with LSTM\nThis notebook demonstrates how to use an LSTM neural network to forecast daily revenue and calculate deviation-based risk scores."))

# Imports
cells.append(nbf.new_code_cell("""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from datetime import datetime, timedelta
import seaborn as sns
"""))

# Simulate data
cells.append(nbf.new_code_cell("""
# Generate sample daily revenue for 180 days
np.random.seed(42)
days = 180
dates = [datetime.today() - timedelta(days=i) for i in range(days)][::-1]
daily_revenue = np.abs(np.random.normal(loc=5000, scale=1200, size=days))

df = pd.DataFrame({
    "date": dates,
    "daily_revenue": daily_revenue
})

df.head()
"""))

# Normalize and prepare data
cells.append(nbf.new_code_cell("""
scaler = MinMaxScaler()
df["scaled_revenue"] = scaler.fit_transform(df[["daily_revenue"]])

# Create sequences
sequence_length = 28
X, y = [], []
for i in range(sequence_length, len(df)):
    X.append(df["scaled_revenue"].iloc[i-sequence_length:i].values)
    y.append(df["scaled_revenue"].iloc[i])

X, y = np.array(X), np.array(y)
X = X.reshape((X.shape[0], X.shape[1], 1))
"""))

# Build and train LSTM
cells.append(nbf.new_code_cell("""
model = Sequential()
model.add(LSTM(50, return_sequences=False, input_shape=(sequence_length, 1)))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=15, batch_size=8, verbose=1)
"""))

# Predict and analyze
cells.append(nbf.new_code_cell("""
predicted = model.predict(X)
df = df.iloc[sequence_length:].copy()
df["predicted"] = scaler.inverse_transform(predicted)
df["actual"] = df["daily_revenue"].values
df["predicted_pct_change"] = df["predicted"].pct_change()
df["actual_pct_change"] = df["actual"].pct_change()
df["risk_score"] = abs(df["predicted_pct_change"] - df["actual_pct_change"])
df.head()
"""))

# Plot
cells.append(nbf.new_code_cell("""
plt.figure(figsize=(14,6))
plt.plot(df["date"], df["actual"], label="Actual", alpha=0.7)
plt.plot(df["date"], df["predicted"], label="Predicted", alpha=0.7)
plt.title("LSTM Forecast: Actual vs Predicted Revenue")
plt.xlabel("Date")
plt.ylabel("Revenue ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
"""))

# Create notebook
nb = nbf.new_notebook(cells=cells)
notebook_path = "/mnt/data/LSTM_Risk_Forecast_Notebook.ipynb"
with open(notebook_path, "w") as f:
    f.write(nbf.writes(nb))

notebook_path

# Re-run setup due to kernel reset
from nbformat import v4 as nbf

# Define notebook cells again
cells = []

# Title and introduction
cells.append(nbf.new_markdown_cell("# Restoration Risk Forecasting with LSTM\nThis notebook demonstrates how to use an LSTM neural network to forecast daily revenue and calculate deviation-based risk scores."))

# Imports
cells.append(nbf.new_code_cell("""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from datetime import datetime, timedelta
import seaborn as sns
"""))

# Simulate data
cells.append(nbf.new_code_cell("""
# Generate sample daily revenue for 180 days
np.random.seed(42)
days = 180
dates = [datetime.today() - timedelta(days=i) for i in range(days)][::-1]
daily_revenue = np.abs(np.random.normal(loc=5000, scale=1200, size=days))

df = pd.DataFrame({
    "date": dates,
    "daily_revenue": daily_revenue
})

df.head()
"""))

# Normalize and prepare data
cells.append(nbf.new_code_cell("""
scaler = MinMaxScaler()
df["scaled_revenue"] = scaler.fit_transform(df[["daily_revenue"]])

# Create sequences
sequence_length = 28
X, y = [], []
for i in range(sequence_length, len(df)):
    X.append(df["scaled_revenue"].iloc[i-sequence_length:i].values)
    y.append(df["scaled_revenue"].iloc[i])

X, y = np.array(X), np.array(y)
X = X.reshape((X.shape[0], X.shape[1], 1))
"""))

# Build and train LSTM
cells.append(nbf.new_code_cell("""
model = Sequential()
model.add(LSTM(50, return_sequences=False, input_shape=(sequence_length, 1)))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=15, batch_size=8, verbose=1)
"""))

# Predict and analyze
cells.append(nbf.new_code_cell("""
predicted = model.predict(X)
df = df.iloc[sequence_length:].copy()
df["predicted"] = scaler.inverse_transform(predicted)
df["actual"] = df["daily_revenue"].values
df["predicted_pct_change"] = df["predicted"].pct_change()
df["actual_pct_change"] = df["actual"].pct_change()
df["risk_score"] = abs(df["predicted_pct_change"] - df["actual_pct_change"])
df.head()
"""))

# Plot
cells.append(nbf.new_code_cell("""
plt.figure(figsize=(14,6))
plt.plot(df["date"], df["actual"], label="Actual", alpha=0.7)
plt.plot(df["date"], df["predicted"], label="Predicted", alpha=0.7)
plt.title("LSTM Forecast: Actual vs Predicted Revenue")
plt.xlabel("Date")
plt.ylabel("Revenue ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
"""))

# Save the notebook
nb = nbf.new_notebook(cells=cells)
notebook_path = "/mnt/data/LSTM_Risk_Forecast_Notebook.ipynb"
with open(notebook_path, "w") as f:
    f.write(nbf.writes(nb))

notebook_path

class RestorationRiskModel:
    def __init__(self, seed=42):
        """
        Initialize the Restoration Risk Forecasting Model
        """
        np.random.seed(seed)
        self.generate_synthetic_data()
    
    def generate_synthetic_data(self, days=365):
        """
        Generate synthetic business data with complex interactions
        """
        # Date range
        dates = [datetime.today() - timedelta(days=i) for i in range(days)][::-1]
        
        # Revenue generation with seasonal and trend components
        base_revenue = 5000 + np.sin(np.linspace(0, 4*np.pi, days)) * 1000
        revenue_noise = np.random.normal(0, 500, days)
        daily_revenue = np.abs(base_revenue + revenue_noise)
        
        # Simulate multiple revenue sources
        source_weights = np.random.dirichlet(alpha=[2, 1, 1, 0.5], size=days)
        
        # Job complexity and rework
        job_complexity = np.random.exponential(scale=1.5, size=days)
        rework_rate = np.clip(job_complexity / 10, 0, 1)
        
        # Insurance carrier interactions
        carrier_relationship = np.cumsum(np.random.normal(0, 0.1, days))
        carrier_relationship = (carrier_relationship - carrier_relationship.min()) / (carrier_relationship.max() - carrier_relationship.min())
        
        # Market dynamics
        market_saturation = np.cumsum(np.random.normal(0, 0.05, days))
        market_saturation = (market_saturation - market_saturation.min()) / (market_saturation.max() - market_saturation.min())
        
        # Construct DataFrame
        self.df = pd.DataFrame({
            "date": dates,
            "daily_revenue": daily_revenue,
            "source_weights_1": source_weights[:, 0],
            "source_weights_2": source_weights[:, 1],
            "source_weights_3": source_weights[:, 2],
            "job_complexity": job_complexity,
            "rework_rate": rework_rate,
            "carrier_relationship": carrier_relationship,
            "market_saturation": market_saturation
        })
    
    def calculate_rvami(self, window=30):
        """
        Restoration Volatility-Adjusted Momentum Index
        """
        revenue_growth = self.df["daily_revenue"].pct_change(window)
        revenue_std = self.df["daily_revenue"].rolling(window=window).std()
        
        rvami = (revenue_growth - 0.02) / revenue_std
        self.df["rvami"] = rvami.fillna(0)
        return rvami
    
    def calculate_cees(self):
        """
        Customer Ecosystem Entropy Score
        """
        source_columns = ["source_weights_1", "source_weights_2", "source_weights_3"]
        cees = -np.sum(self.df[source_columns] * np.log(self.df[source_columns] + 1e-10), axis=1) / np.log(len(source_columns))
        self.df["cees"] = cees
        return cees
    
    def calculate_ofc(self):
        """
        Operational Friction Coefficient
        """
        job_time_baseline = self.df["job_complexity"].quantile(0.1)
        ofc = (self.df["job_complexity"] / job_time_baseline) * (self.df["rework_rate"] + 1)
        self.df["ofc"] = ofc
        return ofc
    
    def calculate_icrdi(self, window=60):
        """
        Insurance Carrier Relationship Decay Index
        """
        icrdi = 1 - self.df["carrier_relationship"].rolling(window=window).mean()
        self.df["icrdi"] = icrdi.fillna(1)
        return icrdi
    
    def calculate_msmi(self, window=45):
        """
        Market Saturation Momentum Indicator
        """
        msmi = self.df["market_saturation"].pct_change(window)
        self.df["msmi"] = msmi.fillna(0)
        return msmi
    
    def calculate_cbhi(self):
        """
        Composite Business Health Index
        """
        # Normalize and weight components
        scaler = MinMaxScaler()
        metrics = [
            scaler.fit_transform(self.df[["rvami"]]),
            scaler.fit_transform(self.df[["cees"]]),
            scaler.fit_transform(self.df[["ofc"]]),
            scaler.fit_transform(self.df[["icrdi"]]),
            scaler.fit_transform(self.df[["msmi"]])
        ]
        
        # Weights can be adjusted based on domain expertise
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        
        cbhi = np.zeros_like(metrics[0])
        for metric, weight in zip(metrics, weights):
            cbhi += metric * weight
        
        self.df["cbhi"] = cbhi
        return cbhi
    
    def visualize_risk_metrics(self):
        """
        Create comprehensive visualization of risk metrics
        """
        plt.figure(figsize=(15, 10))
        
        # Daily Revenue
        plt.subplot(3, 2, 1)
        plt.plot(self.df['date'], self.df['daily_revenue'])
        plt.title('Daily Revenue')
        plt.xticks(rotation=45)
        
        # CBHI
        plt.subplot(3, 2, 2)
        plt.plot(self.df['date'], self.df['cbhi'], color='red')
        plt.title('Composite Business Health Index')
        plt.xticks(rotation=45)
        
        # Individual Metrics
        metrics = ['rvami', 'cees', 'ofc', 'icrdi', 'msmi']
        for i, metric in enumerate(metrics, 3):
            plt.subplot(3, 2, i)
            plt.plot(self.df['date'], self.df[metric])
            plt.title(metric.upper())
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()

# Main execution
if __name__ == "__main__":
    print("Starting Restoration Risk Model Simulation...")
    
    # Create and run the model
    model = RestorationRiskModel()
    
    print("Calculating Metrics...")
    # Calculate metrics
    rvami = model.calculate_rvami()
    cees = model.calculate_cees()
    ofc = model.calculate_ofc()
    icrdi = model.calculate_icrdi()
    msmi = model.calculate_msmi()
    cbhi = model.calculate_cbhi()
    
    print("RVAMI Summary:")
    print(rvami.describe())
    
    print("CEES Summary:")
    print(cees.describe())
    
    print("OFC Summary:")
    print(ofc.describe())
    
    print("ICRDI Summary:")
    print(icrdi.describe())
    
    print("MSMI Summary:")
    print(msmi.describe())
    
    print("CBHI Summary:")
    print(cbhi.describe())
    
    print("Visualizing Risk Metrics...")
    # Visualize results
    model.visualize_risk_metrics()
    
    print("Saving Results...")
    # Optional: Save model and results
    model.df.to_csv('restoration_risk_simulation.csv', index=False)
    
    print("Simulation Complete!")

