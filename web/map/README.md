# Event Ideology Map — local testing

An interactive map of Facebook event political ideology across Copenhagen and
Frederiksberg, in the style of MIT's *Atlas of Inequality*. MapLibre GL + an
OSM-derived dark basemap, fed by a per-event GeoJSON contract.

Each dot is a **location**. Its colour encodes the attendee-weighted mean
political lean (**blue = left, white = centre, red = right**), faded toward
**grey** when the events at that location are politically mixed (high variance).
Opacity reflects how political the location's events are.

## Prerequisites

- Python 3 (only for the static file server — any static server works)
- The data files must exist:
  - `data/map/events.geojson`
  - `data/map/color_params.json`

  If they're missing, regenerate them by running
  [`notebooks/07_event_mapping.ipynb`](../../notebooks/07_event_mapping.ipynb)
  end to end (see *Regenerating the data* below).

## Run it

**Important:** the page must be served over HTTP **from the repository root**,
not opened as a `file://` URL. The map uses `fetch()` to load the GeoJSON, which
browsers block for local files, and it reads the data via a relative path
(`../../data/map/`) that only resolves when the server root is the repo root.

From the repository root (`Thesis/`):

```bash
python3 -m http.server 8000
```

Then open:

```
http://localhost:8000/web/map/index.html
```

Stop the server with `Ctrl+C` in that terminal.

> Any static server works — e.g. `npx serve` or VS Code "Live Server" — as long
> as it serves from the repo root so both `web/` and `data/` are reachable.

## What you should see

- A dark basemap zoomed to Copenhagen/Frederiksberg.
- After the ~22 MB GeoJSON loads (the "Loading events…" overlay clears), a
  scatter of dots — **mostly blue** (left-leaning city), with scattered red,
  white, and grey.
- A control panel (top-right): a colour legend, **YEAR** filter
  (All / 2013-2014 … 2016-2017), **EVENT SIZE** filter (All / Small / Medium),
  and a live **SHOWING** count of locations and events.

Toggling the filters re-aggregates per location on the fly and restyles the
dots. Sanity check: **Small** under **All years** shows **6,151 locations**.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Page shell, control panel markup, CDN includes |
| `map.js` | Loads the contract, filters, client-side per-location aggregation, bivariate styling |
| `style.css` | Dark panel/legend styling |
| `../../data/map/events.geojson` | Per-event GeoJSON contract (the data) |
| `../../data/map/color_params.json` | Pinned colour parameters, mirrored from `src/event_map.py` |

The colour maths in `map.js` mirrors `src/event_map.py` exactly, using the
parameters in `color_params.json` — keep them in sync if you change the scheme.

## Regenerating the data

The map is a pure renderer; all analysis is upstream in Python. To rebuild the
contract (e.g. after changing the colour scheme or the source events):

```bash
# from the repo root
jupyter-nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 notebooks/07_event_mapping.ipynb
```

The first run scans the 13.6 GB raw CSV once and caches `coords_lookup.pkl`;
subsequent runs reuse the cache and are fast. Delete `data/map/coords_lookup.pkl`
to force a re-scan.

## Troubleshooting

Open the browser console (**F12** / **Cmd+Option+I**) if something looks wrong:

- **Blank page / dots never appear** — you probably opened it as `file://` or
  not from the repo root. Use the `http://localhost:8000/web/map/index.html`
  URL above.
- **404 for `events.geojson`** — same cause, or the data files haven't been
  generated yet (run notebook 07).
- **Grey basemap, dots still show** — the CARTO/OSM tile CDN is unreachable
  (offline or blocked); the data layer is unaffected.
