from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where phone is the unique identifier
    instead of username.
    """
    def create_user(self, phone, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a regular user with the given phone and password.
        """
        if not phone:
            raise ValueError('رقم الهاتف مطلوب')
        if not email:
            raise ValueError('البريد الإلكتروني مطلوب')
        
        email = self.normalize_email(email)
        user = self.model(
            phone=phone,
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=phone,  # استخدام الـ phone كـ username
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a superuser with the given phone and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    GOVERNORATE_CHOICES = (
        ('cairo', 'Cairo'),
        ('giza', 'Giza'),
        ('alexandria', 'Alexandria'),
        ('dakahlia', 'Dakahlia'),
        ('red_sea', 'Red Sea'),
        ('beheira', 'Beheira'),
        ('fayoum', 'Fayoum'),
        ('gharbiya', 'Gharbiya'),
        ('ismailia', 'Ismailia'),
        ('menofia', 'Menofia'),
        ('minya', 'Minya'),
        ('qaliubiya', 'Qaliubiya'),
        ('new_valley', 'New Valley'),
        ('suez', 'Suez'),
        ('aswan', 'Aswan'),
        ('assiut', 'Assiut'),
        ('beni_suef', 'Beni Suef'),
        ('port_said', 'Port Said'),
        ('damietta', 'Damietta'),
        ('sharkia', 'Sharkia'),
        ('south_sinai', 'South Sinai'),
        ('kafr_el_sheikh', 'Kafr El-Sheikh'),
        ('matrouh', 'Matrouh'),
        ('luxor', 'Luxor'),
        ('qena', 'Qena'),
        ('north_sinai', 'North Sinai'),
        ('sohag', 'Sohag'),
    )
    
    GRADE_CHOICES = (
        ('1', 'الصف الأول الثانوي'),
        ('2', 'الصف الثاني الثانوي'),
        ('3', 'الصف الثالث الثانوي'),
    )
    
    # Override username to not be required
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    
    # Required fields
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    # Student specific fields
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    governorate = models.CharField(max_length=50, choices=GOVERNORATE_CHOICES, blank=True, null=True)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True, null=True)
    
    objects = CustomUserManager()  # استخدام الـ Custom Manager
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"
    
    def save(self, *args, **kwargs):
        # Auto-generate username from phone if not provided
        if not self.username:
            self.username = self.phone
        super().save(*args, **kwargs)