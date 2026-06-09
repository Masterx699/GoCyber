import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_ml.settings')
try:
    django.setup()
    print("Django setup successful.")
except Exception as e:
    print("Django setup failed:", e)
    sys.exit(1)

from dashboard.views import predict

# Create mock request factory
factory = RequestFactory()
request = factory.post('/predict/', {
    'encryption_used': 'AES',
    'browser_type': 'Chrome',
    'protocol_type': 'TCP',
    'login_attempts': '5',
    'failed_logins': '2',
    'session_duration': '300.5',
    'network_packet_size': '1024',
    'ip_reputation_score': '0.9'
})

# Mock session middleware for authentication
middleware = SessionMiddleware(lambda req: None)
middleware.process_request(request)
request.session['is_auth'] = True

try:
    # Run the predict view
    print("Running predict view with mock request...")
    response = predict(request)
    print("Response Status Code:", response.status_code)
    
    html = response.content.decode('utf-8')
    if "ANALYSIS REPORT" in html:
        print("Test Result: SUCCESS - Found ANALYSIS REPORT in HTML output!")
        # Print lines around the predicted result
        lines = html.split('\n')
        for idx, line in enumerate(lines):
            if "PREDICTED ATTACK:" in line or "result-value" in line:
                print(f"L{idx}: {line.strip()}")
            if "Confidence:" in line or "Model Accuracy:" in line:
                print(f"L{idx}: {line.strip()}")
    else:
        print("Test Result: FAILED - Response HTML does not contain prediction report.")
        print(html[:1000])
except Exception as e:
    print("Error during view execution:", e)
    sys.exit(1)
