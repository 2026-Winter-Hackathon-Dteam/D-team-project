from django import forms
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import Spaces


class CustomOwnerRadioSelect(forms.RadioSelect):
    """カスタムスタイルのRadioSelectウィジェット"""
    
    def render(self, name, value, attrs=None, renderer=None):
        if not self.choices:
            return format_html('<div class="p-3 border-t border-gray-100">メンバーがいません</div>')
        
        output = []
        for option_value, option_label in self.choices:
            checked = 'checked' if str(option_value) == str(value) else ''
            output.append(
                f'<label class="flex items-center justify-between gap-2 p-2 rounded cursor-pointer hover:bg-gray-50">'
                f'<span>{option_label}</span>'
                f'<input type="radio" name="{name}" value="{option_value}" '
                f'class="w-5 h-5 border border-gray-400 appearance-none rounded-full '
                f'checked:bg-teamy-orange cursor-pointer" {checked}>'
                f'</label>'
            )
        return format_html('<div class="p-3 border-t border-gray-100 max-h-40 overflow-y-auto space-y-2">{}</div>', 
                          format_html(''.join(output)))


class SpaceEditForm(forms.ModelForm):
    class Meta:
        model = Spaces
        fields = ['name']  # 編集可能なフィールドを指定
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'border border-gray-400 rounded-lg p-2 flex-[2]',
                'placeholder': 'スペース名を入力'
            }),
        }
        
class SpaceOwnerChangeForm(forms.Form):
    owner_id = forms.ChoiceField(
        widget=CustomOwnerRadioSelect,
        label='新しいオーナーを選択',
        required=False
    )
    
    def __init__(self, space, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # スペースに所属するユーザーを取得
        User = get_user_model()
        members = User.objects.filter(space=space).order_by('name')
        
        # ChoiceFieldの選択肢を設定
        self.fields['owner_id'].choices = [
            (str(member.id), f"{member.name}（{member.employee_id}）")
            for member in members
        ]