# Restoration Business Forecasting & Risk Pipeline
# Section 1: Imports & Data Simulation
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy, zscore
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error, f1_score, roc_auc_score, precision_score
from datetime import datetime, timedelta
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Section 1: Data Simulation
np.random.seed(42)
days = 365 * 10  # 10 years of data
dates = [datetime.today() - timedelta(days=i) for i in range(days)][::-1]

# Simulate revenue with seasonality, trend, and noise
base_revenue = 5000 + np.sin(np.linspace(0, 8*np.pi, days)) * 1000
trend = np.linspace(0, 2000, days)
revenue_noise = np.random.normal(0, 500, days)
daily_revenue = np.abs(base_revenue + trend + revenue_noise)

# Simulate revenue sources
source_weights = np.random.dirichlet(alpha=[2, 1, 1, 0.5], size=days)

# Job complexity, rework, utilization
job_complexity = np.random.exponential(scale=1.5, size=days)
rework_rate = np.clip(job_complexity / 10, 0, 1)
utilization_rate = np.clip(np.random.normal(0.85, 0.08, days), 0.5, 1.0)

# Insurance carrier relationship
carrier_relationship = np.cumsum(np.random.normal(0, 0.1, days))
carrier_relationship = (carrier_relationship - carrier_relationship.min()) / (carrier_relationship.max() - carrier_relationship.min())

# Market saturation
market_saturation = np.cumsum(np.random.normal(0, 0.05, days))
market_saturation = (market_saturation - market_saturation.min()) / (market_saturation.max() - market_saturation.min())

# Seasonality flag (e.g., hurricane season: days 150-210 and 515-575)
hurricane_season = np.zeros(days)
hurricane_season[150:210] = 1
hurricane_season[515:575] = 1

# DataFrame
raw_df = pd.DataFrame({
    "date": dates,
    "daily_revenue": daily_revenue,
    "source_weights_1": source_weights[:, 0],
    "source_weights_2": source_weights[:, 1],
    "source_weights_3": source_weights[:, 2],
    "job_complexity": job_complexity,
    "rework_rate": rework_rate,
    "utilization_rate": utilization_rate,
    "carrier_relationship": carrier_relationship,
    "market_saturation": market_saturation,
    "hurricane_season": hurricane_season
})

# Section 2: Metric Refactoring & Preprocessing
# --- RVAMI ---
window_rvami = 30
revenue_growth = raw_df["daily_revenue"].pct_change(window_rvami)
revenue_std = raw_df["daily_revenue"].rolling(window=window_rvami).std()
rvami_raw = (revenue_growth - 0.02) / revenue_std
rvami_scaled = rvami_raw * 1000  # Scale for interpretability
rvami_scaled = np.clip(rvami_scaled, -10, 10)  # Cap outliers
raw_df["rvami"] = MinMaxScaler().fit_transform(rvami_scaled.fillna(0).values.reshape(-1, 1))

# --- CEES ---
source_cols = ["source_weights_1", "source_weights_2", "source_weights_3"]
cees = -np.sum(raw_df[source_cols] * np.log(raw_df[source_cols] + 1e-10), axis=1) / np.log(len(source_cols))
raw_df["cees"] = MinMaxScaler().fit_transform(cees.values.reshape(-1, 1))

# --- OFC ---
ofc_raw = (raw_df["job_complexity"] / raw_df["job_complexity"].quantile(0.1)) * (raw_df["rework_rate"] + 1)
ofc_log = np.log1p(ofc_raw)
ofc_capped = np.clip(ofc_log, 0, np.percentile(ofc_log, 95))
raw_df["ofc"] = MinMaxScaler().fit_transform(ofc_capped.values.reshape(-1, 1))

# --- ICRDI ---
icrdi_raw = 1 - raw_df["carrier_relationship"].rolling(window=60).mean()
icrdi_filled = icrdi_raw.fillna(1)
raw_df["icrdi"] = MinMaxScaler().fit_transform(icrdi_filled.values.reshape(-1, 1))

# --- MSMI ---
msmi_raw = raw_df["market_saturation"].pct_change(45)
msmi_tanh = np.tanh(msmi_raw / 2)  # Stabilize with tanh
msmi_filled = msmi_tanh.fillna(0)
raw_df["msmi"] = MinMaxScaler().fit_transform(msmi_filled.values.reshape(-1, 1))

# --- CBHI ---
cbhi_weights = [0.3, 0.2, 0.2, 0.15, 0.15]
cbhi = (
    cbhi_weights[0] * raw_df["rvami"] +
    cbhi_weights[1] * raw_df["cees"] +
    cbhi_weights[2] * raw_df["ofc"] +
    cbhi_weights[3] * raw_df["icrdi"] +
    cbhi_weights[4] * raw_df["msmi"]
)
raw_df["cbhi"] = cbhi

# Print summaries
print("CBHI Summary:")
print(raw_df["cbhi"].describe())
print("\nRVAMI Summary:")
print(raw_df["rvami"].describe())
print("\nOFC Summary:")
print(raw_df["ofc"].describe())
print("\nMSMI Summary:")
print(raw_df["msmi"].describe())

# Section 3: Feature Engineering (Rolling Windows, Ratios, Lags, Flags)
# Rolling means and stds for revenue, CBHI, and utilization
for window in [7, 14, 21, 28, 60, 90]:
    raw_df[f'rev_{window}d_avg'] = raw_df['daily_revenue'].rolling(window).mean().bfill()
    raw_df[f'rev_{window}d_std'] = raw_df['daily_revenue'].rolling(window).std().bfill()
    raw_df[f'cbhi_{window}d_avg'] = raw_df['cbhi'].rolling(window).mean().bfill()
    raw_df[f'cbhi_{window}d_std'] = raw_df['cbhi'].rolling(window).std().bfill()
    raw_df[f'util_{window}d_avg'] = raw_df['utilization_rate'].rolling(window).mean().bfill()

# Ratios: 7d/21d and 14d/28d revenue momentum
raw_df['rev_7d_21d_ratio'] = raw_df['rev_7d_avg'] / (raw_df['rev_21d_avg'] + 1e-6)
raw_df['rev_14d_28d_ratio'] = raw_df['rev_14d_avg'] / (raw_df['rev_28d_avg'] + 1e-6)

# Rolling z-score for revenue (28d)
rev_28d_mean = raw_df['daily_revenue'].rolling(28).mean().bfill()
rev_28d_std = raw_df['daily_revenue'].rolling(28).std().bfill()
raw_df['rev_28d_z'] = (raw_df['daily_revenue'] - rev_28d_mean) / (rev_28d_std + 1e-6)

# Lagged features (previous day's CBHI, RVAMI, OFC)
raw_df['cbhi_lag1'] = raw_df['cbhi'].shift(1).bfill()
raw_df['rvami_lag1'] = raw_df['rvami'].shift(1).bfill()
raw_df['ofc_lag1'] = raw_df['ofc'].shift(1).bfill()

# Seasonality flags are already present (hurricane_season)

# Print a sample of engineered features
print('\nFeature Engineering Sample:')
print(raw_df[[
    'date', 'daily_revenue', 'cbhi', 'rev_7d_avg', 'rev_21d_avg', 'rev_7d_21d_ratio',
    'rev_28d_z', 'cbhi_lag1', 'rvami_lag1', 'ofc_lag1', 'hurricane_season'
]].head(10))

# Section 5: Prophet, XGBoost, and Baseline Models for CBHI Forecasting
from prophet import Prophet
from xgboost import XGBRegressor, XGBClassifier
from sklearn.linear_model import LinearRegression

# --- Prophet Forecast (CBHI) ---
prophet_df = raw_df[['date', 'cbhi']].rename(columns={'date': 'ds', 'cbhi': 'y'}).copy()
prophet_train = prophet_df.iloc[:-365]  # Last year as test
prophet_test = prophet_df.iloc[-365:]

prophet_model = Prophet(yearly_seasonality=True, daily_seasonality=False)
prophet_model.fit(prophet_train)
future = prophet_model.make_future_dataframe(periods=365)
forecast = prophet_model.predict(future)
prophet_pred = forecast['yhat'].iloc[-365:].values
prophet_mae = mean_absolute_error(prophet_test['y'], prophet_pred)
prophet_mape = mean_absolute_percentage_error(prophet_test['y'], prophet_pred)
print(f'Prophet MAE: {prophet_mae:.4f}, MAPE: {prophet_mape:.4f}')

# --- XGBoost Regression (CBHI) ---
# Use last 365 days as test, rest as train
xgb_features = ['rvami', 'cees', 'ofc', 'icrdi', 'msmi',
                'rev_7d_avg', 'rev_21d_avg', 'rev_7d_21d_ratio',
                'rev_28d_z', 'cbhi_lag1', 'rvami_lag1', 'ofc_lag1', 'hurricane_season']
xgb_train = raw_df.iloc[:-365]
xgb_test = raw_df.iloc[-365:]
X_xgb_train = xgb_train[xgb_features].values
X_xgb_test = xgb_test[xgb_features].values
y_xgb_train = xgb_train['cbhi'].values
y_xgb_test = xgb_test['cbhi'].values

xgb_reg = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
xgb_reg.fit(X_xgb_train, y_xgb_train)
xgb_pred = xgb_reg.predict(X_xgb_test)
xgb_mae = mean_absolute_error(y_xgb_test, xgb_pred)
xgb_mape = mean_absolute_percentage_error(y_xgb_test, xgb_pred)
print(f'XGBoost MAE: {xgb_mae:.4f}, MAPE: {xgb_mape:.4f}')

# --- Linear Regression Baseline ---
linreg = LinearRegression()
linreg.fit(X_xgb_train, y_xgb_train)
linreg_pred = linreg.predict(X_xgb_test)
linreg_mae = mean_absolute_error(y_xgb_test, linreg_pred)
linreg_mape = mean_absolute_percentage_error(y_xgb_test, linreg_pred)
print(f'Linear Regression MAE: {linreg_mae:.4f}, MAPE: {linreg_mape:.4f}')

# --- Consensus Ensemble (Simple Average) ---
ensemble_pred = (prophet_pred + xgb_pred + linreg_pred) / 3
ensemble_mae = mean_absolute_error(y_xgb_test, ensemble_pred)
ensemble_mape = mean_absolute_percentage_error(y_xgb_test, ensemble_pred)
print(f'Ensemble MAE: {ensemble_mae:.4f}, MAPE: {ensemble_mape:.4f}')

# --- Leaderboard ---
print("\nModel Leaderboard (MAE, MAPE):")
print(f"Prophet: {prophet_mae:.4f}, {prophet_mape:.4f}")
print(f"XGBoost: {xgb_mae:.4f}, {xgb_mape:.4f}")
print(f"Linear Regression: {linreg_mae:.4f}, {linreg_mape:.4f}")
print(f"Ensemble: {ensemble_mae:.4f}, {ensemble_mape:.4f}")

# --- Visualization ---
plt.style.use('dark_background')
plt.figure(figsize=(18, 7))

# Use the same test set as before
cbhi_actual = y_xgb_test
cbhi_prophet = prophet_pred
cbhi_xgb = xgb_pred
cbhi_linreg = linreg_pred
cbhi_ensemble = ensemble_pred
rvami_test = xgb_test['rvami'].reset_index(drop=True)
dates_test = xgb_test['date'].reset_index(drop=True)

# Plot actual and ensemble
plt.plot(dates_test, cbhi_actual, label='Actual CBHI', color='#00BFFF', lw=2, alpha=0.8)
plt.plot(dates_test, cbhi_ensemble, label='Ensemble', color='#FFD700', lw=2, linestyle='--', alpha=0.9)
plt.plot(dates_test, cbhi_prophet, label='Prophet', color='#00FF7F', lw=1, alpha=0.7)
plt.plot(dates_test, cbhi_xgb, label='XGBoost', color='#FF8C00', lw=1, alpha=0.7)
plt.plot(dates_test, cbhi_linreg, label='Linear Regression', color='#B0C4DE', lw=1, alpha=0.7)

# Risk overlays
plt.fill_between(dates_test, 0, 0.25, color='#FF1744', alpha=0.18, label='CBHI < 0.25 (Red Zone)')
plt.fill_between(dates_test, 0.25, 0.5, color='#FFD600', alpha=0.10, label='CBHI 0.25-0.5 (Caution)')
plt.fill_between(dates_test, 0.5, 1, color='#00E676', alpha=0.07, label='CBHI > 0.5 (Healthy)')

# Overlay RVAMI as color
import matplotlib.colors as mcolors
norm = mcolors.Normalize(vmin=0, vmax=1)
plt.scatter(dates_test, cbhi_actual, c=rvami_test, cmap='cool', s=12, label='RVAMI (color)', alpha=0.7, edgecolor='none')

plt.axhline(0.25, color='#FF1744', linestyle='--', lw=1)
plt.axhline(0.5, color='#FFD600', linestyle='--', lw=1)
plt.title('CBHI Forecast & Risk Zones (Dark Theme)', fontsize=18, color='w')
plt.xlabel('Date', fontsize=14, color='w')
plt.ylabel('CBHI', fontsize=14, color='w')
plt.legend(facecolor='#222', framealpha=0.8, fontsize=12)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()

# --- CBHI Robustness & Alternative Transformations ---
from scipy.stats import zscore
from sklearn.model_selection import GridSearchCV

# Rolling z-score for each KPI (window=90)
def rolling_z(series, window=90):
    return (series - series.rolling(window).mean()) / (series.rolling(window).std() + 1e-6)

# Apply alternative transformations
def transform_kpis(df):
    df = df.copy()
    # RVAMI: rolling z-score and tanh
    df['rvami_z'] = rolling_z(df['rvami'], 90).bfill()
    df['rvami_tanh'] = np.tanh(df['rvami_z'])
    # OFC: tanh
    df['ofc_tanh'] = np.tanh(df['ofc'])
    # MSMI: tanh
    df['msmi_tanh'] = np.tanh(df['msmi'])
    # Momentum ratios
    df['rev_21d_28d_ratio'] = df['rev_21d_avg'] / (df['rev_28d_avg'] + 1e-6)
    df['rev_21d_28d_z'] = zscore(df['rev_21d_28d_ratio'].fillna(0))
    return df

raw_df = transform_kpis(raw_df)

# Function to auto-optimize CBHI weights for best XGBoost predictive power
def optimize_cbhi_weights(df, features, target='cbhi', n_iter=20):
    from sklearn.metrics import mean_absolute_error
    best_mae = float('inf')
    best_weights = None
    best_cbhi = None
    np.random.seed(42)
    for _ in range(n_iter):
        # Random weights (sum to 1)
        w = np.random.dirichlet(np.ones(len(features)))
        cbhi = sum(w[i] * df[features[i]] for i in range(len(features)))
        # XGBoost regression
        train, test = cbhi[:-365], cbhi[-365:]
        y_train, y_test = df[target][:-365], df[target][-365:]
        xgb = XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
        xgb.fit(train.values.reshape(-1, 1), y_train)
        pred = xgb.predict(test.values.reshape(-1, 1))
        mae = mean_absolute_error(y_test, pred)
        if mae < best_mae:
            best_mae = mae
            best_weights = w
            best_cbhi = cbhi
    print(f'Best CBHI Weights: {dict(zip(features, best_weights))}')
    print(f'Best XGBoost MAE with optimized CBHI: {best_mae:.4f}')
    return best_cbhi, best_weights

# Try alternative CBHI formulas
test_features = ['rvami_tanh', 'cees', 'ofc_tanh', 'icrdi', 'msmi_tanh', 'rev_21d_28d_z']
cbhi_opt, cbhi_weights = optimize_cbhi_weights(raw_df, test_features, target='cbhi', n_iter=30)
raw_df['cbhi_opt'] = cbhi_opt

# --- Financial Impact by Risk Zone ---
def financial_impact_by_risk_zone(df, cbhi_col='cbhi_opt', revenue_col='daily_revenue'):
    bins = [0, 0.3, 0.5, 1.01]
    labels = ['Red (<0.3)', 'Yellow (0.3-0.5)', 'Green (>0.5)']
    df = df.copy()
    df['risk_zone'] = pd.cut(df[cbhi_col], bins=bins, labels=labels, right=False)
    summary = df.groupby('risk_zone')[revenue_col].agg(['count', 'sum', 'mean'])
    summary['pct_of_total'] = 100 * summary['sum'] / df[revenue_col].sum()
    print('\nRevenue at Risk by CBHI Zone:')
    print(summary)
    return summary

financial_impact_by_risk_zone(raw_df, cbhi_col='cbhi_opt')

# --- Cowen-style Dual-Axis Chart (log(revenue) + CBHI overlays) ---
plt.style.use('dark_background')
fig, ax1 = plt.subplots(figsize=(18, 7))

# Log revenue (left y-axis)
log_revenue = np.log10(raw_df['daily_revenue'].iloc[-365:] + 1)
ax1.plot(raw_df['date'].iloc[-365:], log_revenue, color='#00BFFF', label='Log(Revenue)', lw=2)
ax1.set_ylabel('Log(Revenue)', color='#00BFFF', fontsize=14)
ax1.tick_params(axis='y', labelcolor='#00BFFF')

# CBHI (right y-axis)
ax2 = ax1.twinx()
cbhi_plot = raw_df['cbhi_opt'].iloc[-365:]
ax2.plot(raw_df['date'].iloc[-365:], cbhi_plot, color='#FFD700', label='CBHI (Opt)', lw=2)
ax2.set_ylabel('CBHI (0-1)', color='#FFD700', fontsize=14)
ax2.tick_params(axis='y', labelcolor='#FFD700')

# Risk overlays
ax2.fill_between(raw_df['date'].iloc[-365:], 0, 0.3, color='#FF1744', alpha=0.18)
ax2.fill_between(raw_df['date'].iloc[-365:], 0.3, 0.5, color='#FFD600', alpha=0.10)
ax2.fill_between(raw_df['date'].iloc[-365:], 0.5, 1, color='#00E676', alpha=0.07)
ax2.axhline(0.3, color='#FF1744', linestyle='--', lw=1)
ax2.axhline(0.5, color='#FFD600', linestyle='--', lw=1)

# Color-coded dots for revenue by CBHI
sc = ax2.scatter(raw_df['date'].iloc[-365:], cbhi_plot, c=log_revenue, cmap='cool', s=18, label='Log(Revenue)', alpha=0.7, edgecolor='none')
cbar = plt.colorbar(sc, ax=ax2, pad=0.02)
cbar.set_label('Log(Revenue)', color='w')

fig.suptitle('Cowen-style Restoration Risk Chart (Log Revenue + CBHI)', fontsize=18, color='w')
fig.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()

# --- SHAP Feature Importance for XGBoost ---
import shap
xgb_features = ['rvami', 'cees', 'ofc', 'icrdi', 'msmi',
                'rev_7d_avg', 'rev_21d_avg', 'rev_7d_21d_ratio',
                'rev_28d_z', 'cbhi_lag1', 'rvami_lag1', 'ofc_lag1', 'hurricane_season',
                'rvami_tanh', 'ofc_tanh', 'msmi_tanh', 'rev_21d_28d_z']
xgb_train = raw_df.iloc[:-365]
xgb_test = raw_df.iloc[-365:]
X_xgb_train = xgb_train[xgb_features].values
y_xgb_train = xgb_train['cbhi_opt'].values
xgb_reg = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
xgb_reg.fit(X_xgb_train, y_xgb_train)
explainer = shap.Explainer(xgb_reg, X_xgb_train)
shap_values = explainer(X_xgb_train[:1000])  # Use a sample for speed
shap.summary_plot(shap_values, xgb_train[xgb_features].iloc[:1000], show=True)

# --- Scenario Simulation Function ---
def simulate_scenario(df, feature_changes, model, features):
    df_sim = df.copy()
    for feat, val in feature_changes.items():
        df_sim[feat] = val
    X_sim = df_sim[features].values
    cbhi_pred = model.predict(X_sim)
    print(f"Simulated mean CBHI: {np.mean(cbhi_pred):.4f}")
    return cbhi_pred

# Example: Simulate a hurricane season and OFC spike
simulate_scenario(
    xgb_test,
    feature_changes={'hurricane_season': 1, 'ofc': 1.0},
    model=xgb_reg,
    features=xgb_features
)

def risk_to_impact_table(df, cbhi_col='cbhi_opt', revenue_col='daily_revenue'):
    bins = [0, 0.3, 0.5, 1.01]
    labels = ['Red (<0.3)', 'Yellow (0.3-0.5)', 'Green (>0.5)']
    df = df.copy()
    df['risk_zone'] = pd.cut(df[cbhi_col], bins=bins, labels=labels, right=False)
    summary = df.groupby('risk_zone')[revenue_col].agg(['count', 'sum', 'mean'])
    summary['pct_of_total'] = 100 * summary['sum'] / df[revenue_col].sum()
    return summary

fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=np.log10(daily_revenue+1), name='Log(Revenue)', yaxis='y1'))
fig.add_trace(go.Scatter(x=dates, y=cbhi, name='CBHI', yaxis='y2', line=dict(color='white')))
fig.update_layout(
    yaxis=dict(title='Log(Revenue)', side='left'),
    yaxis2=dict(title='CBHI', side='right', overlaying='y', range=[0,1]),
    shapes=[
        dict(type='rect', xref='x', yref='y2', x0=dates[0], x1=dates[-1], y0=0, y1=0.3, fillcolor='red', opacity=0.1, line_width=0),
        dict(type='rect', xref='x', yref='y2', x0=dates[0], x1=dates[-1], y0=0.3, y1=0.5, fillcolor='yellow', opacity=0.1, line_width=0),
        dict(type='rect', xref='x', yref='y2', x0=dates[0], x1=dates[-1], y0=0.5, y1=1, fillcolor='green', opacity=0.1, line_width=0)
    ]
)
fig.show()

# --- Dynamic CBHI Weights Using Rolling SHAP Importances ---
def dynamic_cbhi_weights(df, features, window=90):
    """
    Compute dynamic CBHI weights using rolling SHAP importances from XGBoost.
    Returns a DataFrame of dynamic weights and a new CBHI series.
    """
    import shap
    weights_list = []
    cbhi_dyn = []
    for i in range(window, len(df)):
        X_window = df[features].iloc[i-window:i].values
        y_window = df['cbhi'].iloc[i-window:i].values
        xgb = XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
        xgb.fit(X_window, y_window)
        explainer = shap.Explainer(xgb, X_window)
        shap_vals = explainer(X_window)
        mean_abs_shap = np.abs(shap_vals.values).mean(axis=0)
        weights = mean_abs_shap / (mean_abs_shap.sum() + 1e-8)
        weights_list.append(weights)
        cbhi_dyn.append((weights * df[features].iloc[i].values).sum())
    # Pad the start with static weights
    weights_arr = np.array(weights_list)
    cbhi_dyn = [np.nan]*window + cbhi_dyn
    weights_df = pd.DataFrame(weights_arr, columns=features, index=df.index[window:])
    df['cbhi_dyn'] = cbhi_dyn
    return df, weights_df

# Add lagged features for all KPIs (7, 14, 21 days)
def add_lagged_features(df, kpi_cols, lags=[7, 14, 21]):
    for col in kpi_cols:
        for lag in lags:
            df[f'{col}_lag{lag}'] = df[col].shift(lag).bfill()
    return df

kpi_cols = ['rvami', 'cees', 'ofc', 'icrdi', 'msmi', 'cbhi']
raw_df = add_lagged_features(raw_df, kpi_cols)

# Compute dynamic CBHI weights and dynamic CBHI
shap_features = ['rvami', 'cees', 'ofc', 'icrdi', 'msmi']
raw_df, cbhi_weights_df = dynamic_cbhi_weights(raw_df, shap_features, window=90)

# --- Executive Summary Generator ---
def executive_summary(df, cbhi_col='cbhi_dyn', revenue_col='daily_revenue'):
    last = df.dropna(subset=[cbhi_col]).iloc[-1]
    zone = 'RED' if last[cbhi_col] < 0.3 else ('YELLOW' if last[cbhi_col] < 0.5 else 'GREEN')
    print(f"\nExecutive Risk Summary:")
    print(f"Current CBHI: {last[cbhi_col]:.3f} ({zone} zone)")
    print(f"Today's Revenue: ${last[revenue_col]:,.0f}")
    # Revenue at risk
    impact = financial_impact_by_risk_zone(df, cbhi_col=cbhi_col, revenue_col=revenue_col)
    print(f"\nRevenue at risk in RED zone: ${impact.loc['Red (<0.3)', 'sum']:,.0f}")
    print(f"% of total revenue in RED zone: {impact.loc['Red (<0.3)', 'pct_of_total']:.2f}%")
    print(f"Top dynamic CBHI weights (last 90d):")
    print(cbhi_weights_df.iloc[-1].sort_values(ascending=False))

executive_summary(raw_df, cbhi_col='cbhi_dyn', revenue_col='daily_revenue')

# --- Scenario Library for Business-Driven What-Ifs ---
scenario_library = [
    {'name': 'Hurricane Season', 'changes': {'hurricane_season': 1}},
    {'name': 'Carrier Delay Spike', 'changes': {'icrdi': 1.0}},
    {'name': 'OFC Surge', 'changes': {'ofc': 1.0}},
    {'name': 'Revenue Momentum Crash', 'changes': {'rvami': 0.0}},
    {'name': 'All Clear', 'changes': {'ofc': 0.0, 'rvami': 1.0, 'hurricane_season': 0}},
]

print("\nScenario Library Results:")
for scenario in scenario_library:
    print(f"\nScenario: {scenario['name']}")
    simulate_scenario(
        xgb_test,
        feature_changes=scenario['changes'],
        model=xgb_reg,
        features=xgb_features
    )

# --- Cowen-Style Dark Theme Plotly Chart with Cost of Risk Overlay ---
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Prepare data for last 10 years
df_plot = raw_df.copy()
df_plot = df_plot.sort_values('date')
df_plot['log_revenue'] = np.log10(df_plot['daily_revenue'] + 1)

# Cost of risk calculation
cost_per_day = np.where(df_plot['cbhi'] < 0.3, 600, np.where(df_plot['cbhi'] < 0.5, 250, 0))
df_plot['cost_of_risk'] = cost_per_day
# Cumulative cost of risk
df_plot['cum_cost_of_risk'] = np.cumsum(df_plot['cost_of_risk'])

# Color scale for risk (use rvami, 0-1)
color_risk = df_plot['rvami']

# Create figure with secondary y-axis for cost overlay
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Log-revenue line (left y-axis)
fig.add_trace(
    go.Scatter(
        x=df_plot['date'],
        y=df_plot['log_revenue'],
        name='Log(Revenue)',
        line=dict(color='#00BFFF', width=2),
        mode='lines',
        showlegend=True
    ),
    secondary_y=False
)

# CBHI line (right y-axis)
fig.add_trace(
    go.Scatter(
        x=df_plot['date'],
        y=df_plot['cbhi'],
        name='CBHI',
        line=dict(color='white', width=2),
        mode='lines',
        showlegend=True
    ),
    secondary_y=True
)

# Risk-colored dots (CBHI, colored by rvami)
fig.add_trace(
    go.Scatter(
        x=df_plot['date'],
        y=df_plot['cbhi'],
        mode='markers',
        marker=dict(
            size=6,
            color=color_risk,
            colorscale='RdYlBu_r',
            cmin=0,
            cmax=1,
            colorbar=dict(title='RVAMI', tickvals=[0, 0.5, 1], ticktext=['Low', 'Med', 'High'], len=0.3, y=0.8),
            line=dict(width=0)
        ),
        name='Risk (RVAMI)',
        showlegend=False
    ),
    secondary_y=True
)

# Cumulative cost of risk overlay (right y-axis)
fig.add_trace(
    go.Scatter(
        x=df_plot['date'],
        y=df_plot['cum_cost_of_risk'],
        name='Cumulative Cost of Risk',
        line=dict(color='#FF1744', width=2, dash='dot'),
        mode='lines',
        showlegend=True,
        yaxis='y3'
    ),
    secondary_y=True
)

# Add shaded risk bands (hrect)
fig.add_shape(type='rect', xref='x', yref='y2', x0=df_plot['date'].iloc[0], x1=df_plot['date'].iloc[-1], y0=0, y1=0.3, fillcolor='rgba(255,23,68,0.18)', line_width=0, layer='below')
fig.add_shape(type='rect', xref='x', yref='y2', x0=df_plot['date'].iloc[0], x1=df_plot['date'].iloc[-1], y0=0.3, y1=0.5, fillcolor='rgba(255,214,0,0.10)', line_width=0, layer='below')
fig.add_shape(type='rect', xref='x', yref='y2', x0=df_plot['date'].iloc[0], x1=df_plot['date'].iloc[-1], y0=0.5, y1=1, fillcolor='rgba(0,230,118,0.07)', line_width=0, layer='below')

# Layout
fig.update_layout(
    template='plotly_dark',
    title=dict(text='Restoration Risk Chart: Log Revenue, CBHI, and Cost of Risk', font=dict(size=22, color='white')),
    xaxis=dict(title='Date', showgrid=False),
    yaxis=dict(title='Log(Revenue)', showgrid=False, color='#00BFFF'),
    yaxis2=dict(title='CBHI (0-1)', range=[0,1], overlaying='y', side='right', color='white', showgrid=False),
    yaxis3=dict(title='Cumulative Cost of Risk ($)', anchor='free', overlaying='y', side='right', position=1.07, showgrid=False, color='#FF1744', showticklabels=True),
    legend=dict(bgcolor='rgba(0,0,0,0.7)', font=dict(color='white', size=13)),
    plot_bgcolor='#181A20',
    paper_bgcolor='#181A20',
    margin=dict(l=60, r=80, t=60, b=40)
)

# Export to PNG (optional)
# fig.write_image('restoration_risk_chart.png', scale=2)

fig.show() 