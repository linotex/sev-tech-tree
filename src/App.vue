<template>
  <div class="app-layout">
    <header class="topbar">
      <div class="app-title">
        <span class="title-icon">⬡</span>
        SEV Tech Tree
      </div>
      <div class="topbar-center">
        <span v-if="version" class="version-badge">v{{ version }}</span>
        <span class="stat">
          <span class="stat-val">{{ store.techs.length }}</span> технологій
        </span>
        <span class="stat">
          <span class="stat-val">{{ researchedCount }}</span> досліджено
        </span>
        <span v-if="store.selectedTech" class="stat-selected">
          ▶ {{ store.selectedTech.name }}
        </span>
      </div>
      <div class="topbar-actions">
        <button
          v-if="store.selectedTech"
          class="btn-research"
          :class="{ researched: currentResearchedLevel > 0 }"
          @click="store.toggleResearched(store.selectedTech.name)"
          :title="`Досліджено: ${currentResearchedLevel} / ${store.selectedTech.maxLevel}`"
        >
          {{ currentResearchedLevel > 0 ? '✓ Досліджено' : '○ Дослідити' }}
        </button>
        <button class="btn-reset" @click="resetProgress" title="Скинути прогрес">
          ↺ Скинути
        </button>
      </div>
    </header>

    <div class="main-content">
      <Sidebar />
      <TechGraph />
      <DetailPanel />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const version = ref('')
onMounted(async () => {
  if (window.app?.version) version.value = await window.app.version()
})
import { useTechStore } from './stores/techStore'
import Sidebar from './components/Sidebar.vue'
import TechGraph from './components/TechGraph.vue'
import DetailPanel from './components/DetailPanel.vue'

const store = useTechStore()

const researchedCount = computed(() =>
  Object.values(store.researchedLevels).filter(l => l > 0).length
)

const currentResearchedLevel = computed(() =>
  store.selectedTech ? store.getResearchedLevel(store.selectedTech.name) : 0
)

function resetProgress() {
  if (confirm('Скинути весь прогрес дослідження?')) {
    store.$patch({ researchedLevels: {} })
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 16px;
  height: 48px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--accent);
  white-space: nowrap;
}
.title-icon { font-size: 18px; }

.topbar-center {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.stat {
  font-size: 12px;
  color: var(--text-dim);
  white-space: nowrap;
}
.stat-val {
  color: var(--text);
  font-weight: 600;
}
.version-badge {
  font-size: 11px;
  color: var(--accent-dim);
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 2px 7px;
  border-radius: 10px;
}

.stat-selected {
  font-size: 12px;
  color: var(--accent);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-research, .btn-reset {
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  border: 1px solid var(--border);
  transition: all 0.15s;
}
.btn-research {
  background: var(--bg-card);
  color: var(--text-dim);
}
.btn-research:hover { background: var(--bg-hover); color: var(--text); }
.btn-research.researched {
  background: #1a3a2a;
  border-color: var(--green);
  color: var(--green);
}
.btn-reset {
  background: var(--bg-card);
  color: var(--text-dim);
}
.btn-reset:hover { background: var(--bg-hover); color: var(--text); }

.main-content {
  display: flex;
  flex: 1;
  min-height: 0;
}
</style>
