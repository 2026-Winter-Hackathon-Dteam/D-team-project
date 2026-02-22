import re
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


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
                regex=r'^[A-Z0-9]{3}$',
                message='英数字3文字で入力してください'
            )
        ],
        unique=True, 
        verbose_name="スペースコード"
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # カスタムUserモデルを参照
        on_delete=models.CASCADE, 
        related_name="owned_spaces",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Spaces"
        verbose_name = "スペース"
        verbose_name_plural = "スペース"

    def __str__(self):
        return f"{self.name}({self.code})"
    
    def clean(self):
        if self.code:
            value_code = self.code.strip().upper()

            if not re.fullmatch(r"^[A-Z0-9]{3}$", value_code):
                raise ValidationError("スペースコードは英数字3文字以内")
            self.code = value_code

    # 保存時に呼ぶuser.save()をオーバーライド
    # 英文字を大文字に揃えて保存
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

