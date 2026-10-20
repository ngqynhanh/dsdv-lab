'use strict';
// Lab 4 — D3 v7 data join, transitions, keyed identity.
const DATA_URL = 'https://tungth.github.io/data/vn-provinces-data.csv';
const LOCAL_COPY = 'vn-provinces-data.csv'; // authentic copy of DATA_URL, contingency only
const INITIAL_COUNT = 20;
const DURATION = 700;

// Layout: fixed width, height derived from the number of bars.
const margin = { top: 20, right: 70, bottom: 55, left: 150 };
const width = 900, innerW = width - margin.left - margin.right;
const BAR_STEP = 24;

// ---- State -----------------------------------------------------------------
// allRecords : validated, immutable, source-file order (never sorted/mutated)
// active     : records included, in inclusion order (membership + add/remove order)
// sortMode   : presentation only; display array is a sorted COPY of active
// lastRemoved: {record, index} for Undo (one level)
let allRecords = [];
let active = [];
let sortMode = 'source';
let lastRemoved = null;

const svg = d3.select('#chart').attr('width', width);
const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
const xAxisG = g.append('g').attr('class', 'x-axis');
const xTitle = g.append('text').attr('class', 'axis-title')
  .attr('x', innerW / 2)
  .text('GRDP (GRDP-VND column, as reported; unit not stated in CSV — see NOTES.md)');
const x = d3.scaleLinear().range([0, innerW]);
const y = d3.scaleBand().padding(0.18);

const key = d => d.id; // stable identity: the CSV "ma" code, unique per province

// ---- Load, inspect, validate ----------------------------------------------
function parseDecimal(s) {
  // "34,33" -> 34.33 ; also tolerate plain "34.33"
  if (s == null) return NaN;
  const t = String(s).trim();
  if (t === '') return NaN;
  return Number(t.replace(',', '.'));
}

function validate(rows) {
  const seen = new Set(), seenName = new Set(), out = [], excluded = [];
  rows.forEach((r, i) => {
    const id = (r.ma ?? '').trim();
    const name = (r.province ?? '').trim();
    const grdp = parseDecimal(r['GRDP-VND']);
    let why = null;
    if (!id || !name) why = 'empty id/name';
    else if (!Number.isFinite(grdp) || grdp < 0) why = 'GRDP not finite/nonnegative';
    else if (seen.has(id)) why = 'duplicate id';
    else if (seenName.has(name)) why = 'duplicate name';
    if (why) { excluded.push({ row: i + 2, id, name, why }); return; }
    seen.add(id); seenName.add(name);
    out.push({ id, name, grdp, raw: r['GRDP-VND'] });
  });
  return { out, excluded };
}

async function loadRows() {
  try {
    const rows = await d3.csv(DATA_URL);
    return { rows, note: '' };
  } catch (err) {
    console.error('CSV failed from', DATA_URL, err);
    const rows = await d3.csv(LOCAL_COPY); // throws again if this also fails
    return { rows, note: `Could not load ${DATA_URL} (${err.message || err}); using the authentic local copy ${LOCAL_COPY}.` };
  }
}

loadRows().then(({ rows, note }) => {
  console.log('CSV headers:', rows.columns);
  console.table(rows.slice(0, 3));
  const { out, excluded } = validate(rows);
  console.log(`valid=${out.length}, excluded=${excluded.length}`, excluded);
  allRecords = out;
  active = allRecords.slice(0, INITIAL_COUNT);
  d3.select('#load-note').text(note);
  wireControls();
  render();
}).catch(err => {
  d3.select('#message').text(`Data failed to load: ${err.message || err}. No substitute data is shown.`);
  d3.selectAll('button, select').property('disabled', true);
});

// ---- Display order ---------------------------------------------------------
function displayRecords() {
  const copy = active.slice(); // never sort `active` or `allRecords`
  switch (sortMode) {
    case 'name': copy.sort((a, b) => a.name.localeCompare(b.name, 'vi')); break;
    case 'grdp-desc': copy.sort((a, b) => d3.descending(a.grdp, b.grdp) || d3.ascending(a.id, b.id)); break;
    case 'grdp-asc': copy.sort((a, b) => d3.ascending(a.grdp, b.grdp) || d3.ascending(a.id, b.id)); break;
    default: { // original source order
      const pos = new Map(allRecords.map((d, i) => [d.id, i]));
      copy.sort((a, b) => pos.get(a.id) - pos.get(b.id));
    }
  }
  return copy;
}

// ---- Render (single entry point for every update) -------------------------
function render() {
  const data = displayRecords();
  const innerH = data.length * BAR_STEP;

  // Scales recomputed from the displayed data; domain includes zero.
  x.domain([0, d3.max(data, d => d.grdp)]).nice();
  y.domain(data.map(key)).range([0, innerH]);

  // One named transition per render; a newer render interrupts the older one.
  const t = svg.transition('render').duration(DURATION);

  svg.transition(t).attr('height', innerH + margin.top + margin.bottom);
  xAxisG.attr('transform', `translate(0,${innerH})`)
    .transition(t).call(d3.axisBottom(x).ticks(8).tickFormat(d3.format(',.0f')));
  xTitle.transition(t).attr('y', innerH + 42);

  const flash = sel => sel
    .on('start', function () { d3.select(this).classed('moving', true); })
    .on('end interrupt', function () { d3.select(this).classed('moving', false); });

  // Bars
  g.selectAll('rect.bar').data(data, key).join(
    enter => enter.append('rect').attr('class', 'bar')
      .attr('x', 0).attr('width', 0).attr('height', y.bandwidth())
      .attr('y', d => y(d.id)).attr('opacity', 0),
    update => update,
    exit => exit.transition(t).attr('width', 0).attr('opacity', 0).remove()
  ).transition(t).call(flash)
    .attr('y', d => y(d.id)).attr('height', y.bandwidth())
    .attr('width', d => x(d.grdp)).attr('opacity', 1);

  // Province name labels (left)
  g.selectAll('text.name-label').data(data, key).join(
    enter => enter.append('text').attr('class', 'name-label').attr('x', -8)
      .attr('y', d => y(d.id) + y.bandwidth() / 2).attr('opacity', 0).text(d => d.name),
    update => update,
    exit => exit.transition(t).attr('opacity', 0).remove()
  ).transition(t).attr('y', d => y(d.id) + y.bandwidth() / 2).attr('opacity', 1);

  // Value labels (right end of each bar)
  g.selectAll('text.value-label').data(data, key).join(
    enter => enter.append('text').attr('class', 'value-label').attr('x', 6)
      .attr('y', d => y(d.id) + y.bandwidth() / 2).attr('opacity', 0),
    update => update,
    exit => exit.transition(t).attr('opacity', 0).remove()
  ).text(d => d.raw.replace(',', '.'))
    .transition(t).attr('x', d => x(d.grdp) + 6)
    .attr('y', d => y(d.id) + y.bandwidth() / 2).attr('opacity', 1);

  updateControls();
}

// ---- Controls ---------------------------------------------------------------
function updateControls() {
  d3.select('#count').text(`Showing ${active.length} of ${allRecords.length} provinces`);
  d3.select('#add-btn').property('disabled', active.length >= allRecords.length);
  d3.select('#remove-btn').property('disabled', active.length <= 1);
  d3.select('#undo-btn').property('disabled', !lastRemoved);
}

function say(msg) { d3.select('#message').text(msg); }

function addProvince() {
  const used = new Set(active.map(key));
  const next = allRecords.find(d => !used.has(d.id)); // next unused, source order
  if (!next) { say('All valid provinces are already shown.'); return; }
  active.push(next);
  say(`Added ${next.name}.`);
  render();
}

function removeProvince() {
  if (active.length <= 1) { say('At least one province must remain.'); return; }
  const index = active.length - 1;
  const record = active.pop(); // last INCLUDED record, regardless of sort
  lastRemoved = { record, index };
  say(`Removed ${record.name}.`);
  render();
}

function undoRemove() {
  if (!lastRemoved) { say('Nothing to undo.'); return; }
  const { record, index } = lastRemoved;
  lastRemoved = null; // a second Undo does nothing
  if (active.some(d => d.id === record.id)) { say(`${record.name} is already shown.`); updateControls(); return; }
  active.splice(Math.min(index, active.length), 0, record);
  say(`Restored ${record.name}.`);
  render();
}

function wireControls() {
  d3.select('#add-btn').on('click', addProvince);
  d3.select('#remove-btn').on('click', removeProvince);
  d3.select('#undo-btn').on('click', undoRemove);
  d3.select('#sort-select').on('change', function (event) {
    sortMode = event.target.value;
    render();
  });
}

// Read-only hook for manual checks in DevTools / automated tests.
window.__lab = {
  get all() { return allRecords; }, get active() { return active; },
  addProvince, removeProvince, undoRemove,
  setSort(m) { d3.select('#sort-select').property('value', m); sortMode = m; render(); }
};
