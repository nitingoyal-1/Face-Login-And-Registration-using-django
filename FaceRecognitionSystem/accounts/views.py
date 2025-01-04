import face_recognition
import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import UserImages, User

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            face_image_data = request.POST['face_image']

            # Decode Base64 data
            face_image_data = face_image_data.split(",")[1]
            face_image = ContentFile(base64.b64decode(face_image_data), name=f'{username}.jpg')

            # Create user and save face image
            user = User.objects.create(username=username)  # Ensure this saves to the DB
            UserImages.objects.create(user=user, face_image=face_image)

            return JsonResponse({'status': 'success', 'message': 'User registered successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request,      u'register.html')
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        face_image_data = request.POST['face_image']

        # Get the user by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'})

        # Convert base64 image data to a file
        face_image_data = face_image_data.split(",")[1]
        uploaded_image = ContentFile(base64.b64decode(face_image_data), name=f'{username}_.jpg') #_.jpg

        # Compare the uploaded face image with the stored face image
        uploaded_face_image = face_recognition.load_image_file(uploaded_image)
        uploaded_face_encoding = face_recognition.face_encodings(uploaded_face_image)

        if uploaded_face_encoding:
            uploaded_face_encoding = uploaded_face_encoding[0]
            user_image = UserImages.objects.filter(user=user).first()  #last()

            stored_face_image = face_recognition.load_image_file(user_image.face_image.path)
            stored_face_encoding = face_recognition.face_encodings(stored_face_image)[0]

            print(stored_face_image, stored_face_encoding)
            # Compare the faces
            match = face_recognition.compare_faces([stored_face_encoding], uploaded_face_encoding)
            if match[0]:
                return JsonResponse({'status': 'success', 'message': 'Login successful!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Face recognition failed.'})

        return JsonResponse({'status': 'error', 'message': 'No face detected in the image.'})

    return render(request, 'login.html')


