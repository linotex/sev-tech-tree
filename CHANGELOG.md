# Changelog

## [1.7.0] — 2026-03-05

### Added
- Component detail panel: weapon reload time (seconds) shown next to damage
- Component detail panel: "Installable on" section listing compatible vehicle types

### Changed
- Detail panel width increased from 300px to 320px
- Removed "(point blank)" label from damage display
- Reload time value highlighted in magenta color

## [1.6.0] — 2026-03-05

### Added
- Ships: resource cost table (minerals, organics, radioactives) per level in detail panel

### Fixed
- Vehicle tonnage levels now show correct tech levels (e.g. Large Fighter shows 7-9, not 1-3)
- Weapon damage formulas with Cyrillic Мин()/Макс() now evaluate correctly
- Component and tech icons now load correctly in packaged app (relative image paths)
- Components and facilities sorted alphabetically in browser; ships sorted by tonnage

## [1.5.0] — 2026-03-05

### Added
- Tech detail panel: tech icon (36×36 sprite) shown next to tech name in header
- Tech detail panel: tech icons shown in "Unlocks technologies" list
- Tech detail panel: component thumbnails (32×32) shown in components list
- Component detail panel: full 512×512 image shown at top of detail panel
- Image asset pipeline: scripts/copy_images.py copies game images to src/public/images/
- Parser: imageNum added to tech_tree JSON, portrait added to vehicle_sizes JSON

## [1.4.0] — 2026-03-05

### Added
- Ships tab: design requirements and abilities (buffs/debuffs) now shown in ship detail panel
- Parser: vehicle sizes now include `designReqs` and `abilities` fields from VehicleSizes.txt

## [1.3.1] — 2026-03-04

### Fixed
- Detail panel: components and facilities now show all their tech requirements, not just the connection to the currently selected tech
- "Unlocks technologies" section also shows additional requirements for each unlocked tech
- Tech graph canvas re-renders correctly when moving window between displays with different DPI
- Mac build: ad-hoc codesign + quarantine strip for portable distribution

## [1.3.0] — 2026-03-04

### Added
- Ships tab: browse all 102 vehicle sizes (Ship, Base, Fighter, Drone, etc.) grouped by type
- Ship detail panel: tonnage table per level with current level highlighted
- Tech detail panel: "Ship sizes" section showing which hulls a tech unlocks
- Vehicle sizes included in global search results

### Fixed
- Expanding one item in detail panel no longer expands all items (expandedItems cleared on tech/item switch)

## [1.2.1] — 2026-03-04

### Changed
- Tech tree graph: zoom disabled, fixed 1:1 scale
- Mouse wheel / trackpad scroll pans the graph (vertical + horizontal)
- Drag-to-pan still available; ⌂ button resets view to start

## [1.2.0] — 2026-03-04

### Added
- Component and Facility browser tabs in the topbar (Technologies / Components / Facilities)
- ItemBrowser: grouped list with unlock status indicators and required tech badges
- Sidebar adapts to show item groups when browsing components or facilities
- Per-level stats for components and facilities (tonnage, durability, resource costs, abilities)
- Resource legend in sidebar with color-coded abbreviations
- Empire bonuses section in detail panel (Cultural, Intelligence, Empire abilities)
- Total research cost display (current level × cost per level)
- Windows x64 portable build

### Changed
- "Розмір" renamed to "Тоннаж" / "Tonnage"
- "Структура" renamed to "Міцність" / "Durability"
- Level control pinned above the scroll area in detail panel
- Resource abbreviations use styled text instead of emoji for cross-platform compatibility

## [1.0.0] — 2026-03-03

### Added
- Interactive tech tree graph (DAG layout via Cytoscape.js + dagre)
- 128 technologies parsed from Space Empires V game files
- Filter by group and category
- Full-text search across technologies, components, and facilities
- Detail panel: prerequisites, unlocked components/facilities, research cost
- Research progress tracking with per-technology level control
- UI localization: Ukrainian and English
- Multilingual data slots for tech tree, components, and facilities
