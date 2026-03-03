<template>
  <aside class="detail-panel" :class="{ open: !!tech || !!store.selectedItem }">
    <!-- Component / Facility view -->
    <template v-if="store.selectedItem">
      <div class="panel-header">
        <div class="tech-title">{{ store.selectedItem.data.name }}</div>
        <div class="tech-meta">
          <span class="badge" :style="store.selectedItem.type === 'component' ? 'background:#1a3a2a;color:#34d399' : 'background:#3a2a1a;color:#fb923c'">
            {{ store.selectedItem.type === 'component' ? 'Компонент' : 'Споруда' }}
          </span>
          <span v-if="store.selectedItem.data.group" class="badge-cat">{{ store.selectedItem.data.group }}</span>
        </div>
        <button class="close-btn" @click="store.selectItem(null)">✕</button>
      </div>
      <div class="panel-body">
        <div v-if="store.selectedItem.data.description" class="description-box">
          {{ store.selectedItem.data.description }}
        </div>

        <div v-if="store.selectedItem.data.requirements.length" class="section">
          <div class="section-title">Потрібні технології</div>
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
        <div v-else class="empty-note">Не потребує технологій</div>
      </div>
    </template>

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

      <div class="panel-body">
        <!-- Level control -->
        <div class="level-section">
          <div class="level-label">
            Рівень дослідження
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
            Вартість рівня: <strong>{{ tech.costPerLevel.toLocaleString() }}</strong> RP
          </div>
        </div>

        <!-- Requirements -->
        <div v-if="tech.requirements.length" class="section">
          <div class="section-title">Потребує</div>
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

        <!-- Unlocks (techs that require this) -->
        <div v-if="unlocksTechs.length" class="section">
          <div class="section-title">Відкриває технології</div>
          <div
            v-for="t in unlocksTechs"
            :key="t.name"
            class="unlock-item"
            @click="store.selectTech(t)"
          >
            {{ t.name }}
            <span class="req-level-badge" :class="{ unlocked: currentLevel >= t.reqLevel }">lvl {{ t.reqLevel }}</span>
          </div>
        </div>

        <!-- Components -->
        <div v-if="components.length" class="section">
          <div class="section-title">Компоненти ({{ components.length }})</div>
          <div v-for="c in components" :key="c.name" class="item-card" @click="toggleItem(c.name)">
            <div class="item-name">
              {{ c.name }}
              <span
                class="req-level-badge"
                :class="{ unlocked: currentLevel >= c.reqLevel }"
              >lvl {{ c.reqLevel }}</span>
            </div>
            <div v-if="expandedItems.has(c.name)" class="item-desc">{{ c.description }}</div>
          </div>
        </div>

        <!-- Facilities -->
        <div v-if="facilities.length" class="section">
          <div class="section-title">Споруди ({{ facilities.length }})</div>
          <div v-for="f in facilities" :key="f.name" class="item-card" @click="toggleItem(f.name)">
            <div class="item-name">
              {{ f.name }}
              <span
                class="req-level-badge"
                :class="{ unlocked: currentLevel >= f.reqLevel }"
              >lvl {{ f.reqLevel }}</span>
            </div>
            <div v-if="expandedItems.has(f.name)" class="item-desc">{{ f.description }}</div>
          </div>
        </div>

        <div v-if="!tech.requirements.length && !unlocksTechs.length && !components.length && !facilities.length" class="empty-note">
          Немає залежностей і розблокованих об'єктів для рівня 1.
        </div>
      </div>
    </template>
    <div v-else class="empty-panel">
      <div class="empty-hint">Натисни на технологію в графі або знайди компонент через пошук</div>
    </div>
  </aside>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useTechStore } from '../stores/techStore'

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

const unlocksTechs = computed(() => {
  if (!tech.value) return []
  return store.techs
    .filter(t => t.requirements.some(r => r.tech === tech.value.name))
    .map(t => ({ ...t, reqLevel: t.requirements.find(r => r.tech === tech.value.name).level }))
    .sort((a, b) => a.reqLevel - b.reqLevel)
})

const components = computed(() => {
  if (!tech.value) return []
  return store.unlockedComponents(tech.value.name)
})

const facilities = computed(() => {
  if (!tech.value) return []
  return store.unlockedFacilities(tech.value.name)
})

function incLevel() {
  if (tech.value && currentLevel.value < tech.value.maxLevel) {
    store.setResearchedLevel(tech.value.name, currentLevel.value + 1)
  }
}
function decLevel() {
  if (tech.value && currentLevel.value > 0) {
    store.setResearchedLevel(tech.value.name, currentLevel.value - 1)
  }
}

function selectReq(techName) {
  goToTech(techName)
}

function goToTech(techName) {
  const t = store.techs.find(t => t.name === techName)
  if (t) store.selectTech(t)
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
.detail-panel.open {
  width: 300px;
  min-width: 300px;
}

.empty-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
.empty-hint {
  color: var(--text-dim);
  font-size: 13px;
  text-align: center;
  padding: 20px;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.tech-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  padding-right: 24px;
  line-height: 1.3;
}
.tech-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.badge-cat {
  font-size: 11px;
  color: var(--text-dim);
  padding: 2px 0;
}
.close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  line-height: 1;
}
.close-btn:hover { color: var(--text); }

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.level-section {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 12px;
}
.level-label {
  font-size: 12px;
  color: var(--text-dim);
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}
.level-current {
  color: var(--accent);
  font-weight: 600;
}
.level-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.lvl-btn {
  width: 26px;
  height: 26px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  flex-shrink: 0;
}
.lvl-btn:disabled { opacity: 0.3; cursor: default; }
.level-track {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}
.level-pip {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.1s;
}
.level-pip.filled { background: var(--accent); border-color: var(--accent); }
.cost-label {
  font-size: 12px;
  color: var(--text-dim);
}

.section { display: flex; flex-direction: column; gap: 4px; }
.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  margin-bottom: 4px;
}

.req-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-card);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.1s;
}
.req-item:hover { background: var(--bg-hover); }
.req-item.met { border-color: var(--green); }
.req-item.met .req-icon { color: var(--green); }
.req-icon { font-size: 12px; color: var(--text-dim); }
.req-level { margin-left: auto; font-size: 11px; color: var(--text-dim); }

.unlock-item {
  padding: 6px 10px;
  background: var(--bg-card);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.1s;
}
.unlock-item:hover { background: var(--bg-hover); color: var(--accent); }

.item-card {
  padding: 7px 10px;
  background: var(--bg-card);
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.1s;
}
.item-card:hover { background: var(--bg-hover); }
.item-name {
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.req-level-badge {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--bg-hover);
  color: var(--text-dim);
  border: 1px solid var(--border);
  flex-shrink: 0;
}
.req-level-badge.unlocked {
  background: #1a3a2a;
  color: var(--green);
  border-color: var(--green);
}
.item-desc {
  font-size: 12px;
  color: var(--text-dim);
  margin-top: 6px;
  line-height: 1.5;
}

.empty-note {
  font-size: 12px;
  color: var(--text-dim);
  font-style: italic;
  text-align: center;
  padding: 8px;
}

.description-box {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 12px;
  font-size: 13px;
  color: var(--text-dim);
  line-height: 1.6;
}
</style>
