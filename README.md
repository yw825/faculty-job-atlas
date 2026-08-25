# Faculty Job Atlas

An interactive map for tracking faculty job openings at four-year colleges and universities, built for a Business Analytics / Information Systems academic job search. Single-file web app — no build step, no server required.

**[Live version hosted via GitHub Pages →](#deploying-with-github-pages)** (link will work once Pages is enabled — see below)

## What it does

- Maps institutions across the **United States**, **Canada**, **Australia**, **New Zealand**, **Macau**, **Singapore**, and **Europe** (22 countries), with more regions in progress
- Color-codes schools by research tier (U.S. Carnegie R1/R2, or U.S. News Best Global Universities ranking elsewhere)
- Lets you search by name, city, state/province, or country
- Filters by program area (Business / CS / Stats) and control (Public / Private) where that data exists
- Drops a pin on any address (or your current location) and filters schools within a driving-time radius
- "Search this area" button re-filters results to whatever's currently visible on the map, like Google Maps
- Every school links to a Google search for its current faculty openings (or a direct careers page where one's been verified)

## Running it

No installation needed — it's a single HTML file with everything (data, styles, logic) embedded.

```bash
# Just open it directly
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux
```

Or in VS Code: install the **Live Server** extension, right-click `index.html`, and choose "Open with Live Server."

## Project structure

```
faculty-job-atlas/
├── index.html      # Everything — HTML, CSS, JS, and embedded institution data
└── README.md
```

Data is embedded directly in the HTML as JS arrays (`SCHOOLS`, `CANADA_SCHOOLS`, `EUROPE_SCHOOLS`, etc.) rather than fetched from external files, so the page works fully offline after the first load (aside from map tiles and geocoding, which need internet).

## Data sources

- **United States:** U.S. Dept. of Education College Scorecard / IPEDS, joined with the American Council on Education's 2025 Carnegie Research Activity Designations
- **Canada:** Universities Canada tuition-fee reporting (institutions with complete tuition data across all 4 categories), joined with U.S. News Best Global Universities rankings
- **Australia / New Zealand:** TEQSA-registered institutions / Universities New Zealand membership, joined with U.S. News Best Global Universities rankings
- **Macau:** Macao Talent Development Committee (cdqq.gov.mo)
- **Singapore:** Singapore ICA's list of Local Universities and Local Polytechnics
- **Hong Kong:** Hong Kong Education Bureau's list of degree-awarding institutions, filtered to those offering Business, CS, and/or Statistics programmes
- **Europe:** curated list from QS World University Rankings: Europe 2026, across 22 countries

## Deploying with GitHub Pages

Once this is pushed to GitHub:

1. Go to the repo on GitHub → **Settings** → **Pages**
2. Under "Build and deployment," set **Source** to "Deploy from a branch"
3. Pick the `main` branch and `/ (root)` folder, then **Save**
4. GitHub will publish it at `https://<your-username>.github.io/<repo-name>/` within a minute or two

## Known limitations

- Distance-radius search uses straight-line ("as the crow flies") distance with an assumed average driving speed, not real road routing
- Coordinates for most non-U.S. institutions are city-center approximations, not exact campus locations
- Europe and a few other regions are curated top-institution lists rather than exhaustive national censuses
