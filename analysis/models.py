from django.db import models
from django.conf import settings
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

#Value_Masterテーブル
class ValueMaster(models.Model):
    value_key = models.CharField(max_length=20, primary_key=True)
    is_active = models.BooleanField(default=True)
    
    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        db_table = 'Value_Master'
        
    # adminやログに出力する文字列の設定   
    def __str__(self):
        return self.value_key
    
#User_Value_Scoresテーブル
class UserValueScore(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False, 
        verbose_name="ユーザー回答スコアID"
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_value_scores"
        )
    value_key = models.ForeignKey("ValueMaster", on_delete=models.PROTECT, related_name="user_scores")
    personal_score = models.SmallIntegerField(
        validators=[MinValueValidator(-12), MaxValueValidator(12)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        db_table = "User_Value_Scores"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["user", "value_key"]),
        ]
    
    # adminやログに出力する文字列の設定
    def __str__(self):
        return f"{self.user} - {self.value_key} : {self.personal_score}"

# Team_Value_Scoresテーブル
class TeamValueScore(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False, 
        verbose_name="チーム回答スコアID"
        )
    team = models.ForeignKey("teams.Teams", on_delete=models.CASCADE, related_name="team_value_scores")
    value_key = models.ForeignKey("ValueMaster", on_delete=models.PROTECT, related_name="team_scores")
    mean = models.FloatField()
    max_diff = models.IntegerField()
    std = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        db_table = "Team_Value_Scores"
        indexes = [
            models.Index(fields=["team", "created_at"]),
            models.Index(fields=["team", "value_key"]),
        ]

    # adminやログに出力する文字列の設定
    def __str__(self):
        return f"{self.team} - {self.value_key}"

# User_Advicesテーブル       
class UserAdvice(models.Model):

    class Importance(models.TextChoices):
        HIGH = "high", "高"
        MIDDLE = "middle", "中"
        LOW = "low", "低"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ユーザーアドバイスID"
    )
    value_key = models.ForeignKey("ValueMaster", on_delete=models.PROTECT, related_name="user_advices")
    importance = models.CharField(
        max_length=10,
        choices=Importance.choices
    )
    is_minus_side = models.BooleanField(default=False)
    advice_text = models.TextField()

    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        db_table = "User_Advices"
        constraints = [
            models.UniqueConstraint(
                fields=["value_key", "importance", "is_minus_side"],
                name="unique_user_advice"
            )
        ]

    # adminやログに出力する文字列の設定
    def __str__(self):
        side = "MINUS" if self.is_minus_side else "PLUS"
        return f"{self.value_key} - {self.importance} - {side}"


# Team_Advicesテーブル
class TeamAdvice(models.Model):
        
    class Code(models.TextChoices):
        Q1 = "Q1_stable_harmony", "安定調和型"
        Q2 = "Q2_deep_focus", "視点深化型"
        Q3 = "Q3_partial_diversity", "部分多様型"
        Q4 = "Q4_wide_diversity", "広域多様型"
        
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="チームアドバイスID"
    )
    code = models.CharField(
    max_length=30,
    choices=Code.choices
    )
    value_key = models.ForeignKey("ValueMaster", on_delete=models.PROTECT, related_name="team_advices")
    situation_text = models.TextField()
    summary_text = models.TextField()
    detail_text = models.TextField()
    
    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        db_table = "Team_Advices"
        constraints = [
            models.UniqueConstraint(
                fields=["value_key", "code"],
                name="unique_team_advice"
            )
        ]
    # adminやログに出力する文字列の設定
    def __str__(self):
        return f"{self.value_key} - {self.code}"
    
# Questionsテーブル
class Question(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="質問"
    )
    value_key = models.ForeignKey("ValueMaster", on_delete=models.PROTECT, related_name="questions")
    text = models.TextField()
    is_reverse = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # モデルのDB・表示まわりの設定(特にadmin使用時)
    class Meta:
        db_table = "Questions"
        
    # adminやログに出力する文字列の設定
    def __str__(self):
        return f"{self.value_key}({self.text})"