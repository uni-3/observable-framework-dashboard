---
theme: dashboard
title: DuckPGQ Node.js Loader
---

# DuckPGQ + Node.js Loader 🦆🚀

ビルド時 (Node.js) にDuckDB + DuckPGQを使ってグラフデータを生成し、それをここで可視化しています。
ブラウザでは計算せず、JSONを表示するだけです。

```js
// データローダーが生成したJSONを読み込む
const data = FileAttachment("data/graph-analytics.json").json();
```

```js
import {createNetworkGraph, createCircularGraph} from "./components/network.js";
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Force Layout</h3>
    ${createNetworkGraph(data, {width: width, height: 500})}
  </div>
  <div class="card">
    <h3>Circular Layout</h3>
    ${createCircularGraph(data, {width: width, height: 500})}
  </div>
</div>

### 生データ (JSON)
```js
display(data);
```
