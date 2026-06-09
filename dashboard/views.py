from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
import json
import os
import joblib
import pandas as pd

# Mock the missing class due to sklearn version differences (1.6.1 vs 1.8.0)
try:
    import sklearn.compose._column_transformer
    class DummyRemainder:
        def __init__(self, *args, **kwargs):
            pass
    sklearn.compose._column_transformer._RemainderColsList = DummyRemainder
except Exception:
    pass

MODEL_PATH = settings.BASE_DIR / "Preprocessing_ml" / "RF_Model.joblib"
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def home(request):
    # Render tampilan terminal
    return render(request, 'dashboard/base.html')

def validasi_key(request):
    if request.method == 'POST':
        try:
            # Membaca data JSON yang dikirim oleh Javascript
            data = json.loads(request.body)
            input_key = data.get('key')
            
            if input_key == "admin123":
                # Jika benar, beri "tiket masuk" berupa session
                request.session['is_auth'] = True
                request.session.set_expiry(3600) # Berlaku 1 jam
                return JsonResponse({'status': 'success', 'message': 'Access Granted. Module Unlocked.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Access Denied: Invalid Security Key.'})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Bad Request'})
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def predict(request):
    # Jika belum auth, REDIRECT langsung ke halaman access_denied
    if not request.session.get('is_auth'):
        return redirect('access_denied')

    context = {}
    if request.method == 'POST':
        try:
            # Retrieve 8 parameters from form
            encryption_used = request.POST.get('encryption_used', 'None')
            browser_type = request.POST.get('browser_type', 'Unknown')
            protocol_type = request.POST.get('protocol_type', 'TCP')
            
            login_attempts = int(request.POST.get('login_attempts', 0))
            failed_logins = int(request.POST.get('failed_logins', 0))
            session_duration = float(request.POST.get('session_duration', 0.0))
            network_packet_size = int(request.POST.get('network_packet_size', 0))
            ip_reputation_score = float(request.POST.get('ip_reputation_score', 0.0))
            
            # Format inputs as DataFrame for the sklearn pipeline
            input_df = pd.DataFrame([{
                'encryption_used': encryption_used,
                'browser_type': browser_type,
                'protocol_type': protocol_type,
                'login_attempts': login_attempts,
                'failed_logins': failed_logins,
                'session_duration': session_duration,
                'network_packet_size': network_packet_size,
                'ip_reputation_score': ip_reputation_score
            }])
            
            # Load the Random Forest model pipeline
            model_data = get_model()
            pipeline = model_data['pipeline']
            accuracy = model_data.get('accuracy', 0.0)
            
            # Predict probabilities and get highest confidence class
            probs = pipeline.predict_proba(input_df)[0]
            pred_label = probs.argmax()
            
            attack_mapping = {
                0: "Brute force",
                1: "Malware",
                2: "Normal",
                3: "Suspicious"
            }
            
            hasil_prediksi = attack_mapping.get(pred_label, "Unknown")
            confidence = probs[pred_label] * 100
            
            # Detailed probability breakdowns for UI
            prob_breakdown = []
            for idx, label in attack_mapping.items():
                prob_breakdown.append({
                    'label': label,
                    'pct': f"{probs[idx] * 100:.2f}%"
                })
            
            context = {
                'status': 'SUCCESS',
                'hasil_prediksi': hasil_prediksi,
                'confidence': f"{confidence:.2f}%",
                'model_accuracy': f"{accuracy * 100:.2f}%",
                'prob_breakdown': prob_breakdown,
                'parameter_masuk': [
                    f"Encryption: {encryption_used}",
                    f"Browser: {browser_type}",
                    f"Protocol: {protocol_type}",
                    f"Login Attempts: {login_attempts}",
                    f"Failed Logins: {failed_logins}",
                    f"Session Duration: {session_duration}s",
                    f"Packet Size: {network_packet_size} bytes",
                    f"IP Reputation Score: {ip_reputation_score}"
                ]
            }
        except Exception as e:
            context = {
                'status': 'ERROR',
                'error_message': str(e)
            }
        
    return render(request, 'dashboard/predict.html', context)

# FUNGSI BARU: Render halaman penolakan
def access_denied(request):
    return render(request, 'dashboard/access_denied.html')