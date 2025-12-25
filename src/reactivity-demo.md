---
theme: dashboard
title: Reactivity Demo
---

# リアクティビティの確認

スライダーを動かすとカード内の数値が変わる


```js
const radius = view(Inputs.range([10, 150], {label: "円の半径 (Radius)", step: 1, value: 50}));
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>計算結果</h2>
    <div class="big">
      半径: ${radius} px<br>
      面積: ${Math.round(radius * radius * Math.PI).toLocaleString()} px²
    </div>
  </div>

  <div class="card">
    <h2>円の描画 半径: ${radius}</h2>
    ${
      resize((width) => Plot.plot({
        width,
        height: 400,
        x: {domain: [0, 400], axis: null},
        y: {domain: [0, 400], axis: null},
        marks: [
          Plot.dot([{x: 200, y: 200}], {
            x: "x",
            y: "y",
            r: radius,
            fill: "skyblue",
            fillOpacity: 0.5
          })
        ]
      }))
    }
  </div>
</div>


### コード

以下のようにradiusを定義することで

````
```js
const radius = view(Inputs.range([10, 150], {label: "円の半径 (Radius)", step: 1, value: 50}));
```
````

html内で参照でき、値の変更も反映される

````
```html
  <div class="card">
    <h2>計算結果</h2>
    <div class="big">
      半径: ${radius} px<br>
      面積: ${Math.round(radius * radius * Math.PI).toLocaleString()} px²
    </div>
  </div>
```
````
