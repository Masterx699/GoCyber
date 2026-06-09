import os
import sys
import joblib
import pandas as pd

# Mock the missing class due to sklearn version differences
try:
    import sklearn.compose._column_transformer
    class DummyRemainder:
        def __init__(self, *args, **kwargs):
            pass
    sklearn.compose._column_transformer._RemainderColsList = DummyRemainder
    print("Mock applied.")
except Exception as e:
    print("Failed to apply mock:", e)

model_path = os.path.join(os.path.dirname(__file__), "Preprocessing_ml", "RF_Model.joblib")
print(f"Loading model from: {model_path}")

try:
    model_data = joblib.load(model_path)
    pipeline = model_data['pipeline']
    accuracy = model_data['accuracy']
    print(f"Model loaded. Training Accuracy: {accuracy*100:.2f}%")
    
    # Test data frame matching the model's expected features:
    # numeric: login_attempts, failed_logins, session_duration, network_packet_size, ip_reputation_score
    # categorical: encryption_used, browser_type, protocol_type
    test_input = pd.DataFrame([{
        'encryption_used': 'AES',
        'browser_type': 'Chrome',
        'protocol_type': 'TCP',
        'login_attempts': 2,
        'failed_logins': 1,
        'session_duration': 120.0,
        'network_packet_size': 512,
        'ip_reputation_score': 0.8
    }])
    
    probs = pipeline.predict_proba(test_input)[0]
    pred_label = probs.argmax()
    
    attack_mapping = {
        0: "Brute force",
        1: "Malware",
        2: "Normal",
        3: "Suspicious"
    }
    
    print("\nPrediction Success!")
    print(f"Predicted Attack: {attack_mapping.get(pred_label, 'Unknown')} ({probs[pred_label]*100:.2f}%)")
    print("\nProbabilities:")
    for idx, name in attack_mapping.items():
        print(f"  {name}: {probs[idx]*100:.2f}%")
        
except Exception as e:
    print(f"Error during validation: {e}")
    sys.exit(1)
