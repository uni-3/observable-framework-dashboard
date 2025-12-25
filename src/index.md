<div class="flex flex-col items-center text-center mt-16 mb-8 px-4">
  <h1 class="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-blue-600 to-yellow-500 py-4">
    Observable Framework Dashboard Explorer
  </h1>
</div>

```js
const pages = FileAttachment("./data/pages.json").json();
```

<ul>
${pages.map(p => html`
  <li>
    <a href="${p.path}"><strong>${p.title}</strong></a>
    <span class="text-slate-400 text-sm ml-2">(${p.path})</span>
  </li>
`)}
</ul>
