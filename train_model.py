import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

print("1. Loading road network data...")
df = pd.read_csv("ner_road_segments.csv")

# Ensure we have a consistent dataset size
print(f"Loaded {len(df)} road segments.")

# 2. Synthetic Feature Engineering (Simulating NER Terrain & Weather Realities)
np.random.seed(42)  # For reproducible results

# Simulate rainfall in mm (skewed distribution: mostly normal, heavy spikes)
df['rainfall_mm'] = np.random.exponential(scale=50, size=len(df))

# Simulate terrain slope in degrees (0 to 45 degrees, higher in mountain regions like Meghalaya/Arunachal)
df['slope_degrees'] = np.random.uniform(low=2.0, high=40.0, size=len(df))

# Simulate historical landslide/flood incidents count (0 to 5)
df['historical_incidents'] = np.random.poisson(lam=1.0, size=len(df))

# 3. Create Target Label (is_disrupted: 1 if high risk, 0 if safe)
# Logic: High rainfall + steep slopes + past incidents heavily increase disruption probability
risk_score = (
    (df['rainfall_mm'] > 100).astype(int) * 2 +
    (df['slope_degrees'] > 25).astype(int) * 2 +
    (df['historical_incidents'] >= 2).astype(int) * 1.5 +
    np.random.normal(0, 0.5, size=len(df))  # Add some noise
)

# Convert risk score to binary label (threshold > 3.0 means disrupted)
df['is_disrupted'] = (risk_score > 3.0).astype(int)

print(f"Disruption Class Distribution:\n{df['is_disrupted'].value_counts()}")

# 4. Prepare Features (X) and Target (y)
features = ['rainfall_mm', 'slope_degrees', 'historical_incidents']
X = df[features]
y = df['is_disrupted']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. Training Random Forest Disruption Prediction Model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Evaluate Model Performance
y_pred = model.predict(X_test)
print("\n--- Model Evaluation ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))