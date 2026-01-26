from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import uuid

# Spacesテーブル
class Spaces(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="スペースID"
    )    
    name = models.CharField(max_length=150, verbose_name="スペース名")
    code = models.CharField(
        max_length=3, 
        validators=[
            RegexValidator(
                # r''(raw文字列)
                regex=r'^[a-zA-Z0-9]{3}$',
                message='3桁の英数字のみ入力してください'
            )
        ],
        unique=True, 
        verbose_name="スペースコード"
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # カスタムUserモデルを参照
        on_delete=models.CASCADE, 
        related_name="owned_spaces"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Spaces"
        verbose_name = "スペース"
        verbose_name_plural = "スペース"
    def __str__(self):
        return f"{self.name}({self.code})"

