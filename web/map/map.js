/* Event ideology map — consumes the GeoJSON produced by
 * notebooks/07_event_mapping.ipynb. All analysis lives in Python; this file
 * only filters, aggregates per location, and styles.
 *
 * MODE:
 *   "aggregate" (default, PUBLIC) — loads events_aggregated.geojson, which holds
 *      sufficient statistics per (location x year x size). No per-event rows,
 *      no individual data. This is what ships to GitHub.
 *   "per-event" (LOCAL dev only) — loads events.geojson (gitignored) for
 *      developing the hover-popup distribution. Keeps per-event detail in memory.
 */
const MODE = "aggregate";
const DATA_BASE = "../../data/map";
const DATA_FILE = MODE === "aggregate" ? "events_aggregated.geojson" : "events.geojson";

const YEARS = ["All years", "2013-2014", "2014-2015", "2015-2016", "2016-2017"];
const SIZES = ["All", "Small", "Medium"];

let FEATURES = [];     // raw features from the contract (cells or events)
let PARAMS = null;     // color_params.json
let GROUPS_BY_ID = {}; // per-event mode only: location_id -> events (for future popup)
let filterYear = "All years";
let filterSize = "All";

// ---- color: mirrors src/event_map.py exactly, using the pinned params ----
function lerp(a, b, t) { return [a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t]; }
function bivariateColor(mean, std) {
  const { left_rgb, center_rgb, right_rgb, gray_rgb, graying_cap, s_ref } = PARAMS;
  let base = mean < 0 ? lerp(center_rgb, left_rgb, Math.min(-mean, 1))
                      : lerp(center_rgb, right_rgb, Math.min(mean, 1));
  const g = s_ref > 0 ? Math.min(std / s_ref, 1) * graying_cap : 0;
  const c = lerp(base, gray_rgb, g);
  return `rgb(${Math.round(c[0])},${Math.round(c[1])},${Math.round(c[2])})`;
}

function passesFilter(p) {
  if (filterYear !== "All years" && p.year !== filterYear) return false;
  if (filterSize !== "All" && p.size.toLowerCase() !== filterSize.toLowerCase()) return false;
  return true;
}

// Build the per-location render feature from accumulated sufficient statistics.
function makeFeature(coords, name, lid, n_events, total_att, w, wx, wxx, wp) {
  const mean = wx / w;
  const std = Math.sqrt(Math.max(wxx / w - mean * mean, 0));
  const pct = wp / w;
  return {
    type: "Feature",
    geometry: { type: "Point", coordinates: coords },
    properties: {
      location_id: lid, place_name: name, n_events, total_attendees: total_att,
      mean_ideology: +mean.toFixed(4), std_ideology: +std.toFixed(4),
      color: bivariateColor(mean, std), opacity: +(0.35 + 0.65 * pct).toFixed(3),
    },
  };
}

// ---- aggregate the active filter into one feature per location ----
function aggregate() {
  const acc = {};
  GROUPS_BY_ID = {};
  for (const f of FEATURES) {
    const p = f.properties;
    if (!passesFilter(p)) continue;
    const lid = p.location_id;
    const a = (acc[lid] ??= { coords: f.geometry.coordinates, name: p.place_name,
                              n: 0, att: 0, w: 0, wx: 0, wxx: 0, wp: 0 });
    if (MODE === "aggregate") {
      a.n += p.n_events; a.att += p.n_att_sum;
      a.w += p.w_sum; a.wx += p.wx_sum; a.wxx += p.wxx_sum; a.wp += p.wp_sum;
    } else {
      const w = p.n_political, x = p.average_normalized;
      a.n += 1; a.att += p.n_attending;
      a.w += w; a.wx += w * x; a.wxx += w * x * x; a.wp += p.percent_political * w;
      (GROUPS_BY_ID[lid] ??= []).push(p); // per-event detail for the future popup
    }
  }

  const feats = [];
  let totalEvents = 0;
  for (const lid in acc) {
    const a = acc[lid];
    totalEvents += a.n;
    feats.push(makeFeature(a.coords, a.name, +lid, a.n, a.att, a.w, a.wx, a.wxx, a.wp));
  }
  document.getElementById("stats").innerHTML =
    `<b>${feats.length.toLocaleString()}</b> locations<br><b>${totalEvents.toLocaleString()}</b> events`;
  return { type: "FeatureCollection", features: feats };
}

function refresh() {
  const src = map.getSource("locations");
  if (src) src.setData(aggregate());
}

// ---- map ----
const map = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    sources: {
      osm: {
        type: "raster",
        tiles: ["https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors © CARTO",
      },
    },
    layers: [{ id: "osm", type: "raster", source: "osm" }],
  },
  center: [12.565, 55.68], // Copenhagen
  zoom: 11.5,
});

function buildControls() {
  const yf = document.getElementById("year-filter");
  YEARS.forEach(y => {
    const b = document.createElement("button");
    b.textContent = y === "All years" ? "All" : y;
    b.className = y === filterYear ? "active" : "";
    b.onclick = () => { filterYear = y; [...yf.children].forEach(c => c.classList.remove("active")); b.classList.add("active"); refresh(); };
    yf.appendChild(b);
  });
  const sf = document.getElementById("size-filter");
  SIZES.forEach(s => {
    const b = document.createElement("button");
    b.textContent = s;
    b.className = s === filterSize ? "active" : "";
    b.onclick = () => { filterSize = s; [...sf.children].forEach(c => c.classList.remove("active")); b.classList.add("active"); refresh(); };
    sf.appendChild(b);
  });
}

map.on("load", async () => {
  [PARAMS, FEATURES] = await Promise.all([
    fetch(`${DATA_BASE}/color_params.json`).then(r => r.json()),
    fetch(`${DATA_BASE}/${DATA_FILE}`).then(r => r.json()).then(fc => fc.features),
  ]);
  buildControls();
  map.addSource("locations", { type: "geojson", data: aggregate() });
  map.addLayer({
    id: "dots", type: "circle", source: "locations",
    paint: {
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 3, 14, 6, 16, 9],
      "circle-color": ["get", "color"],
      "circle-opacity": ["get", "opacity"],
      "circle-stroke-width": 0,
    },
  });
  document.getElementById("loading").classList.add("hidden");
});
