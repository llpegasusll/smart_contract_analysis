import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report
import joblib

#for LSTM
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
    return df

# Load and preprocess the data
json_file = 'slither_data.json'
df = extract_features_from_json(json_file)

# Add labels (assuming you have a way to assign labels)
# Here we randomly assign 0 or 1 for demonstration purposes
df['label'] = np.random.randint(2, size=len(df))

# Define the column transformer with OneHotEncoder for categorical features
categorical_features = ['type', 'name', 'description', 'check', 'impact', 'confidence']
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Split the data into training and testing sets
X = df.drop(columns=['label'])
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit and transform the training data, transform the test data
X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)

# Standardize the features
scaler = StandardScaler(with_mean=False)  # Setting with_mean=False to handle sparse matrices
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Reshape the data for LSTM [samples, time steps, features]
# Assuming each sample is independent and time steps = 1
X_train = X_train.toarray().reshape((X_train.shape[0], 1, X_train.shape[1]))
X_test = X_test.toarray().reshape((X_test.shape[0], 1, X_test.shape[1]))

# Define the LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Define early stopping to prevent overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Train the model
history = model.fit(X_train, y_train, validation_split=0.2, epochs=100, batch_size=32, callbacks=[early_stopping])

# Evaluate the model
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print(classification_report(y_test, y_pred))

# Save the trained model, preprocessor, and scaler
model.save("smart_contract_lstm_model2.h5")
joblib.dump(preprocessor, "preprocessor2.pkl")
joblib.dump(scaler, "scaler2.pkl")
