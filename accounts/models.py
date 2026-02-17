import re
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from spaces.models import Spaces


# ***************************************************************************
# userを作成するための設定
class CustomUserManager(BaseUserManager):
    # ユーザー作成：どの役割にも共通
    def create_user(self, space, employee_id, password=None, **extra_fields):
        if not space:
            raise ValueError('所属スペースは必須です。')
        if not employee_id:
            raise ValueError('employee_idは必須です。')

        # ログインIDの生成
        login_id = f"{space.code}_{employee_id}".upper()

        if not login_id:
            raise ValueError('login_idの生成に失敗しました。')
        if not extra_fields.get("name"):
            raise ValueError('ユーザー名は必須です。')
        # 権限をデフォルトに設定
        extra_fields.setdefault("is_profile_public", False)

        # データの保存
        user = self.model(login_id=login_id, space=space, employee_id=employee_id, **extra_fields)
        # ハッシュ化して保存
        user.set_password(password)
        user.save()
        return user
    
    # 一般ユーザー作成
    def create_member(self, space, employee_id, password=None, **extra_fields):
        if not extra_fields.get("is_admin"):
            extra_fields.setdefault("is_admin", False)
        
        return self.create_user(
            space = space,
            employee_id=employee_id,
            password=password,
            **extra_fields
        )
    
    # オーナー作成
    def create_owner(self, space, employee_id, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        
        return self.create_user(
            space = space,
            employee_id = employee_id,
            password = password,
            **extra_fields
        )

    # オーナーとスペースの同時作成
    @transaction.atomic
    def create_space_with_owner(self, space_name, space_code, employee_id, password, **extra_fields):
        space = Spaces.objects.create(
            name = space_name,
            code = space_code
        )
        owner = self.create_owner(
            space = space,
            employee_id = employee_id,
            password = password,
            **extra_fields
        )
        space.owner_user = owner
        return space, owner

    #スーパーユーザーの作成
    def create_superuser(self, login_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        _, employee_id = login_id.split("_")
        system_space, _ = Spaces.objects.get_or_create(
            code = "sys",
            defaults = {"name":"スーパーユーザー専用スペース"}
        )
        return self.create_user(system_space, employee_id, password, **extra_fields)


# ***************************************************************************
# Usersテーブル
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ユーザーID"
    )
    employee_id = models.CharField(
        max_length=15, 
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{1,15}$',
                message='英数字1文字から15文字で入力してください'
            )
        ],
        verbose_name="社員ID"
    )
    login_id = models.CharField(
        max_length=19,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{3}_[A-Z0-9]{1,15}$',
                message='login_idの形式が不正です'
            )
        ],
        unique=True
    )
    name = models.CharField(max_length=150, verbose_name="ユーザー名") 
    space = models.ForeignKey("spaces.Spaces", on_delete=models.CASCADE, related_name="users")
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
            # 社員IDとスペースIDで一意制約
            models.UniqueConstraint(
                fields = ["employee_id","space"],
                name = "unique_user_space"
            )
        ]
        db_table = "Users"
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"
    
    # adminやログに出力する文字列の設定
    def __str__(self):
        return f"{self.login_id}({self.space.code})"
    
    def clean(self):
        if self.employee_id:
            value_employee_id = self.employee_id.strip().upper()

            if not re.fullmatch(r"^[A-Z0-9]{1,15}$", value_employee_id):
                raise ValidationError("社員IDは英数字15文字以内")
            self.employee_id = value_employee_id

    # 保存時に呼ぶuser.save()をオーバーライド
    def save(self, *args, **kwargs):
        # フィールド検証, model.clean(), uniqueチェック
        self.full_clean()
        super().save(*args, **kwargs)