# SEV Tech Tree

A desktop application for visualizing and tracking the technology tree in **Space Empires V**. Displays all 128 technologies as an interactive DAG (directed acyclic graph), shows prerequisites, unlocked components and facilities, and lets you track your research progress.

Built with Electron + Vue 3 + Cytoscape.js. Runs on macOS and Windows.

## Features

- Interactive tech tree graph with dagre layout
- Filter by group and category
- Search across technologies, components, and facilities
- Track researched levels per technology
- Detail panel with prerequisites, unlocked items, and cost
- UI available in Ukrainian and English (game data is in Russian — original game text)

## Getting Started

**Requirements:** Node.js 18+

```bash
npm install
npm run dev        # development (hot reload)
npm run build      # production build
npm run build:mac  # package for macOS (.app)
npm run build:win  # package for Windows (portable .exe)
```

## Project Structure

```
src/
  locales/           # UI translation strings
    uk.json          # Ukrainian
    en.json          # English
  components/
    TechGraph.vue    # Cytoscape DAG graph
    Sidebar.vue      # Group/category filter, search, language switcher
    DetailPanel.vue  # Tech details, level control, components/facilities
  stores/
    techStore.js     # Pinia store — all state and logic
  i18n.js            # Minimal i18n composable (no external library)
  App.vue            # Root layout and topbar

resources/
  tech_tree_uk.json      # Tech tree data (Ukrainian slot — currently Russian game text)
  tech_tree_en.json      # Tech tree data (English slot — currently Russian game text)
  components_uk.json
  components_en.json
  facilities_uk.json
  facilities_en.json
```

## Adding a New Language

### 1. Add UI translations

Copy `src/locales/en.json` to `src/locales/<code>.json` and translate the values.

### 2. Register the locale in i18n.js

```js
// src/i18n.js
import uk from './locales/uk.json'
import en from './locales/en.json'
import de from './locales/de.json'   // ← add

const locales = { uk, en, de }       // ← add
```

### 3. Add game data files

Copy the existing data files as a placeholder:

```bash
cp resources/tech_tree_en.json   resources/tech_tree_de.json
cp resources/components_en.json  resources/components_de.json
cp resources/facilities_en.json  resources/facilities_de.json
```

Replace the content later when you have parsed game data in the target language.

### 4. Register the dataset in techStore.js

```js
// src/stores/techStore.js
import techTreeDe    from '@parsed/tech_tree_de.json'
import componentsDe  from '@parsed/components_de.json'
import facilitiesDe  from '@parsed/facilities_de.json'

const dataByLang = {
  uk: { ... },
  en: { ... },
  de: { techs: techTreeDe, components: componentsDe, facilities: facilitiesDe },  // ← add
}
```

### 5. Add the button in Sidebar.vue

```html
<!-- src/components/Sidebar.vue -->
<div class="lang-section">
  <button class="lang-btn" :class="{ active: currentLang === 'uk' }" @click="store.setLanguage('uk')">УКР</button>
  <button class="lang-btn" :class="{ active: currentLang === 'en' }" @click="store.setLanguage('en')">ENG</button>
  <button class="lang-btn" :class="{ active: currentLang === 'de' }" @click="store.setLanguage('de')">DEU</button>
</div>
```

## Data

Game data is parsed from the original Space Empires V installation files (`TechAreas.txt`, `Components.txt`, `Facilities.txt`). The files use UTF-16 LE encoding with Russian text. See the parser script for details.

Tech names are used as internal IDs throughout the app. When adding an English dataset, parsed tech names must match the `tech` field in requirements arrays so that cross-references resolve correctly.

## License

Personal use. Space Empires V is a trademark of Malfador Machinations.
