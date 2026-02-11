/* =====================
 * sessionStorage
 * ===================== */
console.log("questions.js loaded");

const radios = document.querySelectorAll('.answer');
// 全ラジオを取得

// ===== 保存 =====
function saveAnswer(questionId, value) {
  const data = JSON.parse(sessionStorage.getItem('answers') || '{}');
  // ブラウザからanswersというデータを読み、空だったら{}を使う
  // JSON.parseが配列の中身の文字列をJSオブジェクトに変換
  data[questionId] = value;
  // dataオブジェクトを作り、質問：回答のセットを格納していく
  sessionStorage.setItem('answers', JSON.stringify(data));
  // dataを文字列にしてブラウザのsessionStorageにanswersという名前で保存する
  // JSON.stringify(data)が文字列に変換
}

// ラジオ選択が変わるたびにqidと値を保存
radios.forEach(radio => {
  radio.addEventListener('change', () => {
    saveAnswer(radio.dataset.qid, radio.value);

    // ===== 次の質問へスクロール =====
    const current = radio.closest('.question-block');
    if (!current) return;

    const hr = current.nextElementSibling;
    if (!hr) return;
    // 現質問ブロックの次の<hr>区切り線までを取得 なければ終了

    const next = hr.nextElementSibling;
    if (!next) return;   
    // <hr>の次の兄弟要素（次の質問ブロック）を取得 なければ終了

    if (next) {
      next.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// ===== 復元 =====
function restoreAnswers() {
  const data = JSON.parse(sessionStorage.getItem('answers') || '{}');

  const entries = Object.entries(data);
  // dataオブジェクトを[キー（質問）：値（回答）]の配列にして、ループで1件ずつ扱えるようにする

  entries.forEach(entry => {
    const questionId = entry[0];
    const value = entry[1];
    // 配列から一つずつ要素を取り出してキーと値を変数に入れる

    const selector = `input[data-qid="${questionId}"][value="${value}"]`;
    // 質問IDと回答値に合うラジオボタンを探すための条件となるセレクタ文字列をつくる
    const radio = document.querySelector(selector);
    // 条件一致する要素を探す

    if (radio) {
      radio.checked = true;
      // 条件一致した箇所のラジオにチェックをつける
    }
  });
}

// ページ読み込み時に保存内容を復元
document.addEventListener('DOMContentLoaded', () => {
  restoreAnswers();
});

// 次へボタン
function nextPage(pageNumber) {
  window.location.href = `/analysis/questions/${pageNumber}/`;
}

// ===== 回答を送信＆未回答バリデーション =====
const form = document.getElementById('question-form');

form.addEventListener('submit', (e) => {
  const blocks = document.querySelectorAll('.question-block');
  let allAnswered = true;
  // submitイベント時にすべてのquestion-blockを取得しtrueと仮定

  blocks.forEach(block => {
    const checked = block.querySelector('input[type="radio"]:checked');
    if (!checked) {
      allAnswered = false;
    }
  });
  // 1つずつ回答をチェックし未回答ならfalseにする

  if (!allAnswered) {
    e.preventDefault(); // ← falseなら送信を止める
    alert('未回答の質問があります');
    return;
  }

});
