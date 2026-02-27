document.addEventListener('DOMContentLoaded', () => {

  const createErrFlag = document.getElementById('create-team-error-flag');
  if (createErrFlag) {
    document.getElementById('createTeamModal')?.classList.remove('hidden');
  }

  const editErrFlag = document.getElementById('edit-team-error-flag');
  if (editErrFlag) {
    document.getElementById('editTeamModal')?.classList.remove('hidden');
  }

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

    // チーム編集（最優先で処理）
    const editBtn = e.target.closest('.btn-edit-team');
    if (editBtn) {
      e.preventDefault();
      e.stopPropagation();
      const modal = document.getElementById('editTeamModal');
      if (modal) {
        // まず前回入力を消す
        resetModalForm(modal);

        // team_id
        const idInput = document.getElementById('editTargetId');
        if (idInput) idInput.value = editBtn.dataset.teamId || '';

        // team名
        const nameInput = modal.querySelector('input[name="name"]');
        if (nameInput) nameInput.value = editBtn.dataset.teamName || '';

        // description
        const descTextarea = modal.querySelector('textarea[name="description"]');
        if (descTextarea) descTextarea.value = editBtn.dataset.teamDescription || '';

        modal.classList.remove('hidden');
      }
      return;
    }

    // チーム削除（最優先で処理）
    const deleteTeamBtn = e.target.closest('.btn-delete-team');
    if (deleteTeamBtn) {
      e.preventDefault();
      e.stopPropagation();
      const modal = document.getElementById('deleteTeamModal');
      if (modal) {
        const text = document.getElementById('deleteTargetText');
        if (text) text.textContent = deleteTeamBtn.dataset.teamName;

        const idInput = document.getElementById('deleteTargetId');
        if (idInput) idInput.value = deleteTeamBtn.dataset.teamId;

        modal.classList.remove('hidden');
      }
      return;
    }

    // チーム行クリック処理
    const row = e.target.closest('.team-row');
    if (row) {

      // ボタンなら無視
      if (e.target.closest('button')) return;

      const teamId = row.dataset.teamId;
      location.href = `?team_id=${teamId}`;
      return;
    }

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

    //  メンバー削除
    if (btn.classList.contains('btn-delete-member')) {
      e.preventDefault();
      const modal = document.getElementById('deleteMemberModal');
      if (modal) {
        document.getElementById('memberDeleteTargetText').textContent = btn.dataset.memberName;
        document.getElementById('memberDeleteTargetId').value = btn.dataset.memberId;
        document.getElementById('memberDeleteTargetEmployeeId').textContent = btn.dataset.memberEmployeeId; // 社員ID表示用
        // display要素（ID）がある場合のみ代入
        const display = document.getElementById('memberDeleteTargetIdDisplay');
        if (display) display.textContent = btn.dataset.memberId;
        // リーダー削除確認
        const leaderNotice = document.getElementById('leaderNotice');
        if (leaderNotice) {
          if (btn.dataset.isLeader === "true") {
            leaderNotice.classList.remove('hidden');
          } else {
            leaderNotice.classList.add('hidden');
          }
        }

        modal.classList.remove('hidden');
      }
      return;
    }

    // リーダー設定
    if (btn.classList.contains('btn-set-leader')) {
      e.preventDefault();

      const memberId = btn.dataset.memberId;
      const memberName = btn.dataset.memberName;
      const employeeId = btn.dataset.memberEmployeeId;
      const teamId = btn.dataset.teamId;

      const message = employeeId
      ? `${memberName}（${employeeId}）をリーダーにしますか？`
      : `${memberName}をリーダーにしますか？`;

      if (!confirm(message)) return;

      fetch('/teams/set-leader/', {
        // POST先URLを仮設定 要BEすり合わせ
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
          team_id: teamId, 
          member_id: memberId,
         })
        // DjangoルールのJSON形式宣言とCSRFトークン
      })
      .then(() => location.reload());

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

// ===== HTMX用 CSRF自動付与 =====
document.body.addEventListener('htmx:configRequest', function (event) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]');
  if (csrfToken) {
    event.detail.headers['X-CSRFToken'] = csrfToken.content;
  }
});

// ===== HTMX後処理（delete member成功時にモーダルを閉じる） =====
document.body.addEventListener('htmx:afterRequest', function (event) {

  // deleteMemberForm からの通信だけ処理する
  if (event.detail.elt.id !== 'deleteMemberForm') return;

  // ステータスが成功時のみ
  if (event.detail.xhr.status === 200) {
    const modal = document.getElementById('deleteMemberModal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }
});