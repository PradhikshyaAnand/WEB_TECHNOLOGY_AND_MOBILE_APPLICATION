import pickle
from train_model import model

# Replace 'model' with the variable name of your trained model
# For example, if you did `model = RandomForestClassifier(...)` in your train_model.py
with open('water_quality_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model saved successfully!")