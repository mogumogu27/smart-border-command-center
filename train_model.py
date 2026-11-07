import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import m2cgen as m2c

# 1. Generate Synthetic Data
np.random.seed(42)
num_records = 1500
zones = np.random.choice(['A', 'B', 'C'], size=num_records)
hours = np.random.randint(0, 24, size=num_records)
temperatures = np.random.normal(25, 5, size=num_records)

motion_counts, threat_levels = [], []

for zone, hour in zip(zones, hours):
    motion = np.random.randint(0, 20)
    threat = 'Low'
    if zone == 'C' and (hour < 5 or hour > 22):
        motion += np.random.randint(20, 40)
        threat = 'High' if motion > 35 else 'Medium'
    elif zone == 'A' and motion > 15:
        threat = 'High' if motion > 25 else 'Medium'
            
    motion_counts.append(motion)
    threat_levels.append(threat)

data = pd.DataFrame({'Zone': zones, 'Hour': hours, 'Temperature': temperatures, 'Motion_Count': motion_counts, 'Threat_Level': threat_levels})
data.to_csv('historical_border_data.csv', index=False)

# 2. Train the Model
X = pd.get_dummies(data[['Zone', 'Hour', 'Temperature', 'Motion_Count']])
expected_columns = ['Hour', 'Temperature', 'Motion_Count', 'Zone_A', 'Zone_B', 'Zone_C']
X = X.reindex(columns=expected_columns, fill_value=0)
y = data['Threat_Level']

# Use a Decision Tree so it translates cleanly to pure Python
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X, y)

# 3. Translate the Model to Pure Python Code
model_code = m2c.export_to_python(model)

# Save the translated code as a new Python file
with open('model_logic.py', 'w') as f:
    f.write(model_code)

print("✅ Model compiled successfully into model_logic.py!")