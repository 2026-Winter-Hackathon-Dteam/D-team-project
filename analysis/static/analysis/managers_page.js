document.addEventListener('DOMContentLoaded', function() {
    renderMatrixChart();
    attachHoverSync();
});

// マトリクス上にドットを描画
function renderMatrixChart() {
    const plotArea = document.getElementById('plotArea');
    const jsonData = document.getElementById('matrix-data');
    
    if (!plotArea || !jsonData) return;

    const matrixData = JSON.parse(jsonData.textContent);
    
    // マトリクス図エリアの実寸pxサイズをHTMLから取得
    const width = plotArea.clientWidth;
    const height = plotArea.clientHeight;

    // 配列の1要素をdataとして（x:40,y:20など）,配列の順番をindexとして受け取りループ
    matrixData.forEach((data, index) => {

        // ドットにする空divにスタイルを適用し、各ドットにdata-index属性で項目番号を持たせる
        // （8件固定なのでHTMLで書いてもいいが、チーム回答0件のときにDOMに残り隠す制御が必要なためJSで描画）
        const dot = document.createElement('div');
        dot.className =
        'matrix-dot absolute w-10 h-10 bg-teamy-teal text-white rounded-full flex items-center justify-center font-bold shadow-md transition-transform duration-150 ease-out z-20';        
        dot.dataset.index = index;

        // 縦横の割合（0〜50）を、実際のグラフサイズにあわせたpx座標に変換（CSSに合わせてwidth-で反転）
        const posX = (data.x / 50) * width;
        const posY = width - ((data.y / 50) * height);

        // 座標位置にドットを配置し、自身のサイズ分を-50％ずらして中心補正
        dot.style.left = `${posX}px`;
        dot.style.top = `${posY}px`;
        dot.style.transform = 'translate(-50%, -50%)';
        
        // ドットに番号とツールチップ設定
        dot.textContent = index + 1;
        dot.title = `項目 ${index + 1}`;
        
        // 作成したドット要素をマトリクスエリアに追加して画面に表示
        plotArea.appendChild(dot);
    });
}


// リストにホバーしたら対応するドットを強調（scale版）
function attachHoverSync() {

    // 右側の項目リスト（8項目）とドットを取得
    const listItems = document.querySelectorAll('.matrix-list-item');
    const dots = document.querySelectorAll('.matrix-dot');

    // 8項目リストごとにイベントを設定
    listItems.forEach(item => {

        // リスト側が持っているdata-indexとリストを取得（どのドットと対応するか）
        const index = item.dataset.index;
        // リスト内の丸要素（番号の丸）を取得
        const circle = item.querySelector('span');

        // ----- マウスが乗ったとき -----
        item.addEventListener('mouseenter', () => {
            // 全ドットの中からindexが一致するドットだけ変更
            dots.forEach(dot => {
                if (dot.dataset.index === index) {

                    // 色の変更・ドット拡大・前面移動
                    dot.classList.remove('bg-teamy-teal');
                    dot.classList.add('bg-teamy-orange');
                    dot.style.transform = 'translate(-50%, -50%) scale(1.25)';
                    dot.style.zIndex = 1000;
                }
            });

            // 右側リストのドット強調
            circle.classList.remove('bg-teamy-teal');
            circle.classList.add('bg-teamy-orange');
            circle.style.transform = 'scale(1.1)';
        });

        // ----- マウスが離れたとき -----
        item.addEventListener('mouseleave', () => {

            // 対応するドットを元に戻す
            dots.forEach(dot => {
                if (dot.dataset.index === index) {

                    // 色・拡大・前面移動を戻す
                    dot.classList.remove('bg-teamy-orange');
                    dot.classList.add('bg-teamy-teal');
                    dot.style.transform = 'translate(-50%, -50%)';

                    // z-indexを元に戻す
                    dot.style.zIndex = 20;
                }
            });

            // リスト側の丸も元に戻す
            circle.classList.remove('bg-teamy-orange');
            circle.classList.add('bg-teamy-teal');
            circle.style.transform = 'scale(1)';
        });
    });
}


// アコーディオンの開閉で矢印回転
document.querySelectorAll('.accordion-item').forEach(item => {

    const arrow = item.querySelector('.arrow');

    item.addEventListener('toggle', () => {
        if (item.open) {
            arrow.classList.add('rotate-180');
        } else {
            arrow.classList.remove('rotate-180');
        }
    });

});