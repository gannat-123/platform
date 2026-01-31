from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.site_header = "منصةتعليمية - لوحة التحكم"
admin.site.site_title = "إدارة المنصة"
admin.site.index_title = "مرحباً بك في لوحة التحكم"

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # الحقول اللي هتظهر في قائمة الـ users
    list_display = ['phone', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    
    # الحقول اللي ممكن تعملي بيها filter
    list_filter = ['role', 'is_staff', 'is_active', 'governorate', 'grade']
    
    # الحقول اللي ممكن تعملي بيها search
    search_fields = ['phone', 'email', 'first_name', 'last_name']
    
    # ترتيب الـ users
    ordering = ['-date_joined']
    
    # الحقول في صفحة التعديل/الإضافة
    fieldsets = (
        ('معلومات الدخول', {
            'fields': ('phone', 'email', 'password')
        }),
        ('المعلومات الشخصية', {
            'fields': ('first_name', 'last_name', 'role')
        }),
        ('معلومات الطالب', {
            'fields': ('parent_phone', 'governorate', 'grade'),
            'classes': ('collapse',),  # قابلة للطي
        }),
        ('الصلاحيات', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('تواريخ مهمة', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    # الحقول عند إضافة user جديد
    add_fieldsets = (
        ('معلومات أساسية', {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
        ('معلومات إضافية', {
            'classes': ('wide',),
            'fields': ('parent_phone', 'governorate', 'grade'),
        }),
    )


# تسجيل الـ model في الـ admin
admin.site.register(CustomUser, CustomUserAdmin)