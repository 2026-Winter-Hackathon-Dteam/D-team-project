from django import forms
from .models import Teams, Team_Users
from django.contrib.auth import get_user_model

User = get_user_model()


# チーム作成フォーム
class TeamCreateForm(forms.ModelForm):

    class Meta:
        model = Teams
        fields = ["name", "description"]
        labels = {
            "name": "チーム名",
            "description": "説明"
        }

    def __init__(self, *args, **kwargs):
        self.space = kwargs.pop("space", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full border border-gray-400 rounded-lg p-3"
            })

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError("チーム名を入力してください")

        if Teams.objects.filter(
            name=name,
            space=self.space
        ).exists():
            raise forms.ValidationError("同じ名前のチームが既に存在します")

        return name



# チーム編集フォーム
class TeamEditForm(forms.ModelForm):

    class Meta:
        model = Teams
        fields = ["name", "description"]
        labels = {
            "name": "チーム名",
            "description": "チームについての説明",
        }
        widgets = {
            "description": forms.Textarea(attrs={
                "maxlength": 30,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.space = kwargs.pop("space", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data["name"]

        if not name:
            raise forms.ValidationError("チーム名を入力してください")

        # 自分以外で同名があるかチェック
        if Teams.objects.filter(
            name=name,
            space=self.space
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("同じ名前のチームが既に存在します")

        return name



# メンバー追加フォーム
class AddMemberForm(forms.Form):
    team_id = forms.UUIDField()
    user_id = forms.UUIDField()

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        # 他フォームと統一したUIクラス
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "border border-gray-400 rounded-lg p-2",
            })

    def clean(self):
        cleaned_data = super().clean()

        team_id = cleaned_data.get("team_id")
        user_id = cleaned_data.get("user_id")

        # 必須チェック（UUIDFieldで基本弾かれるが念のため）
        if not team_id or not user_id:
            raise forms.ValidationError("不正な操作です。")

        # チーム取得（スペース制限込み）
        try:
            team = Teams.objects.get(
                id=team_id,
                space=self.current_user.space
            )
        except Teams.DoesNotExist:
            raise forms.ValidationError("不正なチームです。")

        # ユーザー取得
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise forms.ValidationError("存在しないユーザーです。")

        # スペース整合性チェック
        if user.space_id != self.current_user.space_id:
            raise forms.ValidationError("別スペースのユーザーは追加できません。")

        # 有効ユーザーか
        if hasattr(user, "is_active") and not user.is_active:
            raise forms.ValidationError("無効なユーザーです。")

        # 重複チェック
        if Team_Users.objects.filter(team=team, user=user).exists():
            raise forms.ValidationError("すでにチームメンバーです。")

        # save()で使えるよう保持
        self.team = team
        self.user = user

        return cleaned_data

    def save(self):
        return Team_Users.objects.create(
            team=self.team,
            user=self.user
        )