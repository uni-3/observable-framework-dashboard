---
theme: dashboard
title: pokemon analytics
---


```js
const count_pokemon_type = FileAttachment("data/pokemon-type.csv").csv({typed: true});

const pokemon_height_weight = FileAttachment("data/scatter_pokemon_height_weight.csv").csv({typed: true});

const pokemon_type_network = FileAttachment("data/pokemon-types-network.json").json();


const generationColors = {
  "カントー": "#ef5350",
  "ジョウト": "#ffa726",
  "ホウエン": "#66bb6a",
  "シンオウ": "#42a5f5",
  "イッシュ": "#78909c",
  "カロス": "#ab47bc",
  "アローラ": "#ffee58",
  "ガラル": "#26a69a",
  "パルデア": "#ec407a"
};

const typeColors = {
  "ノーマル": "#8A8B8B",
  "ほのお": "#E62D2D",
  "みず": "#4359FF",
  "くさ": "#50C850",
  "でんき": "#FFD700",
  "こおり": "#80D0D0",
  "かくとう": "#C03028",
  "どく": "#964096",
  "じめん": "#D8C070",
  "ひこう": "#A890F0",
  "エスパー": "#FF80B0",
  "むし": "#A8B820",
  "いわ": "#B8A038",
  "ゴースト": "#682868",
  "ドラゴン": "#78C0F0",
  "あく": "#684838",
  "はがね": "#A8A8C0",
  "フェアリー": "#EE99AC"
};
```

plot

```js
const selectedGenerations = view(Inputs.checkbox(Object.keys(generationColors), {
  label: "世代で絞る",
  value: Object.keys(generationColors)
}));
```

```js
const filtered_count_pokemon_type = count_pokemon_type.filter((d) =>
  selectedGenerations.includes(d.generation_name)
);
```


```js
Plot.waffleY(
    filtered_count_pokemon_type, {
        x: "type_name",
        y: "c",
        fill: "generation_name",
        order: Object.keys(generationColors),
        //sort: {x: null, color: "fill"},
        tip: true
    }).plot({
        marginBottom: 60,
        x: {
           tickRotate: 45,
        },
        y: {label: "カウント"},
        color: {
            domain: Object.keys(generationColors),
            range: Object.values(generationColors),
            legend: true
        },
})
```

- クロス集計

```js
Plot.plot({
  //marginTop: 60,
  marginLeft: 60,
  //height: 500, // 高さはタイプ数（18個）に合わせて調整
  padding: 0,
  x: {
    axis: "top",
    domain: Object.keys(generationColors), // 順番固定
    label: null
  },
  y: {
    label: null
  },
  color: {
    scheme: "turbo",
    opacity: 0.4,
    label: "カウント"
  },
  marks: [
    // セルの背景色
    Plot.cell(count_pokemon_type, {
      x: "generation_name",
      y: "type_name",
      fill: "c",
      fillOpacity: 0.9,
      inset: 0.7,
      tip: true
    }),
    // セル内の数値（真ん中）
    Plot.text(count_pokemon_type, {
      x: "generation_name",
      y: "type_name",
      text: "c",
      fill: "black",
      stroke: "white",
      strokeWidth: 3,
      paintOrder: "stroke",
      pointerEvents: "none"
    })
  ]
})
```

scatter plot

```js
//Inputs.table(pokemon_height_weight)
```

```js
Plot.dot(pokemon_height_weight, {
    x: "height",
    y: "weight",
    fill: "type_name",
    tip: true,
    // tipのカスタム
    title: (d) => `${d.name}\nタイプ: ${d.type_name}\n高さ: ${d.height}m \n重さ: ${d.weight}kg`,
}).plot({
    grid: true,
    color: {
        domain: Object.keys(typeColors),
        range: Object.values(typeColors),
        legend: true
    },
})
```


```js
Inputs.table(pokemon_type_network.nodes)
```

```js
Inputs.table(pokemon_type_network.links)
```

## ポケモン・タイプ共起ネットワーク (二部グラフ)

```js
const width = 800;
const height = 800;

// データをコピー
const nodes = pokemon_type_network.nodes.map(d => ({...d}));
const links = pokemon_type_network.links.map(d => ({...d}));

// type nodeの大きさ制御
const radiusScale = d3.scaleSqrt()
    .domain([0, d3.max(nodes.filter(d => d.group === 1), d => d.count)])
    .range([6, 20]);

const getRadius = d => d.group === 1 ? radiusScale(d.count) : 3;

const simulation = d3.forceSimulation(nodes)
    // 速度の減衰 (0〜1)
    .velocityDecay(0.6)
    // エネルギーの減衰速度。シミュレーションが「安定（停止）」に向かう速さ
    .alphaDecay(0.02)
    // リンク: ポケモンノードをタイプノードにしっかり追従
    .force("link", d3.forceLink(links).id(d => d.id).distance(20).strength(1))
    // 反発力: タイプノード(group:1)は強く反発し、ポケモン(group:2)は弱く反発させる
    .force("charge", d3.forceManyBody().strength(d => d.group === 1 ? -1000 : -10))
    // 中央へ引き寄せる力
    .force("x", d3.forceX(width / 2).strength(0.1))
    .force("y", d3.forceY(height / 2).strength(0.1))
    // 衝突したら動く
    .force("collision", d3.forceCollide().radius(d => getRadius(d) + (d.group === 1 ? 30 : 0)))
    .stop(); // 自動実行を一旦止める

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
    .attr("stroke-opacity", 0.2)
    .attr("pointer-events", "none")
  .selectAll("line")
  .data(links)
  .join("line")
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

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

// タイプノード group = 1
node.filter(d => d.group === 1)
  .append("circle")
    .attr("r", d => getRadius(d))
    .attr("fill", d => typeColors[d.id] || "#ccc")
    .attr("stroke", "#fff")
    .attr("stroke-width", 2);

// ポケモンノード group = 2
node.filter(d => d.group === 2)
  .append("rect")
    .attr("width", 4)
    .attr("height", 4)
    .attr("x", -2)
    .attr("y", -2)
    .attr("fill", "#94a3b8")
    .attr("fill-opacity", 0.3)
    .attr("stroke", "none");

// マウスイベント
node
    .on("mouseover", (event, d) => {
      tooltip.style("visibility", "visible");
      const content = d.group === 1
        ? `<strong>タイプ: ${d.id}</strong><br>所属数: ${d.count}`
        : `<strong>名前: ${d.id}</strong><br>タイプ: ${(d.types || []).join(", ")}`;
      tooltip.html(content);

      d3.select(event.currentTarget).selectAll("circle, rect").attr("stroke", "#ccc").attr("fill-opacity", 1);
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
      d3.select(event.currentTarget).select("rect").attr("stroke", "none").attr("fill-opacity", 0.4);
    });

// ラベル (タイプ名のみ)
const label = svg.append("g")
    .attr("pointer-events", "none")
  .selectAll("text")
  .data(nodes.filter(d => d.group === 1))
  .join("text")
    .text(d => d.id)
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
