import secrets
import string
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError
from .models import CustomUser
from .forms import OwnerSignUpForm, OwnerMemberCreateForm ,SpaceCreateForm, LoginForm


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
                space, owner = CustomUser.objects.create_space_with_owner(
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
# ↓↓↓↓↓↓↓ 作成中のためレビュー対象外 ↓↓↓↓↓↓↓ 
# 一般ユーザー作成
class OwnerMemberCreateView(LoginRequiredMixin, View):
    # 未ログイン時にログイン画面に遷移
    login_url = "login"
    template_name = "accounts/modals/create_member.html"

    def get(self, request):
        self.space = request.user.space
        user_form = OwnerMemberCreateForm()
        created_user = None

        # 新規ユーザー作成後にリダイレクト時に登録ユーザー情報を表示
        created_user_id = request.session.pop("created_user_id", None)
        initial_password = request.session.pop("initial_password", None)
        
        if created_user_id:
            created_user = CustomUser.objects.get(login_id=created_user_id)
        context = {
            "user_form":user_form,
            # Noneまたはさっき登録したユーザー情報が含まれる
            "created_user":created_user,
            "initial_password":initial_password
        }
        return render(request, self.template_name, context)
    

    def post(self, request):
        self.space = request.user.space
        user_form = OwnerMemberCreateForm(request.POST)

        if user_form.is_valid():
            # 新規作成ユーザー登録後の表示のためパスワードを変数に格納
            raw_password = generate_password()
            # 所属スペースの取得
            space = request.user.space
            if not space:
                user_form.add_error(None, "所属スペースが見つかりません")
                return render(request, self.template_name, {"user_form":user_form})
            
            try:
                member = CustomUser.objects.create_member(
                    space = space,
                    employee_id = user_form.cleaned_data["employee_id"],
                    password=raw_password,
                    name=user_form.cleaned_data["name"]
                ) 
                # 新規作成ユーザー登録後の情報表示のためにセッションを保持（URLで渡さない）
                request.session["initial_password"] = raw_password
                request.session["created_user_id"] = member.login_id
                return redirect("create_member_modal")
            
            except IntegrityError:
                user_form.add_error(None, "登録処理中にエラーが発生しました")
        
        return render(request, self.template_name, {"user_form":user_form})
# ↑↑↑↑↑↑ ここまで作成中のためレビュー対象外  ↑↑↑↑↑↑   

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
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")  

# ***************************************************************************
# ランダムパスワードの生成
def generate_password(length=10):
    chars=string.ascii_letters + string.digits
    return ''.join(secrets.chice(chars)for _ in range(length))
