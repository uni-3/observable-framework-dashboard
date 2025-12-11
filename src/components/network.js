//import * as d3 from "npm:d3";
import * as d3 from "d3";

export function createNetworkGraph(data, {width = 600, height = 600} = {}) {
  // 元データを破壊しないようにコピー
  const links = data.links.map(d => ({...d}));
  const nodes = data.nodes.map(d => ({...d}));

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
      .attr("r", 8) // 半径
      .attr("fill", d => color(d.group))
      .call(drag(simulation)); // ドラッグ操作を有効化

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
