<template>
  <aside class="sidebar">
    <!-- Search -->
    <div class="search-wrap">
      <input
        v-model="store.searchQuery"
        class="search"
        :placeholder="t('search_placeholder')"
        @input="store.filterGroup = null; store.filterCategory = null"
      />
      <button v-if="store.searchQuery" class="clear-btn" @click="store.searchQuery = ''">✕</button>
    </div>

    <!-- Search results -->
    <template v-if="store.searchQuery">
      <div class="filter-section">
        <template v-if="results.techs.length">
          <div class="results-label">{{ t('label_techs') }} ({{ results.techs.length }})</div>
          <div
            v-for="tech in results.techs"
            :key="'t-' + tech.name"
            class="result-item"
            :class="{ active: store.selectedTech?.name === tech.name }"
            @click="store.selectTech(tech)"
          >
            <span class="type-badge tech">Т</span>
            {{ tech.name }}
          </div>
        </template>

        <template v-if="results.components.length">
          <div class="results-label">{{ t('label_components') }} ({{ results.components.length }})</div>
          <div
            v-for="c in results.components"
            :key="'c-' + c.name"
            class="result-item"
            :class="{ active: store.selectedItem?.data?.name === c.name }"
            @click="store.selectItem(c, 'component')"
          >
            <span class="type-badge comp">К</span>
            {{ c.name }}
          </div>
        </template>

        <template v-if="results.facilities.length">
          <div class="results-label">{{ t('label_facilities') }} ({{ results.facilities.length }})</div>
          <div
            v-for="f in results.facilities"
            :key="'f-' + f.name"
            class="result-item"
            :class="{ active: store.selectedItem?.data?.name === f.name }"
            @click="store.selectItem(f, 'facility')"
          >
            <span class="type-badge fac">С</span>
            {{ f.name }}
          </div>
        </template>

        <div v-if="!results.techs.length && !results.components.length && !results.facilities.length" class="no-results">
          {{ t('no_results') }}
        </div>
      </div>
    </template>

    <!-- Groups & Categories (normal mode) -->
    <template v-else>
      <div class="filter-section">
        <div
          class="group-item"
          :class="{ active: !store.filterGroup }"
          @click="store.clearFilter()"
        >
          <span class="dot" style="background:#94a3b8" />
          {{ t('all_groups') }}
          <span class="cnt">{{ store.techs.length }}</span>
        </div>
        <template v-for="group in store.groups" :key="group">
          <div
            class="group-item"
            :class="{ active: store.filterGroup === group && !store.filterCategory }"
            @click="toggleGroup(group)"
          >
            <span class="dot" :style="{ background: groupColor(group) }" />
            {{ group }}
            <span class="cnt">{{ store.techs.filter(t => t.group === group).length }}</span>
          </div>
          <template v-if="store.filterGroup === group">
            <div
              v-for="cat in store.categoriesForGroup(group)"
              :key="cat"
              class="cat-item"
              :class="{ active: store.filterCategory === cat }"
              @click.stop="store.filterCategory = cat === store.filterCategory ? null : cat"
            >
              {{ cat }}
              <span class="cnt">{{ store.techs.filter(t => t.group === group && t.category === cat).length }}</span>
            </div>
          </template>
        </template>
      </div>
    </template>

    <!-- Resource legend -->
    <div class="legend-section">
      <div class="section-title">{{ t('legend_title') }}</div>
      <div class="legend-grid">
        <div class="legend-row">
          <span class="legend-dot minerals" /><span class="legend-abbr minerals">{{ t('res_min') }}</span>
          <span class="legend-full">{{ t('res_min_full') }}</span>
        </div>
        <div class="legend-row">
          <span class="legend-dot organics" /><span class="legend-abbr organics">{{ t('res_org') }}</span>
          <span class="legend-full">{{ t('res_org_full') }}</span>
        </div>
        <div class="legend-row">
          <span class="legend-dot radio" /><span class="legend-abbr radio">{{ t('res_rad') }}</span>
          <span class="legend-full">{{ t('res_rad_full') }}</span>
        </div>
        <div class="legend-row">
          <span class="legend-dot fuel" /><span class="legend-abbr fuel">{{ t('res_fuel') }}</span>
          <span class="legend-full">{{ t('res_fuel_full') }}</span>
        </div>
        <div class="legend-row">
          <span class="legend-dot ammo" /><span class="legend-abbr ammo">{{ t('res_ammo') }}</span>
          <span class="legend-full">{{ t('res_ammo_full') }}</span>
        </div>
      </div>
    </div>

    <!-- Language switcher -->
    <div class="lang-section">
      <button
        class="lang-btn"
        :class="{ active: currentLang === 'uk' }"
        @click="store.setLanguage('uk')"
      >УКР</button>
      <button
        class="lang-btn"
        :class="{ active: currentLang === 'en' }"
        @click="store.setLanguage('en')"
      >ENG</button>
    </div>

    <!-- Researched progress -->
    <div class="progress-section">
      <div class="section-title">{{ t('progress_title') }}</div>
      <div class="progress-bar-wrap">
        <div class="progress-bar" :style="{ width: progressPct + '%' }" />
      </div>
      <div class="progress-label">{{ researchedCount }} / {{ store.techs.length }}</div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useTechStore } from '../stores/techStore'
import { t, lang } from '../i18n.js'

const store = useTechStore()
const currentLang = lang

const GROUP_COLORS = {
  'Культура':            '#c084fc',
  'Теоретические науки': '#60a5fa',
  'Прикладные науки':    '#34d399',
  'Вооружение':          '#fb923c'
}
function groupColor(g) { return GROUP_COLORS[g] || '#94a3b8' }

function toggleGroup(group) {
  if (store.filterGroup === group) store.clearFilter()
  else store.setFilter(group)
}

const results = computed(() => store.searchResults || { techs: [], components: [], facilities: [] })

const researchedCount = computed(() =>
  Object.values(store.researchedLevels).filter(l => l > 0).length
)
const progressPct = computed(() =>
  Math.round((researchedCount.value / store.techs.length) * 100)
)
</script>

<style scoped>
.sidebar {
  width: 240px;
  min-width: 240px;
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-wrap {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.search {
  width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 7px 28px 7px 10px;
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.search:focus { border-color: var(--accent); }
.search::placeholder { color: var(--text-dim); }
.clear-btn {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 13px;
  padding: 2px;
  line-height: 1;
}
.clear-btn:hover { color: var(--text); }

.filter-section {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.results-label {
  padding: 8px 14px 4px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
}

.result-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-dim);
  transition: background 0.1s, color 0.1s;
}
.result-item:hover { background: var(--bg-hover); color: var(--text); }
.result-item.active { background: var(--bg-hover); color: var(--text); }

.type-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
  flex-shrink: 0;
}
.type-badge.tech { background: #1e3a5f; color: #60a5fa; }
.type-badge.comp { background: #1a3a2a; color: #34d399; }
.type-badge.fac  { background: #3a2a1a; color: #fb923c; }

.no-results {
  padding: 20px 14px;
  font-size: 13px;
  color: var(--text-dim);
  text-align: center;
}

.group-item, .cat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-dim);
  transition: background 0.1s, color 0.1s;
  user-select: none;
}
.group-item:hover, .cat-item:hover { background: var(--bg-hover); color: var(--text); }
.group-item.active, .cat-item.active { background: var(--bg-hover); color: var(--text); }
.cat-item { padding-left: 34px; font-size: 12px; }

.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.cnt {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-dim);
  background: var(--bg-deep);
  padding: 1px 5px;
  border-radius: 8px;
}

.lang-section {
  display: flex;
  gap: 6px;
  padding: 10px 14px;
  border-top: 1px solid var(--border);
}
.lang-btn {
  flex: 1;
  padding: 5px 0;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-dim);
  transition: all 0.15s;
}
.lang-btn:hover { background: var(--bg-hover); color: var(--text); }
.lang-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
}

.progress-section {
  padding: 12px 14px;
  border-top: 1px solid var(--border);
}
.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  margin-bottom: 8px;
}
.progress-bar-wrap {
  background: var(--bg-card);
  border-radius: 4px;
  height: 6px;
  overflow: hidden;
  margin-bottom: 6px;
}
.progress-bar {
  height: 100%;
  background: var(--accent);
  border-radius: 4px;
  transition: width 0.3s;
}
.progress-label {
  font-size: 12px;
  color: var(--text-dim);
  text-align: right;
}

.legend-section {
  padding: 10px 14px;
  border-top: 1px solid var(--border);
}
.legend-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 6px;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.legend-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-abbr {
  font-size: 11px;
  font-weight: 700;
  width: 28px;
  flex-shrink: 0;
}
.legend-full {
  color: var(--text-dim);
  font-size: 11px;
}

.legend-dot.minerals, .legend-abbr.minerals { background: #94a3b8; color: #94a3b8; }
.legend-dot.organics,  .legend-abbr.organics  { background: #34d399; color: #34d399; }
.legend-dot.radio,     .legend-abbr.radio      { background: #fb923c; color: #fb923c; }
.legend-dot.fuel,      .legend-abbr.fuel       { background: #60a5fa; color: #60a5fa; }
.legend-dot.ammo,      .legend-abbr.ammo       { background: #f87171; color: #f87171; }
</style>
