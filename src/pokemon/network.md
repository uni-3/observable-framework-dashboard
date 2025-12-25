---
theme: dashboard
title: ポケモンタイプネットワーク
---

```js
import {generationColors, typeColors} from "../components/color.js";

const pokemon_network = FileAttachment("../data/pokemon-network.json").json();
```

```js
const totalPokemon = pokemon_network.pokemon_nodes.length;
const singleTypeCount = pokemon_network.pokemon_nodes.filter(d => d.types.length === 1).length;
const multiTypeCount = totalPokemon - singleTypeCount;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>全ポケモン数</h2>
    <span class="big">${totalPokemon}</span>
  </div>
  <div class="card">
    <h2>単タイプ</h2>
    <span class="big">${singleTypeCount}</span>
    <span class="muted">(${((singleTypeCount / totalPokemon) * 100).toFixed(1)}%)</span>
  </div>
  <div class="card">
    <h2>複タイプ</h2>
    <span class="big">${multiTypeCount}</span>
    <span class="muted">(${((multiTypeCount / totalPokemon) * 100).toFixed(1)}%)</span>
  </div>
</div>


## ポケモンタイプ共起ネットワーク

```js
const width = 800;
const height = 800;

const nodes = pokemon_network.type_nodes.map(d => ({...d}));
const links = pokemon_network.co_links.map(d => ({...d}));

// type nodeの大きさ制御
const radiusScale = d3.scaleSqrt()
    .domain([0, d3.max(nodes, d => d.total_count)])
    .range([8, 25]);

const getRadius = d => radiusScale(d.total_count);

// リンクの太さ制御 (共起数)
const linkWidthScale = d3.scaleLinear()
    .domain([0, d3.max(links, d => d.value)])
    .range([1, 15]);

const simulation = d3.forceSimulation(nodes)
    .velocityDecay(0.3)
    .alphaDecay(0.02)
    .force("link", d3.forceLink(links).id(d => d.type_name).distance(250).strength(0.5))
    .force("charge", d3.forceManyBody().strength(-3000))
    .force("x", d3.forceX(width / 2).strength(0.05))
    .force("y", d3.forceY(height / 2).strength(0.05))
    .force("collision", d3.forceCollide().radius(d => getRadius(d) + 10))
    .stop();

// 配置が定まってから描画したいので事前に計算する 300回ループ
for (let i = 0; i < 300; ++i) simulation.tick();

const container = d3.create("div").style("position", "relative");

const svg = container.append("svg")
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto; background: var(--theme-background-alt); border-radius: 8px;");

// カスタム・ツールチップ
const tooltip = container.append("div")
    .style("position", "absolute")
    .style("visibility", "hidden")
    .style("background", "rgba(0,0,0,0.8)")
    .style("color", "#fff")
    .style("padding", "8px 12px")
    .style("border-radius", "4px")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .style("z-index", "10")
    .style("box-shadow", "0 4px 6px rgba(0,0,0,0.1)");

// エッジ
const link = svg.append("g")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.5)
  .selectAll("line")
  .data(links)
  .join("line")
    .attr("stroke-width", d => linkWidthScale(d.value))
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y)
    .attr("cursor", "pointer")
    .attr("pointer-events", "stroke");

// エッジのマウスイベント
link
    .on("mouseover", (event, d) => {
      tooltip.style("visibility", "visible");
      const content = `
        <strong>タイプ: ${d.source.type_name} ・ ${d.target.type_name}</strong><br>
        数: ${d.value}
      `;
      tooltip.html(content);
      d3.select(event.currentTarget)
        .attr("stroke", "#666")
        .attr("stroke-opacity", 1);
    })
    .on("mousemove", (event) => {
      const [x, y] = d3.pointer(event, container.node());
      tooltip
        .style("top", (y + 10) + "px")
        .style("left", (x + 10) + "px");
    })
    .on("mouseout", (event) => {
      tooltip.style("visibility", "hidden");
      d3.select(event.currentTarget)
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.5);
    });

// ノード
const node = svg.append("g")
  .selectAll("g")
  .data(nodes)
  .join("g")
    .attr("transform", d => `translate(${d.x},${d.y})`)
    .attr("cursor", "pointer")
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

// タイプノード
node.append("circle")
    .attr("r", d => getRadius(d))
    .attr("fill", d => typeColors[d.type_name] || "#ccc")
    .attr("stroke", "#fff")
    .attr("stroke-width", 2);

// マウスイベント
node
    .on("mouseover", (event, d) => {
      tooltip.style("visibility", "visible");
      const content = `
        <strong>タイプ: ${d.type_name}</strong><br>
        合計: ${d.total_count}<br>
        単タイプ数: ${d.single_type_count}<br>
        単タイプ率: ${(d.single_type_rate * 100).toFixed(1)}%<br>
        次数中心性: ${d.degree_centrality.toFixed(3)}
      `;
      tooltip.html(content);
      d3.select(event.currentTarget).select("circle").attr("stroke", "#ccc");
    })
    .on("mousemove", (event) => {
      const [x, y] = d3.pointer(event, container.node());
      tooltip
        .style("top", (y + 10) + "px")
        .style("left", (x + 10) + "px");
    })
    .on("mouseout", (event, d) => {
      tooltip.style("visibility", "hidden");
      d3.select(event.currentTarget).select("circle").attr("stroke", "#fff");
    });

// ラベル (タイプ名のみ)
const label = svg.append("g")
    .attr("pointer-events", "none")
  .selectAll("text")
  .data(nodes.filter(d => d.group === 1))
  .join("text")
    .text(d => d.type_name)
    .attr("x", d => d.x)
    .attr("y", d => d.y)
    .attr("font-size", "14px")
    .attr("font-weight", "bold")
    .attr("dx", 10)
    .attr("dy", 5)
    .attr("fill", "currentColor")
    .attr("stroke", "var(--theme-background)")
    .attr("stroke-width", 3)
    .attr("paint-order", "stroke");

simulation.on("tick", () => {
  link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

  node
      .attr("transform", d => `translate(${d.x},${d.y})`);

  label
      .attr("x", d => d.x)
      .attr("y", d => d.y);
});

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

invalidation.then(() => simulation.stop());

display(container.node());
```


## ポケモンタイプ共起ネットワーク。ポケモンノードも描画した版

```js
const bipartite_width = 800;
const bipartite_height = 800;

// データを結合 (タイプノード + ポケモンノード)
// ゴーストがtype pokemonで重複するので、uidにprefixをつけている
const bipartite_nodes = [
  ...pokemon_network.type_nodes.map(d => ({...d, group: 1, uid: `type:${d.type_name}`})),
  ...pokemon_network.pokemon_nodes.map(d => ({...d, group: 2, uid: `pokemon:${d.name}`}))
];
const bipartite_links = pokemon_network.bipartite_links.map(d => ({
  source: `pokemon:${d.source}`,
  target: `type:${d.target}`
}));

// type nodeの位置
const b_radiusScale = d3.scaleSqrt()
    .domain([0, d3.max(pokemon_network.type_nodes, d => d.total_count)])
    .range([6, 20]);

const getBipartiteRadius = d => d.group === 1 ? b_radiusScale(d.total_count) : 3;

const b_simulation = d3.forceSimulation(bipartite_nodes)
    .velocityDecay(0.6)
    .alphaDecay(0.02)
    .force("link", d3.forceLink(bipartite_links).id(d => d.uid).distance(30).strength(1))
    .force("charge", d3.forceManyBody().strength(d => d.group === 1 ? -1000 : -20))
    .force("x", d3.forceX(bipartite_width / 2).strength(0.1))
    .force("y", d3.forceY(bipartite_height / 2).strength(0.1))
    .force("collision", d3.forceCollide().radius(d => getBipartiteRadius(d) + (d.group === 1 ? 30 : 2)))
    .stop();

for (let i = 0; i < 300; ++i) b_simulation.tick();

const b_container = d3.create("div").style("position", "relative");

const b_svg = b_container.append("svg")
    .attr("viewBox", [0, 0, bipartite_width, bipartite_height])
    .attr("style", "max-width: 100%; height: auto; background: var(--theme-background-alt); border-radius: 8px;");

const b_tooltip = b_container.append("div")
    .style("position", "absolute")
    .style("visibility", "hidden")
    .style("background", "rgba(0,0,0,0.8)")
    .style("color", "#fff")
    .style("padding", "8px 12px")
    .style("border-radius", "4px")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .style("z-index", "10")
    .style("box-shadow", "0 4px 6px rgba(0,0,0,0.1)");

const b_link = b_svg.append("g")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.1)
    .attr("pointer-events", "none")
  .selectAll("line")
  .data(bipartite_links)
  .join("line")
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

const b_node = b_svg.append("g")
  .selectAll("g")
  .data(bipartite_nodes)
  .join("g")
    .attr("transform", d => `translate(${d.x},${d.y})`)
    .attr("cursor", "pointer")
    .call(d3.drag()
        .on("start", (event, d) => {
          if (!event.active) b_simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) b_simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

b_node.filter(d => d.group === 1)
  .append("circle")
    .attr("r", d => getBipartiteRadius(d))
    .attr("fill", d => typeColors[d.type_name] || "#ccc")
    .attr("stroke", "#fff")
    .attr("stroke-width", 2);

b_node.filter(d => d.group === 2)
  .append("rect")
    .attr("width", 4)
    .attr("height", 4)
    .attr("x", -2)
    .attr("y", -2)
    .attr("fill", "#94a3b8")
    .attr("fill-opacity", 0.3)
    .attr("stroke", "none");

b_node
    .on("mouseover", (event, d) => {
      b_tooltip.style("visibility", "visible");
      const content = d.group === 1
        ? `<strong>タイプ: ${d.type_name}</strong><br>合計: ${d.total_count}`
        : `<strong>名前: ${d.name}</strong><br>タイプ: ${(d.types || []).join(", ")}`;
      b_tooltip.html(content);
      d3.select(event.currentTarget).selectAll("circle, rect").attr("stroke", "#ccc").attr("fill-opacity", 1);
    })
    .on("mousemove", (event) => {
      const [x, y] = d3.pointer(event, b_container.node());
      b_tooltip
        .style("top", (y + 10) + "px")
        .style("left", (x + 10) + "px");
    })
    .on("mouseout", (event, d) => {
      b_tooltip.style("visibility", "hidden");
      d3.select(event.currentTarget).select("circle").attr("stroke", "#fff");
      d3.select(event.currentTarget).select("rect").attr("stroke", "none").attr("fill-opacity", 0.4);
    });

const b_label = b_svg.append("g")
    .attr("pointer-events", "none")
  .selectAll("text")
  .data(bipartite_nodes.filter(d => d.group === 1))
  .join("text")
    .text(d => d.type_name)
    .attr("x", d => d.x)
    .attr("y", d => d.y)
    .attr("font-size", "12px")
    .attr("font-weight", "bold")
    .attr("dx", 10)
    .attr("dy", 5)
    .attr("fill", "currentColor")
    .attr("stroke", "var(--theme-background)")
    .attr("stroke-width", 2)
    .attr("paint-order", "stroke");

b_simulation.on("tick", () => {
  b_link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

  b_node
      .attr("transform", d => `translate(${d.x},${d.y})`);

  b_label
      .attr("x", d => d.x)
      .attr("y", d => d.y);
});

display(b_container.node());
```



## 数値データ

グラフの描画に用いたタイプ別の集計指標です。

```js
Inputs.table(pokemon_network.type_nodes, {
  select: false,
  columns: [
    "type_name",
    "total_count",
    "single_type_count",
    "single_type_rate",
    "degree_centrality",
    // "eigenvector_centrality"
  ],
})
```


#### ネットワーク指標の定義

- **次数中心性 (Degree Centrality)**: ノードが持つエッジ（直接つながっている他のタイプの数） ${tex `deg(v)`} を、自分以外の全ノード数 ${tex `n-1`} で割ったもの。どれだけ多くの異なるタイプとの組み合わせがあるかを示します。範囲は0〜1で表され、例えば**1.0 の場合は自分以外の全タイプ（17種類）との組み合わせが存在すること**を意味します。

```tex
C_{degree}(v) = \frac{deg(v)}{n-1}
```

#### 複タイプ共起数

タイプの組み合わせを持つポケモンが何匹いるかを示します。

```js
Inputs.table(pokemon_network.co_links, {select: false, sort: "value", reverse: true})
```
