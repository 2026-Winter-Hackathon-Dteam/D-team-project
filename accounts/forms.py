import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from spaces.models import Spaces


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
# ユーザー作成フォーム
# オーナー
class OwnerSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
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


# ↓↓↓↓↓↓↓ 作成中のためレビュー対象外 ↓↓↓↓↓↓↓ 
# 一般ユーザー
class OwnerMemberCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["employee_id", "name", "password"]
    
    def __init__(self, *args, **kwargs):
        # フォームの初期化
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full border border-gray-400 rounded-lg p-3",
            })
# ↑↑↑↑↑↑ ここまで作成中のためレビュー対象外  ↑↑↑↑↑↑  


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