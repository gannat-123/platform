from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'phone', 
            'email', 
            'password', 
            'password2',
            'role',
            'parent_phone',
            'governorate',
            'grade'
        ]
    
    def validate(self, data):
        # Check passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "كلمتا السر غير متطابقتين"})
        
        # Validate student fields
        if data.get('role') == 'student':
            if not data.get('parent_phone'):
                raise serializers.ValidationError({"parent_phone": "رقم ولي الأمر مطلوب للطلاب"})
            if not data.get('governorate'):
                raise serializers.ValidationError({"governorate": "المحافظة مطلوبة للطلاب"})
            if not data.get('grade'):
                raise serializers.ValidationError({"grade": "الصف الدراسي مطلوب للطلاب"})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "كلمتا السر غير متطابقتين"})
        return data