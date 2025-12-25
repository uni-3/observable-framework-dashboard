---
theme: dashboard
title: ポケモン分析
---


```js
import {generationColors, typeColors} from "../components/color.js";

const count_pokemon_type = FileAttachment("../data/pokemon-type.csv").csv({typed: true});

const pokemon_height_weight = FileAttachment("../data/scatter-pokemon-height-weight.csv").csv({typed: true});

```

## 世代ごとのポケモンタイプ数

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

## 世代・タイプのクロス集計

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

## 高さ・重さの散布図


```js
const selectedTypes = view(Inputs.checkbox(Object.keys(typeColors), {
  label: "タイプで絞る",
  value: Object.keys(typeColors)
}));
```

```js
const filtered_pokemon_height_weight = pokemon_height_weight.filter((d) =>
  selectedTypes.includes(d.type_name)
);
```

```js
//Inputs.table(pokemon_height_weight)
```

```js
Plot.dot(filtered_pokemon_height_weight, {
    x: "height",
    y: "weight",
    fill: "type_name",
    tip: true,
    // tipのカスタム
    title: (d) => `${d.name}\nタイプ: ${d.type_names}\n高さ: ${d.height}m \n重さ: ${d.weight}kg`,
}).plot({
    grid: true,
    color: {
        domain: Object.keys(typeColors),
        range: Object.values(typeColors),
        legend: true
    },
})
```

