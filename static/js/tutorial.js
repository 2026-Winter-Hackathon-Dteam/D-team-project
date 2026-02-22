//  ================ 表示切り替え処理 ================ 

const slides = Array.from(document.querySelectorAll(".tutorial-slide"));
  // すべてのスライド要素をまとめて配列(Array)として準備
let currentStep = 1; 
  // 表示中のスライド番号（1枚目からスタート）

const showStep = (step) => {
  slides.forEach(slide => {
    const s = Number(slide.dataset.step);
    slide.classList.toggle("hidden", s !== step);
  });
};
  // stepを引数として受け取る関数を、変数showStepにする
  // data-stepから取得した番号(s)が、表示したい番号（step）と違ったらhidden
  // 同じだったらhiddenを外す
  // classList.toggle（クラス名,条件）は、trueならクラスを付け、falseなら外す

//  ================ モーダル開閉をする関数 ================ 

// オープン（hiddenを外す）
function openTutorial(startStep = 1) {
  currentStep = startStep;
  showStep(currentStep);
  document.getElementById("tutorial-modal").classList.remove("hidden");
}
  // 引数なしなら1スライド目からスタート
  // 途中スライドからスタートするページでは引数を渡す

// クローズ（hiddenをつける）
function closeTutorial() {
  document.getElementById("tutorial-modal").classList.add("hidden");
}

//  ================ クリックイベント処理 ================ 
  document.addEventListener("click", (e) => {

    // --- ？ボタン（btn-help） ---
    if (e.target.closest(".btn-help")) {
      openTutorial();
      return;
    }
    
    // --- ×ボタン（btn-close） ---
    if (e.target.closest(".btn-close")) {
      closeTutorial();
      return;
    }
    
    // --- モーダル背景クリックで閉じる ---
    const bg = document.getElementById("tutorial-bg")
    if (e.target === bg) {
      closeTutorial();
      return;  
    }  
      // 背景部分のクリックのみ対象・モーダル本体のクリックは含まない
    
    // --- 次へボタン（btn-next） ---
    if (e.target.closest(".btn-next")) {
      if (currentStep < 4) currentStep++;
      showStep(currentStep);
    }
      // クリックされた場所が「次へ（btn_next）」なら
      // currentStepが4より小さければ、1つ増やす
      // 増やしたcurrentStepをshowStepとして表示スライドを切り替え
    
    // --- 戻るボタン（btn-prev） ---
    if (e.target.closest(".btn-prev")) {
      if (currentStep > 1) currentStep--;
      showStep(currentStep);
    }
      // 戻る(btn_prev)の場合も、次へボタン同様に逆の処理を行う
  });

  showStep(currentStep);
    // 初期表示用（currentStep = 1）