# Yemen Offline Map Export Pipeline

This directory is structured as a standalone project so it can be published separately from the iPod-focused repository. Copy the folder into a new Git project (or export it as an archive) to share it independently on GitHub or any other hosting platform.

The guide below describes how to build a Yemen-wide offline map package in QGIS that can be loaded in All-in-One Offline Maps (Android), Guru Maps / Map Plus (iOS), and QField. It covers imagery, vector basemaps, an optional searchable points-of-interest layer, and strategies for size optimisation so the package fits on a single SSD or SD card.

## 1. Prerequisites

- QGIS Long-Term Release (LTR) — install from https://qgis.org (v3.28 or newer).
- Sufficient disk space for intermediate rasters (hundreds of GB for country-scale imagery).
- Data sources:
  - Yemen administrative boundaries (e.g., [GADM](https://gadm.org) or [Natural Earth](https://www.naturalearthdata.com)).
  - OpenStreetMap vector extract for Yemen (e.g., [Geofabrik](https://download.geofabrik.de/asia/yemen.html)).
  - Raster imagery (Maxar SecureWatch exports, Sentinel-2 mosaics, ESRI/Google/Planet XYZ caches, etc.).
  - Optional POI dataset (OSM `points` file, humanitarian datasets, gazetteers).
- Plugins:
  - **QuickMapServices** (QMS) for preview basemaps.
  - **MMQGIS** (optional) for quick CSV-to-layer and attribute processing.
  - **QMetaTiles** (optional) if you prefer a dedicated MBTiles exporter.

## 2. Project Setup

1. Launch QGIS LTR and create a new project.
2. Set the project coordinate reference system (CRS) to **EPSG:3857 – WGS 84 / Pseudo-Mercator**:
   - Bottom-right of QGIS window → click the current CRS → search `3857` → apply.
3. Add source layers:
   - **Country boundary**: Load the Yemen polygon as a vector layer. Keep it available for clipping and extent definition.
   - **OSM vectors**: Import the Geofabrik `.gpkg` or `.pbf` via *Layer → Data Source Manager*. Load roads, waterways, places, landuse, etc., as separate layers or style them using an OSM style pack.
   - **Imagery**: Add your raster sources. For XYZ tiles, use *Layer → Data Source Manager → XYZ*. For GeoTIFFs, drag them in or use *Add Raster Layer*.
4. Optional: Add QuickMapServices → search for "Google Satellite" or "ESRI World Imagery" to preview coverage. Keep this layer turned off during export to avoid licensing conflicts.
5. Save the project (`yemen_offline.qgz`) inside a working directory, e.g., `~/projects/yemen_offline/`.

## 3. Imagery to MBTiles

### Option A – Starting from GeoTIFF mosaics

1. Ensure your imagery mosaics are in EPSG:3857. If not, reproject via *Raster → Projections → Warp (Reproject)* using `EPSG:3857` and the Yemen boundary as a cutline.
2. Open *Processing Toolbox → Generate XYZ Tiles (MBTiles)*.
3. Configure parameters:
   - **Extent**: Use the Yemen boundary layer (`Calculate from Layer`).
   - **Minimum/Maximum Zoom**: Country reference overview (z5–z7), general navigation (z8–z11), detail imagery (z12–z15). Adjust based on source resolution; avoid generating zoom levels finer than your raster pixel size (e.g., Sentinel-2 supports up to z14 gracefully, Maxar up to z17).
   - **Tile format**: PNG for imagery with transparency; JPEG (quality 80–85) to reduce size for full-color imagery.
   - **Output file**: `imagery_yemen.mbtiles` in your export folder.
   - Enable **Use Multiple Threads** and set **Tile Column/Row Limit** if you want to chunk output per zoom.
4. Run the tool. Monitor the log for tile counts. Expect several hours for z5–z15.

### Option B – Downloading XYZ tiles directly

1. Add the XYZ tile URL (e.g., Google, Bing) to QGIS.
2. Right-click the layer → *Export → Save As…* → `MBTiles` format.
3. Match the zoom range to the service terms and device capacity. For commercial basemaps respect licensing terms.
4. Enable **Tile Matrix** `WebMercatorQuad` and set compression to JPEG 80.
5. Save as `imagery_yemen.mbtiles`.

### Post-processing (optional)

- Use `mb-util` or `tile-join` (from Tippecanoe) to merge or thin zoom levels.
- Use `sqlite3 imagery_yemen.mbtiles 'VACUUM;'` to compact the database.
- Generate metadata JSON: `title`, `description`, `attribution`, `minzoom`, `maxzoom`.

## 4. Vector Basemap Layers

### 4.1 Prepare data in GeoPackage

1. Import OSM extracts into a working GeoPackage (`yemen_vectors.gpkg`). Use *Processing → Vector → General → Extract by extent* to clip to Yemen plus a 10–20 km buffer.
2. Simplify high-resolution geometry for lower zooms using *Processing → Vector → Geometry → Simplify*. Create multiple generalized tables if you plan to export scale-dependent tiles.
3. Standard layers to prepare:
   - `roads_primary`, `roads_secondary`, `tracks`
   - `admin_boundaries_lvl1`, `admin_boundaries_lvl2`
   - `settlements` (cities, towns, villages)
   - `hydrography` (rivers, lakes)
   - `landmarks` (airports, ports)

### 4.2 Style for output

- Create QGIS styles using categorized or rule-based symbology.
- For device legibility, keep line widths ≥ 0.3 mm and use high-contrast colors.
- Set labeling rules for settlement names (priority: city > town > village) with scale-based visibility.

### 4.3 Export options

**Option A – MBTiles Vector Tiles (recommended for Guru/All-in-One)**

1. Install **Vector Tiles Writer** plugin (or use QGIS 3.34+'s native exporter).
2. *Project → Import/Export → Generate Vector Tiles (MBTiles)*.
3. Configure:
   - **Extent**: Yemen boundary.
   - **Min/Max zoom**: Typically z5–z12 for vectors. Higher zooms inflate size; rely on imagery for detail.
   - **Tile resolution**: 4096 for detail, 2048 for smaller files.
   - **Layers**: Select only the needed layers. Use attribute filters to drop unused fields (e.g., keep `name`, `type`, `ref`).
   - Output: `yemen_basemap.mbtiles`.
4. After export, open the MBTiles in the **Browser** panel to verify styling.

**Option B – Shapefiles/GeoPackage for QField**

- Duplicate layers into a `qfield` GeoPackage with simplified geometry and minimal attributes.
- Use *QField Sync* plugin (see Section 6) to package the layers directly without MBTiles.

## 5. Optional Searchable POI / Labels Layer

1. Start from OSM `points` or curated datasets.
2. Clean attributes:
   - Keep `name`, `name:ar`, `name:en`, `amenity`, `tourism`, `shop`, `phone`, `website`.
   - Normalize categories (e.g., map multiple amenities to a `poi_class`).
3. Use *Processing → Vector Table → Refactor Fields* to control field order and type.
4. For searchable MBTiles:
   - Convert to GeoJSON and load into Tippecanoe: `tippecanoe -f -o yemen_poi.mbtiles -zg --drop-densest-as-needed poi.geojson`.
   - Add `--include=name --include=amenity` flags for search fields.
   - Set `--layer=poi` and `--drop-rate=1` to reduce density.
5. For QField:
   - Keep as a point layer in the project GeoPackage.
   - Add form widgets for offline data entry if needed.

## 6. Packaging for Target Apps

### 6.1 All-in-One Offline Maps (Android)

1. Copy `imagery_yemen.mbtiles`, `yemen_basemap.mbtiles`, and `yemen_poi.mbtiles` onto the device under `Android/data/net.psyberia.offlinemaps/files/tiles/` or import through the app's *Maps → Imported Map → +* menu.
2. Ensure MBTiles metadata fields `name` and `type` are set (`type=baselayer` or `overlay`).
3. For large datasets, split into multiple files (north/south) and use the app's layer stacking to toggle.

### 6.2 Guru Maps / Map Plus (iOS)

1. Rename MBTiles files to descriptive names (e.g., `Yemen_Imagery.mbtiles`).
2. Transfer via iTunes File Sharing or AirDrop into Guru Maps' *Maps* folder.
3. In Guru Maps, go to *Maps → Import Map → MBTiles* and activate imagery as base map, vector tiles as overlay.
4. Guru supports search on vector tiles if attributes are included in the MBTiles metadata (`json` column). Tippecanoe automatically writes these.

### 6.3 QField (Android / Desktop)

1. Install the **QField Sync** plugin in QGIS.
2. Configure the project for offline use:
   - Use GeoPackage layers for editable data (roads, POI, admin boundaries).
   - Register MBTiles for background imagery: *Project Properties → QField → Add Offline Base Map*.
3. Run *Project → QField Sync → Package for QField*:
   - Choose an output folder (`/exports/yemen_qfield`).
   - Include MBTiles and reference layers.
4. Copy the output folder onto the device (`/QField/yemen_offline/`).
5. On QField, open the project, verify layers, and test label visibility.

## 7. Size Optimisation Strategies

- **Zoom level budgeting**: Each additional zoom roughly quadruples tile count. Choose max zoom per dataset based on resolution (e.g., vector z12, imagery z15).
- **Tile format**: Prefer JPEG for true-color imagery, PNG only when transparency is required.
- **Generalisation**: Simplify vectors for low zooms and use attribute filtering to drop unused fields.
- **Spatial partitioning**: If a single MBTiles exceeds device limits (>6–8 GB), create north/south or governorate-based subsets.
- **Compression**: Run `VACUUM` on MBTiles and enable `--gzip` in Tippecanoe for vector tiles.
- **Storage planning**: A full Yemen package with imagery (z5–z15 JPEG 80) plus vector tiles typically ranges 40–80 GB. Ensure the SSD/SD card is formatted exFAT for cross-platform support.

## 8. Quality Assurance Checklist

- Load MBTiles in QGIS or MapTiler Desktop to ensure tiles render correctly.
- Verify attribution requirements for each data source inside the MBTiles metadata.
- Test imagery and vector toggling on target devices.
- Confirm search functionality (Guru Maps) by searching for known POI names.
- For QField, test feature editing on a dummy layer to ensure the GeoPackage is writable.

## 9. Automation Tips

- Script exports with `qgis_process` for reproducible builds, e.g.,
  ```bash
  qgis_process run qgis:tilesxyzmbtiles -- INPUT_RASTER=imagery_3857.tif ZOOM_MIN=5 ZOOM_MAX=15 TILE_FORMAT=1 OUTPUT=imagery_yemen.mbtiles
  ```
- Use cron or CI to refresh OSM extracts monthly and regenerate vector tiles with Tippecanoe.
- Maintain a `metadata.yaml` describing datasets, zooms, and licences to track updates.

## 10. Deliverables Summary

| File | Purpose | Target Apps |
| --- | --- | --- |
| `imagery_yemen.mbtiles` | Raster basemap imagery (JPEG z5–z15) | All-in-One, Guru, QField |
| `yemen_basemap.mbtiles` | Vector tiles (roads, admin, hydro, settlements) | All-in-One, Guru |
| `yemen_poi.mbtiles` | Optional POI/labels with search metadata | All-in-One (overlay), Guru |
| `yemen_vectors.gpkg` | Editable layers for QField | QField |
| `yemen_offline.qgz` | QGIS project configured for packaging | QField |

With these components you can rapidly deploy a Yemen-wide offline mapping solution that works across Android, iOS, and field data collection workflows.
