from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from .forms import OwnerSignUpForm,SpaceCreateForm, LoginForm


# カスタムユーザークラスを取得
User = get_user_model()

# ***************************************************************************
# サインアップ：オーナー
class OwnerSignupView(View):
    template_name = "accounts/signup_owner.html"

    def get(self, request):
        space_form = SpaceCreateForm()
        user_form = OwnerSignUpForm()

        context = {
            "space_form":space_form,
            "user_form":user_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # 回答を受け取る
        space_form = SpaceCreateForm(request.POST)
        user_form = OwnerSignUpForm(request.POST)
        context = {
            "space_form":space_form,
            "user_form":user_form,
        }

        # 入力項目のバリデーションチェック
        if space_form.is_valid() and user_form.is_valid():
            try:
                space, owner = User.objects.create_space_with_owner(
                    space_name=space_form.cleaned_data["name"],
                    space_code=space_form.cleaned_data["code"],
                    password=user_form.cleaned_data["password1"],
                    name=user_form.cleaned_data["name"],
                    employee_id=user_form.cleaned_data["employee_id"],
                )
                # 正常登録出来たらログインページにリダイレクト
                return redirect("accounts:login")
            
            # データベースのデータ整合性ルール（制約）に違反したときに発生するエラー
            except IntegrityError:
                user_form.add_error(None, "登録処理中にエラーが発生しました")
        
        return render(request, self.template_name, context)
      

# ***************************************************************************
# ログイン
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"

    # ログイン後の遷移先指定
    def get_success_url(self):
        user = self.request.user
        # 役割によって分離
        if user.is_admin:
            return reverse_lazy("accounts:top")
        else:
            return reverse_lazy("analysis:personal_analysis")

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


# ***************************************************************************
# ログアウト
class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("accounts:login")  
    http_method_names = ['post']

