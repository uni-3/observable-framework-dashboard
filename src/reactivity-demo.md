---
theme: dashboard
title: Reactivity Demo
---

# リアクティビティの実験 🧪

これが **"State管理不要"** の世界です。
スライダーを動かしてみてください。`addEventListener` も `useState` も書いていません！

```js
// 1. Inputs (入力コンポーネント) を作る
// view(...) でラップすると、その値がリアクティブな変数になります
const radius = view(Inputs.range([10, 200], {label: "円の半径 (Radius)", step: 1, value: 50}));
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>計算結果 (ただの変数参照)</h2>
    <!-- 2. 変数 radius をただ参照するだけ。値が変わればここも勝手に書き換わります -->
    <div class="big">
      半径: ${radius} px<br>
      面積: ${Math.round(radius * radius * Math.PI).toLocaleString()} px²
    </div>
  </div>

  <div class="card">
    <h2>グラフ (Plot)</h2>
    <!-- 3. グラフの中に radius 変数を入れるだけ -->
    ${
      Plot.plot({
        width: 400,
        height: 400,
        x: {domain: [0, 400]},
        y: {domain: [0, 400]},
        marks: [
          Plot.circle([{x: 200, y: 200}], {
            r: radius, // ここ！変数を渡すだけで連動します
            fill: "var(--theme-foreground-focus)"
          }),
          Plot.text([{x: 200, y: 200}], {
            text: [`r = ${radius}`],
            fill: "white",
            fontWeight: "bold"
          })
        ]
      })
    }
  </div>
</div>

```js
// 現在の radius の値をコンソールに出すだけのブロック
// これも radius が変わるたびに再実行されます
console.log("現在の半径:", radius);
```
