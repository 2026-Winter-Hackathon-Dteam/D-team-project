from django.db import models
from django.conf import settings
import uuid

class Teams(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="チームID"
    )    
    name = models.CharField(max_length=150, verbose_name="チーム名")
    description = models.CharField(max_length=30,verbose_name="チーム説明",null=True,blank=True)
    space = models.ForeignKey("spaces.Spaces", on_delete=models.CASCADE)
    # related_nameは逆算参照時に使用
    leader_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="led_teams", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Teams"
        verbose_name = "チーム"
        verbose_name_plural = "チーム"
    def __str__(self):
        return f"{self.name}({self.space.code})"


class Team_Users(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="チームユーザーID"
    )
    team = models.ForeignKey("Teams", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team","user"],
                name="unique_team_user"
            )
        ]
        db_table = "Team_Users"
    

