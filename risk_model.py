import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import seaborn as sns

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
        rvami = pd.Series(np.nan_to_num(rvami, nan=0.0, posinf=1.0, neginf=-1.0))
        self.df["rvami"] = rvami
        return rvami
    
    def calculate_cees(self):
        """
        Customer Ecosystem Entropy Score
        """
        source_columns = ["source_weights_1", "source_weights_2", "source_weights_3"]
        cees = -np.sum(self.df[source_columns] * np.log(self.df[source_columns] + 1e-10), axis=1) / np.log(len(source_columns))
        cees = pd.Series(np.nan_to_num(cees, nan=0.0, posinf=1.0, neginf=0.0))
        self.df["cees"] = cees
        return cees
    
    def calculate_ofc(self):
        """
        Operational Friction Coefficient
        """
        job_time_baseline = self.df["job_complexity"].quantile(0.1)
        ofc = (self.df["job_complexity"] / job_time_baseline) * (self.df["rework_rate"] + 1)
        ofc = pd.Series(np.nan_to_num(ofc, nan=0.0, posinf=1.0, neginf=0.0))
        self.df["ofc"] = ofc
        return ofc
    
    def calculate_icrdi(self, window=60):
        """
        Insurance Carrier Relationship Decay Index
        """
        icrdi = 1 - self.df["carrier_relationship"].rolling(window=window).mean()
        icrdi = pd.Series(np.nan_to_num(icrdi, nan=1.0, posinf=1.0, neginf=0.0))
        self.df["icrdi"] = icrdi
        return icrdi
    
    def calculate_msmi(self, window=45):
        """
        Market Saturation Momentum Indicator
        """
        msmi = self.df["market_saturation"].pct_change(window)
        msmi = pd.Series(np.nan_to_num(msmi, nan=0.0, posinf=1.0, neginf=-1.0))
        self.df["msmi"] = msmi
        return msmi
    
    def calculate_cbhi(self):
        """
        Composite Business Health Index
        """
        # Normalize and weight components
        scaler = MinMaxScaler()
        metrics = [
            scaler.fit_transform(np.abs(self.df[["rvami"]])),
            scaler.fit_transform(np.abs(self.df[["cees"]])),
            scaler.fit_transform(np.abs(self.df[["ofc"]])),
            scaler.fit_transform(np.abs(self.df[["icrdi"]])),
            scaler.fit_transform(np.abs(self.df[["msmi"]]))
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
        Print comprehensive risk metrics
        """
        print("\n--- Risk Metrics Visualization ---")
        
        # Daily Revenue Summary
        print("\nDaily Revenue Summary:")
        print(self.df['daily_revenue'].describe())
        
        # CBHI Summary
        print("\nComposite Business Health Index Summary:")
        print(self.df['cbhi'].describe())
        
        # Individual Metrics Summary
        metrics = ['rvami', 'cees', 'ofc', 'icrdi', 'msmi']
        for metric in metrics:
            print(f"\n{metric.upper()} Summary:")
            print(self.df[metric].describe())

# Main execution
if __name__ == "__main__":
    # Create and run the model
    model = RestorationRiskModel()
    
    # Calculate metrics
    rvami = model.calculate_rvami()
    cees = model.calculate_cees()
    ofc = model.calculate_ofc()
    icrdi = model.calculate_icrdi()
    msmi = model.calculate_msmi()
    cbhi = model.calculate_cbhi()
    
    # Print metric summaries
    print("RVAMI Summary:")
    print(rvami.describe())
    
    print("\nCEES Summary:")
    print(cees.describe())
    
    print("\nOFC Summary:")
    print(ofc.describe())
    
    print("\nICRDI Summary:")
    print(icrdi.describe())
    
    print("\nMSMI Summary:")
    print(msmi.describe())
    
    print("\nCBHI Summary:")
    print(pd.Series(cbhi.flatten()).describe())
    
    # Visualize results
    model.visualize_risk_metrics()
    
    # Save results
    model.df.to_csv('restoration_risk_simulation.csv', index=False) 