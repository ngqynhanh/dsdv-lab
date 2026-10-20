# PRE-LAB 04 — D3.js Data Updates & Transitions

**International University | Data Science and Data Visualization (DSDV)**  
**Preparation for:** Lab 04 — Transition, Update, Enter & Exit  
**Estimated self-study:** **15–20 minutes**, before the lab session  
**Working mode:** individual; compare predictions with your lab partner later

## What you will learn

By the time you finish the pre-lab, you should be able to (1) distinguish *data updates* from *new or removed data*, (2) predict the effects of a *key function*, and (3) explain the role of a D3 *transition*. These are small demonstrations, **not the solution to Lab 04**.

## Setup — 2 minutes

Download the folder `prelab_demo/` and open the three `.html` files in a browser (internet is needed to load **D3 v7** from the CDN). Alternatively, start a local web server with `python -m http.server 8000` and visit `http://localhost:8000/prelab_demo/01_update_values.html` from the parent directory.

If nothing appears: check DevTools → Console and Network; confirm the `d3.min.js` script loaded. No CSV is required for the pre-lab: the examples use **synthetic teaching values**, not real Vietnamese provincial statistics.

## Demo 1 — Updating existing elements (4 minutes)

Open `prelab_demo/01_update_values.html`. Click **Change values**, then **Reset**. Compare the rectangle count and the width of each bar.

```js
const bars = plot.selectAll('rect.bar')
  .data(data, d => d.id);

bars.join('rect')
  .transition()
  .duration(700)
  .attr('width', d => x(d.value));
```

**Before clicking:** predict whether the number of rectangles changes. **After clicking:** explain why the widths changed but the number of bars did not. The code snippet shows a pattern; the real page contains all setup code.

## Demo 2 — Enter, update and exit (6 minutes)

Open `prelab_demo/02_enter_exit.html`. Click **Add item** twice, then **Remove item** twice. Watch new bars grow from zero and removed bars shrink to zero.

```js
const bars = svg.selectAll('rect.item').data(active, d => d.id);

bars.join(
  enter => enter.append('rect') /* new data → new element */,
  update => update               /* same key → reuse element */,
  exit => exit.remove()          /* missing key → remove element */
);
```

The actual demo adds transitions and attributes inside these callbacks. Answer: (1) Which action triggers `enter`? (2) Which action triggers `exit`? (3) Why must exiting elements eventually be removed from the DOM? (4) What if the key is the index rather than a stable item ID?

## Demo 3 — Sorting with stable keys (5 minutes)

Open `prelab_demo/03_sort_and_key.html`. Change sorting between **Name (A–Z)** and **Value (high–low)**.

```js
const sorted = [...data].sort((a, b) => d3.descending(a.value, b.value));
const bars = g.selectAll('rect.bar').data(sorted, d => d.id);
```

Observe that items **move** smoothly rather than behaving like different objects. The `d => d.id` function connects the same data object to its existing visual element even if the order changes. Observe the temporary highlight during the motion (`transition().on('start', ...)`, `.on('end', ...)`).

## Quick check — 3 minutes

| Question | Your answer (one sentence) |
|---|---|
| What is the difference between `enter` and `update`? | |
| What is the difference between `exit` and hiding with `opacity: 0`? | |
| Why is a stable key important when sorting? | |
| Does a transition guarantee a correct chart? Why/why not? | |

**Bring to class:** your four answers and one screenshot showing an Enter/Exit change. You will not be asked to reproduce all the source code from memory.

> **Next lab challenge:** Move from toy data to an updateable horizontal bar chart of Vietnamese provinces. Your job is to manage identity, changing scales, ordered presentation and correctness when users add/remove/sort records.

**Optional reference:** [D3](https://d3js.org/) • [D3 selections](https://d3js.org/d3-selection) • [D3 transitions](https://d3js.org/d3-transition) • *Interactive Data Visualization for the Web*, Chapter 9 (*Updates, Transitions, and Motion*). The chapter’s older event/callback syntax may differ from D3 v7.
