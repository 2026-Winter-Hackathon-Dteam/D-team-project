document.addEventListener('DOMContentLoaded', () => {

  // --- モーダル内の入力内容をリセットする関数 ---
  const resetModalForm = (modal) => {
    // モーダルを閉じたらフォーム入力内容をリセットする
    const forms = modal.querySelectorAll('form');
    forms.forEach(form => form.reset());
    // フォーム外のinput（検索窓など）をクリア
    const inputs = modal.querySelectorAll('input:not([type="hidden"])');
    inputs.forEach(input => { input.value = ''; });
  };

  // クリックイベント
  document.addEventListener('click', (e) => {
    
    //  背景クリックでモーダルを閉じる
    if (e.target.classList.contains('modal-bg')) {
      const modal = e.target.closest('.fixed.inset-0');
      if (modal) {
        resetModalForm(modal); // 閉じる前に入力をリセット
        modal.classList.add('hidden');
      }
      return;
    }

    // クリックされた要素の直近のボタンを取得
    const btn = e.target.closest('button');
    if (!btn) return;

    //  モーダルを閉じる（×ボタン）
    if (btn.classList.contains('modal-close')) {
      const modal = btn.closest('.fixed.inset-0');
      if (modal) {
        resetModalForm(modal); // 閉じる前に入力をリセット
        modal.classList.add('hidden');
      }
      return;
    }

    //  チーム作成
    if (btn.id === 'openCreateTeam') {
      document.getElementById('createTeamModal')?.classList.remove('hidden');
      return;
    }

    //  メンバー追加（右側の詳細エリア）
    if (btn.id === 'openAddMember') {
      document.getElementById('searchMemberModal')?.classList.remove('hidden');
      return;
    }

    //  チーム編集
    if (btn.classList.contains('btn-edit-team')) {
      e.preventDefault();
      document.getElementById('editTeamModal')?.classList.remove('hidden');
      return;
    }

    //  チーム削除
    if (btn.classList.contains('btn-delete-team')) {
      e.preventDefault();
      const modal = document.getElementById('deleteTeamModal');
      if (modal) {
        document.getElementById('deleteTargetText').textContent = btn.dataset.teamName;
        document.getElementById('deleteTargetId').value = btn.dataset.teamId;
        modal.classList.remove('hidden');
      }
      return;
    }

    //  メンバー削除
    if (btn.classList.contains('btn-delete-member')) {
      e.preventDefault();
      const modal = document.getElementById('deleteMemberModal');
      if (modal) {
        document.getElementById('memberDeleteTargetText').textContent = btn.dataset.memberName;
        document.getElementById('memberDeleteTargetId').value = btn.dataset.memberId;
        // display要素（ID）がある場合のみ代入
        const display = document.getElementById('memberDeleteTargetIdDisplay');
        if (display) display.textContent = btn.dataset.memberId;
        modal.classList.remove('hidden');
      }
      return;
    }

    //  ヘルプボタン
    if (btn.classList.contains('btn-help')) {
      if (typeof openTutorial === 'function') {
        openTutorial(4);
      }
      return;
    }

  }); 
});