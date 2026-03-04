# Changelog

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
