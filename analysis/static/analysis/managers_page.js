document.addEventListener('DOMContentLoaded', function() {
    renderMatrixChart();
});

//  *チームの価値観マップ（マトリクス）を描画
function renderMatrixChart() {
    const plotArea = document.getElementById('plotArea');
    const jsonData = document.getElementById('matrix-data');
    
    if (!plotArea || !jsonData) return;

    // JSONデータを取得
    const matrixData = JSON.parse(jsonData.textContent);
    
    // プロットエリアのサイズ取得
    const width = plotArea.clientWidth;
    const height = plotArea.clientHeight;

    // データの正規化（max_diffとstdを座標に変換）
    // max_diff(x軸): 0〜100 を想定
    // std(y軸): 0〜50 を想定 (ばらつきなのでxより範囲が狭いことが多い)
    
    matrixData.forEach((data, index) => {
        const dot = document.createElement('div');
        dot.className = 'absolute w-10 h-10 bg-teamy-teal text-white rounded-full flex items-center justify-center font-bold shadow-lg border-2 border-white transition-transform hover:scale-110 z-20';
        
        // 座標計算 (左下が 0,0 の想定)
        // x: 最大差 (右に行くほど大きい)
        // y: ばらつき (上に行くほど大きい)
        const posX = (data.x / 100) * width;
        const posY = height - ((data.y / 50) * height); // Y軸は上が0なので引き算

        dot.style.left = `${posX}px`;
        dot.style.top = `${posY}px`;
        dot.style.transform = 'translate(-50%, -50%)'; // 中心を合わせる
        
        dot.textContent = index + 1; // 1〜8の番号
        
        // ツールチップ（ホバー時に項目名などを出す場合用）
        dot.title = `項目 ${index + 1}`;
        
        plotArea.appendChild(dot);
    });
}

//  アコーディオンの開閉
function toggleAccordion(contentId, button) {
    const content = document.getElementById(contentId);
    const icon = button.querySelector('svg');

    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        if (icon) icon.classList.add('rotate-180');
    } else {
        content.classList.add('hidden');
        if (icon) icon.classList.remove('rotate-180');
    }
}