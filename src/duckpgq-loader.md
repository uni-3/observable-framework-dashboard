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
import {createNetworkGraph} from "./components/network.js";
```

<div class="card">
  ${createNetworkGraph(data, {width: width, height: 500})}
</div>

### 生データ (JSON)
```js
display(data);
```
