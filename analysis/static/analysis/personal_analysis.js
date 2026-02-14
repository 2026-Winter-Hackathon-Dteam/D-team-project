document.addEventListener('DOMContentLoaded', () => {
    // --- BEからの辞書データをJSオブジェクトとして取得 ---
    const adviceData = JSON.parse(document.getElementById('personal-advice-data').textContent);
    console.log("取り出したデータ:", adviceData);
    // devツールで確認用

    // --- 1. 要素の取得 ---
    const btnMe = document.getElementById('tab-me-btn');
    const btnTeam = document.getElementById('tab-team-btn');
    const contentMe = document.getElementById('content-me');
    const contentTeam = document.getElementById('content-team');
    const tip = document.getElementById('hover-tooltip');
    const allRows = document.querySelectorAll('.analysis-row');

    // --- 2. ピンの配置 ---
    const positionPins = () => {
        const pins = document.querySelectorAll('.user-pin, .team-pin');
        pins.forEach(pin => {
            // 画面上の自分とチームのピンを取得して動きを指示
            const score = pin.getAttribute('data-score');
            if (score !== null && score !== "") {
                // HTMLのdata-score属性から値を取り出す スコアが空ならスキップ
                pin.style.left = `${score}%`;
                pin.style.transform = "translateX(-50%)";
                // スコア値をleft○％のスタイル指定することでピンを配置
                // -50%でピン自身の半分の大きさだけ左に動かして真ん中補正
            }
        });
    };

    // --- 3. タブ切り替えロジック ---
    const switchTab = (target) => {
        if (target === 'team') {
            contentMe.classList.add('hidden');
            contentTeam.classList.remove('hidden');
            // team選択時にhiddenの付け外し
            btnTeam.className = "px-6 py-2 text-teamy-teal font-bold border-b-2 border-teamy-teal -mb-[1px]";
            btnMe.className = "px-6 py-2 text-gray-400 font-bold";
            // 選択タブ/非選択タブのデザイン切り替え

            // タブ表示された瞬間にピンを再配置
            positionPins();
        } else {
            contentTeam.classList.add('hidden');
            contentMe.classList.remove('hidden');
            btnMe.className = "px-6 py-2 text-teamy-teal font-bold border-b-2 border-teamy-teal -mb-[1px]";
            btnTeam.className = "px-6 py-2 text-gray-400 font-bold";
        }
    };

    // --- 4. ツールチップ ---
    allRows.forEach(row => {
        // ホバー時：表示
        row.onmouseenter = () => {
            tip.style.opacity = "0.8";
        };
        // マウスが離れた時：非表示
        row.onmouseleave = () => {
            tip.style.opacity = "0";
            tip.style.left = "-1000px"; // 念のため画面外へ
        };
        // チップをマウスに追従
        row.onmousemove = (e) => {
            // clientX, clientY は画面上のポインタの座標
            // +15 でポインタの少し右下に表示
            tip.style.left = (e.clientX + 15) + 'px';
            tip.style.top = (e.clientY + 15) + 'px';
        };
        // クリックしたらメッセージを消す
        row.onclick = () => {
            tip.style.opacity = "0";
        };
    });

    // --- 5. ページ遷移時の初期実行 ---
    const urlParams = new URLSearchParams(window.location.search);
    const firstTab = urlParams.get('tab');
    // URL末尾「?tab=team」があるかを確認し、あれば格納、なければfirstTabは空っぽ
    switchTab(firstTab === 'team' ? 'team' : 'me');
    // 判定：teamだったらteamタブを開く ちがったらmeタブを開く（ ?：を使ったif文と同じ処理）

    btnMe.onclick = () => switchTab('me');
    btnTeam.onclick = () => switchTab('team');
    // アロー関数によるクリック待ち
    
    positionPins(); // すべてのピンを配置する
});