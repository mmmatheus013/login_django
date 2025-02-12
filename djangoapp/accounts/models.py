from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.contrib.auth import get_user_model
import uuid


class UsuarioManager(BaseUserManager):
    def create_user(self, cpf, email, password=None, **extra_fields):
        if not cpf or not email:
            raise ValueError("É necessário fornecer CPF e email.")
        email = self.normalize_email(email)
        user = self.model(cpf=cpf, email=email, is_active=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(cpf, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Controle de tentativas de login
    login_attempts = models.PositiveIntegerField( default=0)  # Campo para tentativas
    locked_until = models.DateTimeField(null=True, blank=True)  # Campo para bloqueio

    # Garantir que o usuário possa ser desativado
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Necessário para admin

    objects = UsuarioManager()



    USERNAME_FIELD = "email"  # Mudança para compatibilidade com django-allauth
    REQUIRED_FIELDS = ["cpf", "name"]

    def __str__(self):
        return self.email or self.cpf

    def is_locked(self):
        """Verifica se o usuário está temporariamente bloqueado"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def increment_login_attempts(self):
        """Aumenta as tentativas de login e bloqueia o usuário se ultrapassar o limite"""
        self.login_attempts += 1
        if self.login_attempts >= 5 and self.locked_until is None:  # Bloqueia após 5 tentativas erradas
            self.locked_until = timezone.now() + timedelta(minutes=5)  # Bloqueio de 5 min
        self.save()

    def reset_login_attempts(self):
        """Reseta as tentativas após um login bem-sucedido"""
        self.login_attempts = 0
        self.locked_until = None
        self.save()


User = get_user_model()


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    device = models.CharField(max_length=500)
    browser = models.CharField(max_length=500)
    login_time = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=500)

    def __str__(self):
        return f"LoginLog(user={self.user.email}, ip_address={self.ip_address}, device={self.device}, browser={self.browser}, login_time={self.login_time})"




