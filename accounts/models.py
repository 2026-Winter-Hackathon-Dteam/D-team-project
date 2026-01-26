from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


# userを作成するための設定
class CustomUserManager(BaseUserManager):
    def create_user(self, employee_id, username, password=None, **extra_fields):
        if not employee_id:
            raise ValueError('社員IDは必須です')
        
        user = self.model(employee_id=employee_id, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, employee_id, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(employee_id, username, password, **extra_fields)


# Usersテーブル
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ユーザーID"
    )
    employee_id = models.CharField(max_length=15, verbose_name="社員ID")
    login_id = models.CharField(max_length=18, unique=True)
    name = models.CharField(max_length=150, verbose_name="ユーザー名") 
    space = models.ForeignKey("spaces.Spaces", on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False, verbose_name="管理者権限設定")
    is_profile_public = models.BooleanField(default=False, verbose_name="プライバシー設定")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ログイン時に使用する識別子を指定
    USERNAME_FIELD = "login_id"
    # スーパーユーザー作成時に必要
    REQUIRED_FIELDS = ["name"]  
    #「ユーザーを作成・管理するためのマネージャークラス（CustomUserManager）」を使う宣言
    objects = CustomUserManager()

    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id","space"],
                name="unique_user_space"
            )
        ]
        db_table = "Users"
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"
    
    # adminやログに出力する文字列の設定
    def __str__(self):
        return f"{self.employee_id}({self.space.code})"
