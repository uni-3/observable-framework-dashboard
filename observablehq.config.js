// See https://observablehq.com/framework/config for documentation.
export default {
  title: "Observable Framework Dashboard",

  // Content to add to the head of the page, e.g. for a favicon:
  head: `
    <link rel="icon" href="observable.png" type="image/png" sizes="32x32">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/style.css">
  `,

  // The path to the source root.
  root: "src",

  // Some additional configuration options and their defaults:
  theme: "slate",
  // header: "", // what to show in the header (HTML)
  // footer: "Built with Observable.", // what to show in the footer (HTML)
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs
  interpreters: {
    ".py": ["uv", "run"],
  },
};
