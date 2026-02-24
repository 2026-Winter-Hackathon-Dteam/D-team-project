import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from spaces.models import Spaces
from teams.models import Teams


# カスタムユーザークラスを取得
User = get_user_model()

# ***************************************************************************
# スペース作成フォーム(スペース作成はサインアップの一部のためaccountsアプリ内に作成)
class SpaceCreateForm(forms.ModelForm):
    class Meta:
        model = Spaces
        fields = ["name", "code"]
        labels = {
            "name":"スペース名（会社名など）",
            "code":"スペースコード（ログイン時に必要）"
        }
        widgets = {
            "code": forms.TextInput(attrs={
                "minlength":3,
                "maxlength": 3,
                "pattern": "^[A-Za-z0-9]{3}$",
                "placeholder": "半角英数字3桁",
            }),
        }

    def __init__(self, *args, **kwargs):
        # フォームの初期化
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "border border-gray-400 rounded-lg p-2",
            })

    def clean_code(self):
        code = self.cleaned_data["code"]
        return code.upper()

# ***************************************************************************
# オーナーユーザー作成フォーム
class OwnerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["employee_id", "name"]
        labels = {
            "employee_id":"社員ID",
            "name":"名前",
        }
        widgets = {
            "employee_id": forms.TextInput(attrs={
                "maxlength": 15,
                "pattern": "^[A-Za-z0-9]{1,15}$",
            }),
        }

    def __init__(self, *args, **kwargs):
        # フォームの初期化
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "border border-gray-400 rounded-lg p-2",
            })

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"]
        return employee_id.upper()

# ***************************************************************************
# 一般ユーザー作成フォーム
class OwnerMemberCreateForm(forms.ModelForm):
    teams = forms.ModelMultipleChoiceField(
        label="チーム",
        queryset=Teams.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = User
        fields = ["employee_id", "name", "is_admin"]
        labels = {
            "employee_id":"社員ID",
            "name":"名前",
        }
        widgets = {
            "employee_id": forms.TextInput(attrs={
                "maxlength": 15,
                "pattern": "^[A-Za-z0-9]{1,15}$",
                "class": "w-full border border-gray-400 rounded-lg p-3"
            }),
            "name":forms.TextInput(attrs={
                "class": "w-full border border-gray-400 rounded-lg p-3",
            }),
            "is_admin":forms.CheckboxInput(attrs={
                "class":"sr-only peer"
            })
        }
    
    # フォーム表示時の処理
    def __init__(self, *args, **kwargs):
        # ユーザー情報をを受け取る
        space = kwargs.pop("space", None)
        user = kwargs.pop("user", None)
        # フォームの初期化
        super().__init__(*args, **kwargs)

        if space:
            self.fields["teams"].queryset = Teams.objects.filter(space=space)

        # HTMLの{{ choice_label }} の表示名を指定
        self.fields["teams"].label_from_instance = (
              lambda obj: obj.name
        )
        # is_adminはオーナーユーザー以外に表示しない
        if user != space.owner_user:
            self.fields.pop("is_admin")
        
    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"]
        return employee_id.upper()


# ***************************************************************************
# ログインフォーム
class LoginForm(AuthenticationForm):
    space_code = forms.CharField(
        label="スペースコード",
        min_length=3,
        max_length=3,
        required=True,
        widget=forms.TextInput(attrs={
            "class":"border border-gray-400 rounded-lg p-2",
            "placeholder": "半角英数字3桁"
        })
    )
    employee_id = forms.CharField(
        label="社員ID",
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            "class":"border border-gray-400 rounded-lg p-2"
        })
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={
            "class":"border border-gray-400 rounded-lg p-2"
        })
    )

    def __init__(self, *args, **kwargs):
        # フォームの初期化
        super().__init__(*args, **kwargs)
        # username を非表示に
        self.fields["username"].widget = forms.HiddenInput()
        self.fields["username"].required = False

    def clean_space_code(self):
        value = self.cleaned_data["space_code"]
        value = value.upper()
        if not re.fullmatch(r"[A-Z0-9]{3}", value):
            raise forms.ValidationError("英数字3文字で入力してください")
        return value
    
    def clean_employee_id(self):
        value = self.cleaned_data["employee_id"]
        value = value.upper()
        if not re.fullmatch(r"[A-Z0-9]{1,15}", value):
            raise forms.ValidationError("英数字15文字以内で入力")
        return value
    
    def clean(self):
        space_code = self.cleaned_data.get("space_code")
        employee_id = self.cleaned_data.get("employee_id")

        if space_code and employee_id:
            login_id = f"{space_code}_{employee_id}"
            self.cleaned_data["username"] = login_id

        return super().clean()
    
# ***************************************************************************
# パスワード変更フォーム
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="旧パスワード",
        widget=forms.PasswordInput(attrs={
            "class":"border border-gray-400 rounded-lg p-2"
        })
    )
    new_password1 = forms.CharField(
        label="新パスワード",
        widget=forms.PasswordInput(attrs={
            "class":"border border-gray-400 rounded-lg p-2"
        })
    )
    new_password2 = forms.CharField(
        label="新パスワード（確認）",
        widget=forms.PasswordInput(attrs={
            "class":"border border-gray-400 rounded-lg p-2"
        })
    )

    def __init__(self, *args, **kwargs):
        # フォームの初期化
        super().__init__(*args, **kwargs)

# ***************************************************************************
# プロフィールフォーム
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "is_profile_public"]
        labels = {
            "name":"名前"
        }
        widgets = {
            "name":forms.TextInput(attrs={
                "class": "border border-gray-400 rounded-lg p-2 flex-[2]",
            }),
            "is_profile_public":forms.CheckboxInput(attrs={
                "class":"sr-only peer"
            })
        }

    # フォーム表示時の処理
    def __init__(self, *args, **kwargs):
        # ユーザー情報を受け取る
        user = kwargs.pop("user", None)
        # フォームの初期化
        super().__init__(*args, **kwargs)

        if user:
            self.fields["name"].initial = user.name
            self.fields["is_profile_public"].initial = user.is_profile_public
