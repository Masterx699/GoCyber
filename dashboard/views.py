from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
import json
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
        param1 = request.POST.get('param1')
        param2 = request.POST.get('param2')
        param3 = request.POST.get('param3')
        param4 = request.POST.get('param4')
        param5 = request.POST.get('param5')
        
        context = {
            'status': 'SUCCESS',
            'hasil_prediksi': 'Anomali Terdeteksi: SYN Flood Attack',
            'parameter_masuk': [param1, param2, param3, param4, param5]
        }
        
    return render(request, 'dashboard/predict.html', context)

# FUNGSI BARU: Render halaman penolakan
def access_denied(request):
    return render(request, 'dashboard/access_denied.html')