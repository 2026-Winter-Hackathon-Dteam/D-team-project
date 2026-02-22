
def header_context(request):
    show_space_edit_button = False
    if not request.user.is_authenticated:
        return {"show_space_edit_button": False}
    
    # ユーザーがスペースを持っているか確認
    if request.user.space:
        # オーナーかどうか確認
        if request.user.space.owner_user_id == request.user.id:
            show_space_edit_button = True
    
    return {"show_space_edit_button": show_space_edit_button}