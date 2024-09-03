import json
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

#for lstm
# Function to extract features from JSON data
def extract_features_from_json(json_file):
    with open(json_file) as file:
        data = json.load(file)

    features = []
    for detector in data[0]['results']['detectors']:
        for element in detector['elements']:
            feature = {
                'type': element.get('type', ''),
                'name': element.get('name', ''),
                'description': detector.get('description', ''),
                'check': detector.get('check', ''),
                'impact': detector.get('impact', ''),
                'confidence': detector.get('confidence', '')
            }
            features.append(feature)
    
    df = pd.DataFrame(features)
    print(df.head(20))
    return df

# Load and preprocess new Solidity code features
new_json_file = 'C:/Users/stanl/Desktop/praccc/slither_test.json'
df_new = extract_features_from_json(new_json_file)

# Load the trained preprocessor and scaler
preprocessor = joblib.load("preprocessor2.pkl")
scaler = joblib.load("scaler2.pkl")

# Encode categorical features and scale the data
X_new = preprocessor.transform(df_new)
X_new = scaler.transform(X_new)

# Reshape the data for LSTM [samples, time steps, features]
# Assuming each sample is independent and time steps = 1
X_new = X_new.toarray().reshape((X_new.shape[0], 1, X_new.shape[1]))

# Load the trained model
model = load_model("smart_contract_lstm_model2.h5")

# Predict vulnerabilities
predictions = (model.predict(X_new) > 0.5).astype("int32")

# Print predictions
print(predictions)

# For better understanding, map predictions back to the original JSON data
for i, prediction in enumerate(predictions):
    print(f"Feature set {i}: Vulnerability {'Detected' if prediction == 1 else 'Not Detected'}")
