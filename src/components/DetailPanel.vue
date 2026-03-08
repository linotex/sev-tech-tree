<template>
  <aside class="detail-panel" :class="{ open: !!tech || !!store.selectedItem }">

    <!-- Component / Facility / Vehicle view (from search or ItemBrowser) -->
    <template v-if="store.selectedItem">
      <div class="panel-header">
        <div class="tech-title">{{ store.selectedItem.data.name }}</div>
        <div class="tech-meta">
          <span class="badge" :style="itemBadgeStyle">{{ itemBadgeLabel }}</span>
          <span v-if="store.selectedItem.data.group || store.selectedItem.data.shipType" class="badge-cat">
            {{ store.selectedItem.data.group || store.selectedItem.data.shipType }}
          </span>
        </div>
        <button class="close-btn" @click="store.selectItem(null)">✕</button>
      </div>
      <div v-if="itemImageUrl" class="item-image-wrap">
        <img :src="itemImageUrl" class="item-image" alt="" @error="e => e.target.style.display='none'" />
      </div>
      <div class="panel-body">
        <div v-if="store.selectedItem.data.description" class="description-box">
          {{ store.selectedItem.data.description }}
        </div>

        <!-- Vehicle size: show level table -->
        <template v-if="store.selectedItem.type === 'vehicle'">
          <div class="section">
            <div class="section-title">{{ t('stat_size') }}</div>
            <table class="vehicle-table">
              <thead>
                <tr>
                  <th>{{ t('stat_level_prefix') }}</th>
                  <th>{{ t('stat_tonnage_short') }}</th>
                  <th>{{ t('res_min') }}</th>
                  <th>{{ t('res_org') }}</th>
                  <th>{{ t('res_rad') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="lvl in vehicleLevels"
                  :key="lvl.display"
                  :class="{ current: lvl.display === vehicleCurrentLevel }"
                >
                  <td class="td-lvl">{{ lvl.display }}</td>
                  <td>{{ evalFormula(store.selectedItem.data.formulas.tonnage, lvl.local) }}</td>
                  <td class="td-min">{{ evalFormula(store.selectedItem.data.formulas.minerals, lvl.local) }}</td>
                  <td class="td-org">{{ evalFormula(store.selectedItem.data.formulas.organics, lvl.local) }}</td>
                  <td class="td-rad">{{ evalFormula(store.selectedItem.data.formulas.radioactives, lvl.local) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="store.selectedItem.data.techReq" class="section">
            <div class="section-title">{{ t('req_techs') }}</div>
            <div
              class="req-item"
              :class="{ met: store.getResearchedLevel(store.selectedItem.data.techReq.tech) >= store.selectedItem.data.techReq.level }"
              @click="goToTech(store.selectedItem.data.techReq.tech)"
            >
              <span class="req-icon">{{ store.getResearchedLevel(store.selectedItem.data.techReq.tech) >= store.selectedItem.data.techReq.level ? '✓' : '○' }}</span>
              {{ store.selectedItem.data.techReq.tech }}
              <span class="req-level">lvl {{ store.selectedItem.data.techReq.level }}</span>
            </div>
          </div>
          <div v-if="store.selectedItem.data.designReqs?.length" class="section">
            <div class="section-title">{{ t('design_reqs') }}</div>
            <div v-for="(req, i) in store.selectedItem.data.designReqs" :key="i" class="design-req">
              {{ req }}
            </div>
          </div>
          <div v-if="store.selectedItem.data.abilities?.length" class="section">
            <div class="section-title">{{ t('stat_abilities') }}</div>
            <div class="abilities">
              <div
                v-for="(ab, i) in store.selectedItem.data.abilities"
                :key="i"
                class="ability-line"
              >
                {{ renderAbilityDesc(ab, vehicleCurrentLevel || 1) }}
              </div>
            </div>
          </div>
        </template>

        <!-- Component / Facility stats -->
        <template v-else>
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
        </template>
      </div>
    </template>

    <!-- Tech view -->
    <template v-else-if="tech">
      <div class="panel-header">
        <div class="tech-header-row">
          <div v-if="tech.imageNum" class="tech-icon-sprite" :style="techIconStyle(tech.imageNum)" />
          <div class="tech-title">{{ tech.name }}</div>
        </div>
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
          <div v-if="currentLevel > 0" class="cost-total">
            {{ t('total_cost') }}: <strong>{{ (currentLevel * tech.costPerLevel).toLocaleString() }}</strong> RP
          </div>
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
            <div class="unlock-main">
              <div v-if="ut.imageNum" class="list-icon-sprite" :style="techIconStyle(ut.imageNum)" />
              <span class="unlock-name">{{ ut.name }}</span>
              <span class="req-level-badge" :class="{ unlocked: currentLevel >= ut.reqLevel }">
                lvl {{ ut.reqLevel }}
              </span>
            </div>
            <div
              v-for="req in ut.requirements.filter(r => r.tech !== tech.name)"
              :key="req.tech"
              class="unlock-also-req"
              :class="{ met: store.getResearchedLevel(req.tech) >= req.level }"
              @click.stop="goToTech(req.tech)"
            >
              + {{ req.tech }} lvl {{ req.level }}
            </div>
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
              <img v-if="c.imageNum" :src="compIconUrl(c.imageNum)" class="list-comp-icon" alt="" @error="e => e.target.style.display='none'" />
              <span class="item-name-text">{{ c.name }}</span>
              <span class="req-level-badge" :class="{ unlocked: currentLevel >= c.reqLevel }">
                lvl {{ c.reqLevel }}
              </span>
            </div>
            <div
              v-for="req in c.requirements.filter(r => r.tech !== tech.name)"
              :key="req.tech"
              class="unlock-also-req"
              :class="{ met: store.getResearchedLevel(req.tech) >= req.level }"
            >+ {{ req.tech }} lvl {{ req.level }}</div>
            <template v-if="expandedItems[c.name]">
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
            <div
              v-for="req in f.requirements.filter(r => r.tech !== tech.name)"
              :key="req.tech"
              class="unlock-also-req"
              :class="{ met: store.getResearchedLevel(req.tech) >= req.level }"
            >+ {{ req.tech }} lvl {{ req.level }}</div>
            <template v-if="expandedItems[f.name]">
              <div v-if="f.description" class="item-desc">{{ f.description }}</div>
              <ItemStats :item="f" :level="techEffectiveLevel(f)" :show-fuel="false" />
            </template>
          </div>
        </div>

        <!-- Empire bonuses -->
        <div v-if="bonuses.length" class="section">
          <div class="section-title">{{ t('empire_bonuses') }} ({{ bonuses.length }})</div>
          <div
            v-for="b in bonuses"
            :key="b.name"
            class="item-card bonus-card"
            @click="toggleItem(b.name)"
          >
            <div class="item-name">
              {{ b.name }}
              <span class="req-level-badge" :class="{ unlocked: currentLevel >= b.reqLevel }">
                lvl {{ b.reqLevel }}
              </span>
            </div>
            <template v-if="expandedItems[b.name]">
              <div v-if="b.description" class="item-desc">{{ b.description }}</div>
              <div class="abilities bonus-abilities">
                <div
                  v-for="(ab, i) in b.abilities.filter(a => a.description)"
                  :key="i"
                  class="ability-line"
                >
                  {{ renderAbilityDesc(ab, techEffectiveLevel(b)) }}
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- Vehicle sizes -->
        <div v-if="vehicleSizes.length" class="section">
          <div class="section-title">{{ t('unlocks_vehicles') }} ({{ vehicleSizes.length }})</div>
          <div
            v-for="v in vehicleSizes"
            :key="v.name"
            class="item-card"
            @click="toggleItem('v:' + v.name)"
          >
            <div class="item-name">
              {{ v.name }}
              <span class="req-level-badge" :class="{ unlocked: currentLevel >= v.reqLevel }">
                lvl {{ v.reqLevel }}
              </span>
            </div>
            <template v-if="expandedItems['v:' + v.name]">
              <div class="vehicle-stats">
                <div v-for="lvl in techVehicleLevels(v)" :key="lvl.display" class="vehicle-row" :class="{ current: lvl.display === currentLevel }">
                  <span class="vlvl">{{ lvl.display }}</span>
                  <span class="vstat">{{ evalFormula(v.formulas.tonnage, lvl.local) }}{{ t('stat_tonnage_short') }}</span>
                </div>
              </div>
            </template>
          </div>
        </div>

        <div
          v-if="!tech.requirements.length && !unlocksTechs.length && !components.length && !facilities.length && !bonuses.length && !vehicleSizes.length"
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
import { computed, reactive, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTechStore } from '../stores/techStore'
import { t } from '../i18n.js'
import { evalFormula, renderAbilityDesc } from '../formulaUtil.js'
import ItemStats from './ItemStats.vue'

const store = useTechStore()
const { selectedTech: tech } = storeToRefs(store)
const expandedItems = reactive({})

// Clear expanded state whenever selected tech or item changes
watch([tech, () => store.selectedItem], () => {
  Object.keys(expandedItems).forEach(k => delete expandedItems[k])
})

const GROUP_COLORS = {
  'Культура':            '#c084fc',
  'Теоретические науки': '#60a5fa',
  'Прикладные науки':    '#34d399',
  'Вооружение':          '#fb923c'
}
function groupColor(g) { return GROUP_COLORS[g] || '#94a3b8' }

const currentLevel = computed(() => store.getResearchedLevel(tech.value?.name))

const itemBadgeStyle = computed(() => {
  const type = store.selectedItem?.type
  if (type === 'component') return 'background:#1a3a2a;color:#34d399'
  if (type === 'facility')  return 'background:#3a2a1a;color:#fb923c'
  return 'background:#1a2a3a;color:#60a5fa'
})
const itemBadgeLabel = computed(() => {
  const type = store.selectedItem?.type
  if (type === 'component') return t('type_component')
  if (type === 'facility')  return t('type_facility')
  return t('view_vehicles')
})
const vehicleCurrentLevel = computed(() => {
  const v = store.selectedItem?.data
  if (!v?.techReq) return 0
  return store.getResearchedLevel(v.techReq.tech)
})

// Actual tech levels for a vehicle: from techReq.level to techReq.level + maxLevel - 1
const vehicleLevels = computed(() => {
  const d = store.selectedItem?.data
  if (!d) return []
  const start = d.techReq?.level ?? 1
  return Array.from({ length: d.maxLevel }, (_, i) => ({ display: start + i, local: i + 1 }))
})

function techVehicleLevels(v) {
  const start = v.techReq?.level ?? 1
  return Array.from({ length: v.maxLevel }, (_, i) => ({ display: start + i, local: i + 1 }))
}

// Image URL for the selected item (component / facility / vehicle)
const itemImageUrl = computed(() => {
  const item = store.selectedItem
  if (!item) return null
  if (item.type === 'component' && item.data.imageNum)
    return `./images/components/${String(item.data.imageNum).padStart(3, '0')}.jpg`
  return null
})

function compIconUrl(imageNum) {
  if (!imageNum) return null
  return `./images/components/${String(imageNum).padStart(3, '0')}.jpg`
}

// CSS style for a tech icon sprite (36×36 grid, 14 cols)
function techIconStyle(imageNum) {
  const idx = imageNum - 1
  const col = idx % 14
  const row = Math.floor(idx / 14)
  return {
    backgroundImage: "url('./images/tech_icons.png')",
    backgroundPosition: `-${col * 36}px -${row * 36}px`,
    backgroundRepeat: 'no-repeat',
    width: '36px',
    height: '36px',
    flexShrink: '0',
    imageRendering: 'pixelated',
  }
}

// Level to use when showing stats for components/facilities under a tech.
// Component level = (current tech level - base req level + 1), clamped to [1, maxLevel].
// e.g. a component requiring tech >= 20 shows level 1 stats when tech is at 20.
function techEffectiveLevel(item) {
  const base = item.reqLevel || 1
  const techLevel = Math.max(currentLevel.value || 1, base)
  const compLevel = techLevel - base + 1
  return Math.max(1, Math.min(compLevel, item.maxLevel || 1))
}

// Level to use when showing a standalone selectedItem (from search)
const selectedItemLevel = computed(() => {
  const data = store.selectedItem?.data
  if (!data) return 1
  const reqs = data.requirements || []
  if (!reqs.length) return 1
  let best = 1
  for (const req of reqs) {
    const techLevel = store.getResearchedLevel(req.tech) || 0
    const compLevel = Math.max(1, Math.min(techLevel - req.level + 1, data.maxLevel || 1))
    if (compLevel > best) best = compLevel
  }
  return best
})

const unlocksTechs = computed(() => {
  if (!tech.value) return []
  return store.techs
    .filter(t => t.requirements.some(r => r.tech === tech.value.name))
    .map(t => ({ ...t, reqLevel: t.requirements.find(r => r.tech === tech.value.name).level }))
    .sort((a, b) => a.reqLevel - b.reqLevel)
})

const components    = computed(() => tech.value ? store.unlockedComponents(tech.value.name) : [])
const facilities    = computed(() => tech.value ? store.unlockedFacilities(tech.value.name) : [])
const bonuses       = computed(() => tech.value ? store.unlockedBonuses(tech.value.name) : [])
const vehicleSizes  = computed(() => tech.value ? store.unlockedVehicleSizes(tech.value.name) : [])

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
  expandedItems[name] = !expandedItems[name]
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
.detail-panel.open { width: 320px; min-width: 320px; }

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
.cost-total { font-size: 12px; color: var(--accent-dim); margin-top: 5px; }

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
  display: flex; flex-direction: column; gap: 3px;
}
.unlock-item:hover { background: var(--bg-hover); color: var(--accent); }
.unlock-main {
  display: flex; align-items: center; justify-content: space-between; gap: 6px;
}
.unlock-also-req {
  font-size: 11px;
  color: var(--text-dim);
  padding-left: 4px;
}
.unlock-also-req.met { color: var(--green); }

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

.bonus-card { border-color: transparent; }
.bonus-card:hover { border-color: var(--accent-dim); }

.bonus-abilities {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.ability-line {
  font-size: 12px;
  color: var(--text-dim);
  line-height: 1.4;
  padding-left: 10px;
  position: relative;
}
.ability-line::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--accent-dim);
}

.empty-note { font-size: 12px; color: var(--text-dim); font-style: italic; text-align: center; padding: 8px; }

.vehicle-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.vehicle-row {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 3px 7px;
  font-size: 11px;
  color: var(--text-dim);
}
.vehicle-row.current { border-color: var(--accent); color: var(--accent); }
.vlvl { font-weight: 600; min-width: 14px; }
.vstat { color: inherit; }

.vehicle-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-top: 6px;
}
.vehicle-table th {
  text-align: right;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  padding: 3px 6px;
  border-bottom: 1px solid var(--border);
}
.vehicle-table th:first-child { text-align: left; }
.vehicle-table td {
  text-align: right;
  padding: 4px 6px;
  color: var(--text-dim);
  border-bottom: 1px solid var(--bg-hover);
}
.vehicle-table td:first-child { text-align: left; font-weight: 600; }
.vehicle-table tr.current td { color: var(--accent); background: #0d1f2d; }
.td-lvl { color: var(--text) !important; }
.td-min { color: #94a3b8 !important; }
.td-org { color: #34d399 !important; }
.td-rad { color: #fb923c !important; }
.vehicle-table tr.current .td-min,
.vehicle-table tr.current .td-org,
.vehicle-table tr.current .td-rad { opacity: 0.9; }

.description-box {
  background: var(--bg-card); border-radius: 8px; padding: 12px;
  font-size: 13px; color: var(--text-dim); line-height: 1.6;
}

.item-image-wrap {
  width: 100%;
  background: #000;
  flex-shrink: 0;
  overflow: hidden;
}
.item-image {
  width: 100%;
  display: block;
  object-fit: cover;
  max-height: 240px;
}

.tech-header-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  padding-right: 24px;
}
.tech-header-row .tech-title {
  margin-bottom: 0;
  padding-right: 0;
}
.tech-icon-sprite {
  border-radius: 4px;
  flex-shrink: 0;
}

.list-icon-sprite {
  border-radius: 3px;
  flex-shrink: 0;
}

.unlock-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-comp-icon {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 3px;
  flex-shrink: 0;
}
.item-name-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.design-req {
  font-size: 12px;
  color: var(--text-dim);
  line-height: 1.5;
  padding: 4px 10px;
  background: var(--bg-card);
  border-radius: 5px;
  border-left: 2px solid var(--border);
}

.abilities {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
</style>
