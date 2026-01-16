---
theme: dashboard
title: ポケモンのタイプやかたち、環境適応の分析
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


# 環境適応の分析

ポケモンの生息地（Habitat）に対するかたち（Shape）の分布や、タイプ、タマゴグループとの関係を可視化します。

<div>分析対象データ数: <strong>${rawData.length}</strong> (生息地・かたち・タマゴグループ完備)</div>

## 1. 生息地とかたちのヒートマップ (Habitat vs Shape)

どの生息地に、どのようなかたちのポケモンが多いかを概観します。どこに住んでいるか

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


## 2. 多重対応分析 (Habitat, Shape, Egg Group, Type)

生息地、かたち、タマゴグループ、タイプ、そしてポケモン個体の関係性を2次元マップに可視化（多重対応分析）します。

### 分析に使用したデータと手法

以下の4つのカテゴリー変数（カラム）を用いて、多重対応分析（MCA）を行いました。

1. 生息地 (`habitat_name_ja`)
2. かたち (`shape_name_ja`)
3. タマゴグループ (`egg_groups_ja`)
4. タイプ (`types_ja`)

これらを2次元空間にマッピングし、互いに関連の強いカテゴリーが近くに配置されるように可視化しています。

これらが地図上でどのようにグループ化されるかを見ることで、「環境（生息地）」と「姿（かたち）」と「分類（タマゴ・タイプ）」の複雑な絡み合いを直感的に把握できます。

```js
const caData = FileAttachment("../data/pokemon/correspondence-analysis.json").json();
```

```js
const showPokemon = view(Inputs.toggle({label: "ポケモン個体を表示", value: false}));
```

```js
Plot.plot({
  width: 600,
  aspectRatio: 1,
  grid: true,
  x: {label: "Dimension 1", domain: [-2, 3]}, // Auto domain is fine usually, but fixed keeps stability
  y: {label: "Dimension 2"},
  color: {
    domain: ["habitat", "shape", "egg", "poke_type", "pokemon"],
    range: ["var(--theme-foreground-focus)", "var(--theme-primary)", "#e91e63", "#ff9800", "#ccc"],
    legend: true
  },
  marks: [
    Plot.frame(),
    Plot.ruleX([0], {strokeOpacity: 0.2}),
    Plot.ruleY([0], {strokeOpacity: 0.2}),

    // Pokemon points (Toggleable)
    showPokemon ? Plot.dot(caData.filter(d => d.type === "pokemon"), {
      x: "x",
      y: "y",
      r: 2,
      fill: "type", // Use 'type' column which has value 'pokemon'
      stroke: "white",
      strokeWidth: 0.5,
      title: "label",
      tip: true,
      opacity: 0.5
    }) : null,

    // Category points
    Plot.dot(caData.filter(d => d.type !== "pokemon"), {
      x: "x",
      y: "y",
      r: 5,
      fill: "type",
      stroke: "white",
      strokeWidth: 2,
      title: "label",
      tip: true
    }),

    // Labels
    Plot.text(caData.filter(d => d.type !== "pokemon"), {
      x: "x",
      y: "y",
      text: "label",
      dy: -12,
      fill: "type",
      stroke: "white",
      strokeWidth: 3,
      fontWeight: "bold"
    })
  ]
})
```

> **読み方**:
> - **近くにあるカテゴリー**: 互いに関連が強い（例：「みずべ」と「さかな」が近くにある場合、水辺には魚型が多い）。
> - **中心から遠い**: 特徴が際立っている。中心に近いほど平均的。
