from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password  # ← ضيفي السطر ده

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'تم إنشاء الحساب بنجاح',
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'email': user.email,
                    'role': user.role,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return Response({
                    'error': 'رقم الهاتف أو كلمة السر غير صحيحة'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Authenticate using username (which is phone)
            user = authenticate(username=user.username, password=password)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'تم تسجيل الدخول بنجاح',
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': user.phone,
                        'email': user.email,
                        'role': user.role,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'رقم الهاتف أو كلمة السر غير صحيحة'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset link (adjust based on your frontend URL)
                reset_link = f"http://localhost:3000/reset-password/{uid}/{token}/"
                
                # Send email
                subject = 'إعادة تعيين كلمة السر'
                message = f'''
مرحباً {user.first_name},

لقد تلقينا طلباً لإعادة تعيين كلمة السر الخاصة بك.

الرجاء الضغط على الرابط التالي لإعادة تعيين كلمة السر:
{reset_link}

إذا لم تطلب إعادة تعيين كلمة السر، يرجى تجاهل هذه الرسالة.

مع تحياتنا
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'تم إرسال رسالة إلى بريدك الإلكتروني لإعادة تعيين كلمة السر',
                    'uid': uid,
                    'token': token  # في الـ production ما ترجعيش الـ token في الـ response
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                # لأسباب أمنية، نرجع نفس الرسالة حتى لو المستخدم مش موجود
                return Response({
                    'message': 'إذا كان البريد الإلكتروني موجوداً، سيتم إرسال رسالة لإعادة تعيين كلمة السر'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'رابط غير صالح'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({
                'error': 'رابط غير صالح أو منتهي الصلاحية'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # نستخدم serializer بسيط بدون token field
        password = request.data.get('password')
        password2 = request.data.get('password2')
        
        if not password or not password2:
            return Response({
                'error': 'كلمتا السر مطلوبتان'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password != password2:
            return Response({
                'error': 'كلمتا السر غير متطابقتين'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        try:
            validate_password(password, user)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.save()
        
        return Response({
            'message': 'تم إعادة تعيين كلمة السر بنجاح'
        }, status=status.HTTP_200_OK)