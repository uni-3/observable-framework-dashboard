---
theme: dashboard
title: pokemon analytics
---


```js
const count_pokemon_type = FileAttachment("data/pokemon-type.csv").csv({typed: true});

const pokemon_height_weight = FileAttachment("data/scatter_pokemon_height_weight.csv").csv({typed: true});

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
