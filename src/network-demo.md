---
theme: dashboard
title: Network Graph Demo
---

# ネットワーク図のデモ 🕸️

D3.js の Force Simulation を使って、重み付きのネットワーク図を描画します。
ドラッグして動かせます！

```js
// 必要なライブラリとデータを読み込み
import {createNetworkGraph} from "./components/network.js";
const data = FileAttachment("data/network.json").json();
```

<div class="card">
${createNetworkGraph(data, {width: width, height: 600})}
</div>

