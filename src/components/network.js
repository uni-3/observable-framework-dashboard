//import * as d3 from "npm:d3";
import * as d3 from "d3";

export function createNetworkGraph(data, {width = 600, height = 600} = {}) {
  // 元データを破壊しないようにコピー
  const links = data.links.map(d => ({...d}));
  const nodes = data.nodes.map(d => ({...d}));

  // 次数 (degree) を計算
  const nodeById = new Map(nodes.map(d => [d.id, d]));
  nodes.forEach(n => n.degree = 0);
  links.forEach(l => {
    // ForceSimulationがsource/targetをオブジェクトに置換する前はID文字列かもしれないので注意が必要だが
    // ここでは初期状態として文字列IDを想定
    if (nodeById.has(l.source)) nodeById.get(l.source).degree++;
    if (nodeById.has(l.target)) nodeById.get(l.target).degree++;
  });

  // カラーパレット
  const color = d3.scaleOrdinal(d3.schemeTableau10);

  // シミュレーションの設定
  const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100)) // リンクの長さ
      .force("charge", d3.forceManyBody().strength(-400)) // 反発力
      .force("center", d3.forceCenter(width / 2, height / 2)); // 重心

  // SVGコンテナの作成
  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "max-width: 100%; height: auto;");

  // リンク（線）の描画
  const link = svg.append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(links)
    .join("line")
      .attr("stroke-width", d => Math.sqrt(d.value) * 2); // 重みによって太さを変える

  // ノード（円）の描画
  const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("r", d => d.degree) // 半径を次数に比例させる(ベース小さく)
      .attr("fill", d => color(d.group))
      .call(drag(simulation)); // ドラッグ操作を有効化

  // ツールチップ (title属性)
  node.append("title")
      .text(d => `ID: ${d.id}\nConnections: ${d.degree}`);

  // ノードごとのラベル
  const text = svg.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
      .text(d => d.id)
      .attr("font-size", 10)
      .attr("dx", 12)
      .attr("dy", 4)
      .attr("fill", "currentColor"); // テーマに合わせて色が変わるように

  // ラベルにもツールチップを追加
  text.append("title")
      .text(d => `ID: ${d.id}\nConnections: ${d.degree}`);

  // タイマーごとに位置を更新
  simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    text
        .attr("x", d => d.x)
        .attr("y", d => d.y);
  });

  // ドラッグ操作の実装
  function drag(simulation) {
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
  }

  return svg.node();
}

// 円形配置 (Circular Layout)
export function createCircularGraph(data, {width = 600, height = 600} = {}) {
  // 次数を計算してノードに追加
  // ForceGraphと同じデータセットを参照してしまうとsimulationでx,yが書き換わっているのでコピー
  const nodesRaw = data.nodes.map(d => ({...d}));
  const nodeMap = new Map(nodesRaw.map(d => [d.id, d]));

  nodesRaw.forEach(n => n.degree = 0);
  data.links.forEach(l => {
     // linksのsource/targetは文字列のまま
     if (nodeMap.has(l.source)) nodeMap.get(l.source).degree++;
     if (nodeMap.has(l.target)) nodeMap.get(l.target).degree++;
  });

  const radius = Math.min(width, height) / 2 * 0.8;
  const nodes = nodesRaw.map((d, i) => {
    const angle = (i / nodesRaw.length) * 2 * Math.PI;
    return {
      ...d,
      x: (width / 2) + radius * Math.cos(angle - Math.PI / 2),
      y: (height / 2) + radius * Math.sin(angle - Math.PI / 2)
    };
  });

  const nodeById = new Map(nodes.map(d => [d.id, d]));
  const links = data.links.map(d => ({
    ...d,
    source: nodeById.get(d.source),
    target: nodeById.get(d.target)
  }));

  const color = d3.scaleOrdinal(d3.schemeTableau10);

  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

  // リンク
  svg.append("g")
      .attr("fill", "none")
      .attr("stroke-opacity", 0.4)
    .selectAll("path")
    .data(links)
    .join("path")
      .style("mix-blend-mode", "multiply")
      .attr("d", d => {
          return `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`;
      })
      .attr("stroke", d => color(d.source.group))
      .attr("stroke-width", 1);

  // ノード
  const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("cx", d => d.x)
      .attr("cy", d => d.y)
      .attr("r", d => d.degree) // 半径を次数に比例させる(強調)
      .attr("fill", d => color(d.group))

  // ツールチップ
  node.append("title")
      .text(d => `ID: ${d.id}\nConnections: ${d.degree}`);

  // ラベル
  svg.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
      .attr("x", d => d.x)
      .attr("y", d => d.y)
      .attr("dy", "0.31em")
      .attr("dx", d => d.x < width / 2 ? -10 : 10)
      .attr("text-anchor", d => d.x < width / 2 ? "end" : "start")
      .text(d => d.id)
      .clone(true).lower() // 白い縁取りを追加して読みやすく
        .attr("fill", "none")
        .attr("stroke", "white")
        .attr("stroke-width", 3);

    // ラベルにもツールチップを追加
    svg.select("g:last-child").selectAll("text") // 最後に追加したg(テキスト)を選択
        .append("title")
        .text(d => `ID: ${d.id}\nConnections: ${d.degree}`);

  return svg.node();
}
