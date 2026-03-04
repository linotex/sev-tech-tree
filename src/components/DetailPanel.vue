<template>
  <aside class="detail-panel" :class="{ open: !!tech || !!store.selectedItem }">

    <!-- Component / Facility view (from search) -->
    <template v-if="store.selectedItem">
      <div class="panel-header">
        <div class="tech-title">{{ store.selectedItem.data.name }}</div>
        <div class="tech-meta">
          <span class="badge" :style="store.selectedItem.type === 'component'
            ? 'background:#1a3a2a;color:#34d399'
            : 'background:#3a2a1a;color:#fb923c'">
            {{ store.selectedItem.type === 'component' ? t('type_component') : t('type_facility') }}
          </span>
          <span v-if="store.selectedItem.data.group" class="badge-cat">
            {{ store.selectedItem.data.group }}
          </span>
        </div>
        <button class="close-btn" @click="store.selectItem(null)">✕</button>
      </div>
      <div class="panel-body">
        <div v-if="store.selectedItem.data.description" class="description-box">
          {{ store.selectedItem.data.description }}
        </div>

        <!-- Stats for selected item -->
        <ItemStats
          :item="store.selectedItem.data"
          :level="selectedItemLevel"
          :show-fuel="store.selectedItem.type === 'component'"
        />

        <div v-if="store.selectedItem.data.requirements?.length" class="section">
          <div class="section-title">{{ t('req_techs') }}</div>
          <div
            v-for="req in store.selectedItem.data.requirements"
            :key="req.tech"
            class="req-item"
            :class="{ met: store.getResearchedLevel(req.tech) >= req.level }"
            @click="goToTech(req.tech)"
          >
            <span class="req-icon">{{ store.getResearchedLevel(req.tech) >= req.level ? '✓' : '○' }}</span>
            {{ req.tech }}
            <span class="req-level">lvl {{ req.level }}</span>
          </div>
        </div>
        <div v-else class="empty-note">{{ t('no_tech_req') }}</div>
      </div>
    </template>

    <!-- Tech view -->
    <template v-else-if="tech">
      <div class="panel-header">
        <div class="tech-title">{{ tech.name }}</div>
        <div class="tech-meta">
          <span class="badge" :style="{ background: groupColor(tech.group) + '33', color: groupColor(tech.group) }">
            {{ tech.group }}
          </span>
          <span v-if="tech.category !== tech.group" class="badge-cat">{{ tech.category }}</span>
        </div>
        <button class="close-btn" @click="store.selectTech(null)">✕</button>
      </div>

      <!-- Level control — outside scroll area, always visible -->
      <div class="level-section">
        <div class="level-label">
          {{ t('research_level') }}
          <span class="level-current">{{ currentLevel }} / {{ tech.maxLevel }}</span>
        </div>
        <div class="level-controls">
          <button class="lvl-btn" @click="decLevel" :disabled="currentLevel === 0">−</button>
          <div class="level-track">
            <div
              v-for="i in tech.maxLevel"
              :key="i"
              class="level-pip"
              :class="{ filled: i <= currentLevel }"
              @click="store.setResearchedLevel(tech.name, i === currentLevel ? i - 1 : i)"
            />
          </div>
          <button class="lvl-btn" @click="incLevel" :disabled="currentLevel === tech.maxLevel">+</button>
        </div>
        <div class="cost-label">
          {{ t('cost_per_level') }}: <strong>{{ tech.costPerLevel.toLocaleString() }}</strong> RP
        </div>
      </div>

      <div class="panel-body">
        <!-- Requirements -->
        <div v-if="tech.requirements.length" class="section">
          <div class="section-title">{{ t('requires') }}</div>
          <div
            v-for="req in tech.requirements"
            :key="req.tech"
            class="req-item"
            :class="{ met: store.getResearchedLevel(req.tech) >= req.level }"
            @click="selectReq(req.tech)"
          >
            <span class="req-icon">{{ store.getResearchedLevel(req.tech) >= req.level ? '✓' : '○' }}</span>
            {{ req.tech }}
            <span class="req-level">lvl {{ req.level }}</span>
          </div>
        </div>

        <!-- Unlocks -->
        <div v-if="unlocksTechs.length" class="section">
          <div class="section-title">{{ t('unlocks_techs') }}</div>
          <div
            v-for="ut in unlocksTechs"
            :key="ut.name"
            class="unlock-item"
            @click="store.selectTech(ut)"
          >
            {{ ut.name }}
            <span class="req-level-badge" :class="{ unlocked: currentLevel >= ut.reqLevel }">
              lvl {{ ut.reqLevel }}
            </span>
          </div>
        </div>

        <!-- Components -->
        <div v-if="components.length" class="section">
          <div class="section-title">{{ t('label_components') }} ({{ components.length }})</div>
          <div
            v-for="c in components"
            :key="c.name"
            class="item-card"
            @click="toggleItem(c.name)"
          >
            <div class="item-name">
              {{ c.name }}
              <span class="req-level-badge" :class="{ unlocked: currentLevel >= c.reqLevel }">
                lvl {{ c.reqLevel }}
              </span>
            </div>
            <template v-if="expandedItems.has(c.name)">
              <div v-if="c.description" class="item-desc">{{ c.description }}</div>
              <ItemStats :item="c" :level="techEffectiveLevel(c)" :show-fuel="true" />
            </template>
          </div>
        </div>

        <!-- Facilities -->
        <div v-if="facilities.length" class="section">
          <div class="section-title">{{ t('label_facilities') }} ({{ facilities.length }})</div>
          <div
            v-for="f in facilities"
            :key="f.name"
            class="item-card"
            @click="toggleItem(f.name)"
          >
            <div class="item-name">
              {{ f.name }}
              <span class="req-level-badge" :class="{ unlocked: currentLevel >= f.reqLevel }">
                lvl {{ f.reqLevel }}
              </span>
            </div>
            <template v-if="expandedItems.has(f.name)">
              <div v-if="f.description" class="item-desc">{{ f.description }}</div>
              <ItemStats :item="f" :level="techEffectiveLevel(f)" :show-fuel="false" />
            </template>
          </div>
        </div>

        <div
          v-if="!tech.requirements.length && !unlocksTechs.length && !components.length && !facilities.length"
          class="empty-note"
        >
          {{ t('no_deps') }}
        </div>
      </div>
    </template>

    <div v-else class="empty-panel">
      <div class="empty-hint">{{ t('click_hint') }}</div>
    </div>
  </aside>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useTechStore } from '../stores/techStore'
import { t } from '../i18n.js'
import { evalFormula, renderAbilityDesc, effectiveLevel } from '../formulaUtil.js'
import ItemStats from './ItemStats.vue'

const store = useTechStore()
const { selectedTech: tech } = storeToRefs(store)
const expandedItems = reactive(new Set())

const GROUP_COLORS = {
  'Культура':            '#c084fc',
  'Теоретические науки': '#60a5fa',
  'Прикладные науки':    '#34d399',
  'Вооружение':          '#fb923c'
}
function groupColor(g) { return GROUP_COLORS[g] || '#94a3b8' }

const currentLevel = computed(() => store.getResearchedLevel(tech.value?.name))

// Level to use when showing stats for components/facilities under a tech.
// Use max(currentLevel, reqLevel) so a component that requires lvl 3
// never shows stats below lvl 3, even if tech is not yet researched that far.
function techEffectiveLevel(item) {
  const minLevel = item.reqLevel || 1
  return effectiveLevel(item, Math.max(currentLevel.value || 1, minLevel))
}

// Level to use when showing a standalone selectedItem (from search)
const selectedItemLevel = computed(() => {
  const data = store.selectedItem?.data
  if (!data) return 1
  const reqs = data.requirements || []
  if (!reqs.length) return 1
  const researched = Math.max(...reqs.map(r => store.getResearchedLevel(r.tech)))
  return effectiveLevel(data, researched || 1)
})

const unlocksTechs = computed(() => {
  if (!tech.value) return []
  return store.techs
    .filter(t => t.requirements.some(r => r.tech === tech.value.name))
    .map(t => ({ ...t, reqLevel: t.requirements.find(r => r.tech === tech.value.name).level }))
    .sort((a, b) => a.reqLevel - b.reqLevel)
})

const components = computed(() => tech.value ? store.unlockedComponents(tech.value.name) : [])
const facilities = computed(() => tech.value ? store.unlockedFacilities(tech.value.name) : [])

function incLevel() {
  if (tech.value && currentLevel.value < tech.value.maxLevel)
    store.setResearchedLevel(tech.value.name, currentLevel.value + 1)
}
function decLevel() {
  if (tech.value && currentLevel.value > 0)
    store.setResearchedLevel(tech.value.name, currentLevel.value - 1)
}
function selectReq(techName) { goToTech(techName) }
function goToTech(techName) {
  const found = store.techs.find(t => t.name === techName)
  if (found) store.selectTech(found)
}
function toggleItem(name) {
  if (expandedItems.has(name)) expandedItems.delete(name)
  else expandedItems.add(name)
}
</script>

<style scoped>
.detail-panel {
  width: 0;
  min-width: 0;
  background: var(--bg-panel);
  border-left: 1px solid var(--border);
  overflow: hidden;
  transition: width 0.25s ease, min-width 0.25s ease;
  display: flex;
  flex-direction: column;
}
.detail-panel.open { width: 300px; min-width: 300px; }

.empty-panel { display: flex; align-items: center; justify-content: center; height: 100%; }
.empty-hint { color: var(--text-dim); font-size: 13px; text-align: center; padding: 20px; }

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.tech-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; padding-right: 24px; line-height: 1.3; }
.tech-meta { display: flex; flex-wrap: wrap; gap: 6px; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: 500; }
.badge-cat { font-size: 11px; color: var(--text-dim); padding: 2px 0; }
.close-btn {
  position: absolute; top: 14px; right: 14px;
  background: none; border: none; color: var(--text-dim);
  cursor: pointer; font-size: 14px; padding: 2px; line-height: 1;
}
.close-btn:hover { color: var(--text); }

.panel-body {
  flex: 1; overflow-y: auto; padding: 12px 16px;
  display: flex; flex-direction: column; gap: 16px;
}

.level-section {
  background: var(--bg-card);
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.level-label { font-size: 12px; color: var(--text-dim); margin-bottom: 10px; display: flex; justify-content: space-between; }
.level-current { color: var(--accent); font-weight: 600; }
.level-controls { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.lvl-btn {
  width: 26px; height: 26px; background: var(--bg-hover);
  border: 1px solid var(--border); color: var(--text);
  border-radius: 5px; cursor: pointer; font-size: 16px; flex-shrink: 0;
}
.lvl-btn:disabled { opacity: 0.3; cursor: default; }
.level-track { flex: 1; display: flex; flex-wrap: wrap; gap: 3px; }
.level-pip {
  width: 10px; height: 10px; border-radius: 2px;
  background: var(--bg-hover); border: 1px solid var(--border);
  cursor: pointer; transition: background 0.1s;
}
.level-pip.filled { background: var(--accent); border-color: var(--accent); }
.cost-label { font-size: 12px; color: var(--text-dim); }

.section { display: flex; flex-direction: column; gap: 4px; }
.section-title { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-dim); margin-bottom: 4px; }

.req-item {
  display: flex; align-items: center; gap: 8px; padding: 6px 10px;
  background: var(--bg-card); border-radius: 6px; font-size: 13px;
  cursor: pointer; border: 1px solid transparent; transition: background 0.1s;
}
.req-item:hover { background: var(--bg-hover); }
.req-item.met { border-color: var(--green); }
.req-item.met .req-icon { color: var(--green); }
.req-icon { font-size: 12px; color: var(--text-dim); }
.req-level { margin-left: auto; font-size: 11px; color: var(--text-dim); }

.unlock-item {
  padding: 6px 10px; background: var(--bg-card); border-radius: 6px;
  font-size: 13px; cursor: pointer; transition: background 0.1s;
  display: flex; align-items: center; justify-content: space-between;
}
.unlock-item:hover { background: var(--bg-hover); color: var(--accent); }

.item-card {
  padding: 7px 10px; background: var(--bg-card); border-radius: 6px;
  cursor: pointer; border: 1px solid transparent; transition: background 0.1s;
}
.item-card:hover { background: var(--bg-hover); }
.item-name { font-size: 13px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.req-level-badge {
  font-size: 11px; padding: 1px 6px; border-radius: 4px;
  background: var(--bg-hover); color: var(--text-dim);
  border: 1px solid var(--border); flex-shrink: 0;
}
.req-level-badge.unlocked { background: #1a3a2a; color: var(--green); border-color: var(--green); }
.item-desc { font-size: 12px; color: var(--text-dim); margin-top: 6px; line-height: 1.5; }

.empty-note { font-size: 12px; color: var(--text-dim); font-style: italic; text-align: center; padding: 8px; }

.description-box {
  background: var(--bg-card); border-radius: 8px; padding: 12px;
  font-size: 13px; color: var(--text-dim); line-height: 1.6;
}
</style>
