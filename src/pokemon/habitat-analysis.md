---
theme: dashboard
title: ポケモンのタイプやかたち、生息環境の分析
---

```js
const rawData = FileAttachment("../data/pokemon/habitat-shape.json").json();
```

```js
// flat Egg Groups
const flatEggData = rawData.flatMap(d =>
  d.egg_groups_ja.map(eggGroup => ({
    ...d,
    egg_group_ja: eggGroup
  }))
);

// flat types
const flatTypeData = rawData.flatMap(d =>
  Array.isArray(d.types_ja) ? d.types_ja.map(t => ({
    ...d,
    type_ja: t
  })) : []
);

// 凡例用リスト
const habitats = [...new Set(rawData.map(d => d.habitat_name_ja))].filter(d => d).sort();
const shapes = [...new Set(rawData.map(d => d.shape_name_ja))].filter(d => d).sort();
const eggGroups = [...new Set(flatEggData.map(d => d.egg_group_ja))].filter(d => d).sort();
const pokemonTypes = [...new Set(flatTypeData.map(d => d.type_ja))].filter(d => d).sort();
```


# 生息環境の関係分析

ポケモンの生息地（Habitat）に対するかたち（Shape）の分布や、タイプ、タマゴグループとの関係を可視化します。

```js
const knownHabitatCount = rawData.filter(d => d.habitat_name_ja !== '不明').length;
const unknownHabitatCount = rawData.filter(d => d.habitat_name_ja === '不明').length;
```

## 生息地とかたちの分布

生息地ごとに、どのかたちのポケモンが多いか概観します。

```js
Plot.plot({
  padding: 0,
  marginLeft: 100,
  marginBottom: 100,
  x: { label: "かたち", domain: shapes, tickRotate: -45 },
  y: { label: "生息地", domain: habitats },
  color: { scheme: "YlGnBu", opacity: 0.8, label: "ポケモン数" },
  marks: [
    Plot.cell(rawData, Plot.group({ fill: "count" }, {
      x: "shape_name_ja",
      y: "habitat_name_ja",
      inset: 0.5,
      tip: true
    })),
    Plot.text(rawData, Plot.group({ text: "count" }, {
      x: "shape_name_ja",
      y: "habitat_name_ja",
      fill: "black",
      stroke: "white",
      strokeWidth: 3,
      paintOrder: "stroke"
    }))
  ]
})
```

## タマゴグループと生息地の分布

生息地ごとに、どのタマゴグループのポケモンが多いか概観します。タマゴグループを複数もつポケモンもいるため、カウントが多くなっています。

```js
Plot.plot({
  padding: 0,
  marginLeft: 100,
  marginBottom: 100,
  x: { label: "タマゴグループ", domain: eggGroups, tickRotate: -45 },
  y: { label: "生息地", domain: habitats },
  color: { scheme: "YlGnBu", opacity: 0.8, label: "ポケモン数" },
  marks: [
    Plot.cell(flatEggData, Plot.group({ fill: "count" }, {
      x: "egg_group_ja",
      y: "habitat_name_ja",
      inset: 0.5,
      tip: true
    })),
    Plot.text(flatEggData, Plot.group({ text: "count" }, {
      x: "egg_group_ja",
      y: "habitat_name_ja",
      fill: "black",
      stroke: "white",
      strokeWidth: 3,
      paintOrder: "stroke"
    }))
  ]
})
```

## 多重対応分析 (correspondence analysis)

生息地、かたち、タマゴグループ、タイプ、そしてポケモン個体の関係性について対応分析を行い、2次元空間にマッピングしました。

### 分析に使用したデータと手法

以下の4つのカテゴリ変数を用いて、多重対応分析（MCA）を行いました。

`生息地・かたち・タマゴグループ・タイプ`

結果を可視化することで、互いに関連の強いカテゴリーがわかる。

マッピング結果上でどのようにグループ化されるかを見ることで、「環境（生息地）」と「姿（かたち）」と「分類（タマゴ・タイプ）」の関連性を把握できます。

```js
const caData = FileAttachment("../data/pokemon/correspondence-analysis.json").json();
```

```js
const showPokemon = view(Inputs.toggle({label: "ポケモン個体を表示", value: false}));
```

```js
const typeLabels = {
  "habitat": "生息地",
  "shape": "かたち",
  "egg": "タマゴグループ",
  "poke_type": "タイプ",
  "pokemon": "ポケモン"
};
const caDataJa = caData.map(d => ({
  ...d,
  type_ja: typeLabels[d.type] || d.type,
  tooltip: d.type === "pokemon" ? d.label : `${typeLabels[d.type]}: ${d.label}`
}));
```


```js
Plot.plot({
  width: 600,
  aspectRatio: 1,
  grid: true,
  x: {label: "次元 1", domain: [-2, 3]},
  y: {label: "次元 2"},
  color: {
    domain: ["生息地", "かたち", "タマゴグループ", "タイプ", "ポケモン"],
    range: ["var(--theme-foreground-focus)", "var(--theme-primary)", "#e91e63", "#ff9800", "#ccc"],
    legend: true
  },
  marks: [
    Plot.frame(),
    Plot.ruleX([0], {strokeOpacity: 0.2}),
    Plot.ruleY([0], {strokeOpacity: 0.2}),

    // Pokemon points (Toggleable)
    showPokemon ? Plot.dot(caDataJa.filter(d => d.type === "pokemon"), {
      x: "x",
      y: "y",
      r: 2,
      fill: "type_ja",
      stroke: "white",
      strokeWidth: 0.5,
      title: "tooltip",
      tip: true,
      opacity: 0.5
    }) : null,

    // Category points
    Plot.dot(caDataJa.filter(d => d.type !== "pokemon"), {
      x: "x",
      y: "y",
      r: 5,
      fill: "type_ja",
      stroke: "white",
      strokeWidth: 2,
      title: "tooltip",
      tip: true
    }),

    // Labels
    Plot.text(caDataJa.filter(d => d.type !== "pokemon"), {
      x: "x",
      y: "y",
      text: "label",
      dy: -12,
      fill: "type_ja",
      stroke: "white",
      strokeWidth: 3,
      fontWeight: "bold"
    })
  ]
})
```

軸（次元）ごとに傾向をみると、それぞれ正の方向に向かうほど、次元1は「水中」、次元2は「空中」っぽい


---

## 生データ

タイプでフィルタリングして、各ポケモンの詳細データを確認できます。

```js
const selectedTypes = view(Inputs.checkbox(pokemonTypes, {label: "タイプで絞り込み", value: pokemonTypes}));
```

```js
const filteredData = rawData.filter(d => {
  if (selectedTypes.length === 0) return true;
  return d.types_ja && d.types_ja.some(t => selectedTypes.includes(t));
});
```

<div>表示件数: <strong>${filteredData.length}</strong> / ${rawData.length}</div>

```js
Inputs.table(filteredData, {
  columns: [
    "ja_name",
    "types_ja",
    "habitat_name_ja",
    "shape_name_ja",
    "egg_groups_ja"
  ],
  header: {
    ja_name: "ポケモン名",
    types_ja: "タイプ",
    habitat_name_ja: "生息地",
    shape_name_ja: "かたち",
    egg_groups_ja: "タマゴグループ"
  },
  width: {
    types_ja: 150,
    egg_groups_ja: 180
  },
  format: {
    types_ja: d => d ? d.join(", ") : "",
    egg_groups_ja: d => d ? d.join(", ") : ""
  },
  select: false,
  sort: "ja_name",
  rows: 20
})
```
