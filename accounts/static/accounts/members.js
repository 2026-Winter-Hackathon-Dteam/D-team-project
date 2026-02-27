
  // ======= 「閉じる」処理 （イベント委譲） =======
  // モーダル全体（入れ替わらない外枠）に対して1回だけイベント登録
  document.addEventListener('click', (e) => {
    
    // --- 閉じるボタン（×ボタン・キャンセルボタン） ---
    if (e.target.closest('.modal-close')) {
      const modal = e.target.closest('.fixed.inset-0'); // 親のモーダル要素を探す
      if (modal) modal.classList.add('hidden');
    }

    // --- 背景クリックで閉じる ---
    if (e.target.classList.contains('modal-bg')) {
      const modal = e.target.closest('.fixed.inset-0');
      if (modal) modal.classList.add('hidden');
    }

    // --- ヘルプボタン ---
    if (e.target.closest('.btn-help')) {
      openTutorial(2);
    }
  });

  // ======= メンバー作成モーダル（イベント委譲） =======
  document.addEventListener('click', (e) => {
    const openBtn = e.target.closest('#openCreateMember');
    if (!openBtn) return;

    const createModal = document.getElementById('createMemberModal');
    // モーダル箱の中からformタグを探して、あればフォームのリセットを行う
    if (createModal) {
      const form = createModal.querySelector('form');
      if (form) {
        form.reset();
      }
      // createModal.classList.remove('hidden');
      // hiddenのつけ外しによる開閉ではなく、HTMXによる空箱の中身の入れ替えによる制御
    }
  });

  // ======= メンバー削除モーダル（イベント委譲） ======= 
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-delete');
    if (!btn) return;

    const deleteModal = document.getElementById('deleteMemberModal');
    const deleteText = document.getElementById('deleteTargetText');
    const deleteIdInput = document.getElementById('deleteTargetId');

    if (deleteModal && deleteText && deleteIdInput) {
      // datasetから情報を取得してセット
      deleteText.textContent = `${btn.dataset.name}：${btn.dataset.userId}`;
      deleteIdInput.value = btn.dataset.uuid;
      deleteModal.classList.remove('hidden');
    }
  });