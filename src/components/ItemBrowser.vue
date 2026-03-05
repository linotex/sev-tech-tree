<template>
  <div class="item-browser">
    <template v-if="items.length === 0">
      <div class="empty">{{ t('no_results') }}</div>
    </template>

    <!-- Grouped view (no filter) -->
    <template v-else-if="!store.itemFilterGroup && !store.searchQuery">
      <div
        v-for="group in visibleGroups"
        :key="group"
        class="group-block"
      >
        <div class="group-header">
          <span class="group-dot" :style="{ background: groupColor }" />
          {{ group }}
          <span class="group-cnt">{{ itemsInGroup(group).length }}</span>
        </div>
        <div
          v-for="item in itemsInGroup(group)"
          :key="item.name"
          class="item-row"
          :class="{ selected: store.selectedItem?.data?.name === item.name }"
          @click="selectItem(item)"
        >
          <span class="status-dot" :class="isUnlocked(item) ? 'unlocked' : 'locked'" />
          <span class="item-name">{{ item.name }}</span>
          <span v-if="isVehicle && vehicleTonnage(item) != null" class="tonnage-badge">
            {{ vehicleTonnage(item) }}{{ t('stat_tonnage_short') }}
          </span>
          <span v-else-if="!isVehicle && item.requirements.length" class="req-tags">
            <span v-for="r in item.requirements.slice(0, 2)" :key="r.tech" class="req-tag">
              {{ shortName(r.tech) }} {{ r.level }}
            </span>
          </span>
        </div>
      </div>
    </template>

    <!-- Flat view (group filter or search active) -->
    <template v-else>
      <div
        v-for="item in items"
        :key="item.name"
        class="item-row flat"
        :class="{ selected: store.selectedItem?.data?.name === item.name }"
        @click="selectItem(item)"
      >
        <span class="status-dot" :class="isUnlocked(item) ? 'unlocked' : 'locked'" />
        <span class="item-name">{{ item.name }}</span>
        <span v-if="!store.itemFilterGroup" class="group-tag">{{ groupKey(item) }}</span>
        <span v-if="isVehicle && vehicleTonnage(item) != null" class="tonnage-badge">
          {{ vehicleTonnage(item) }}{{ t('stat_tonnage_short') }}
        </span>
        <span v-else-if="!isVehicle && item.requirements.length" class="req-tags">
          <span v-for="r in item.requirements.slice(0, 2)" :key="r.tech" class="req-tag">
            {{ shortName(r.tech) }} {{ r.level }}
          </span>
        </span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTechStore } from '../stores/techStore'
import { evalFormula } from '../formulaUtil.js'
import { t } from '../i18n.js'

const props = defineProps({
  type: { type: String, required: true } // 'component' | 'facility' | 'vehicle'
})

const store = useTechStore()

const isVehicle = computed(() => props.type === 'vehicle')

const items = computed(() => {
  if (props.type === 'component') {
    return store.filteredComponents.slice().sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
  }
  if (props.type === 'facility') {
    return store.filteredFacilities.slice().sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
  }
  return store.filteredVehicleSizes
})

const groupColor = computed(() =>
  props.type === 'component' ? '#34d399' : props.type === 'facility' ? '#fb923c' : '#60a5fa'
)

// For vehicles, group by shipType; for others, group by group
const groupKey = (item) => isVehicle.value ? item.shipType : item.group

const visibleGroups = computed(() => {
  const seen = new Set()
  const groups = items.value.map(i => groupKey(i)).filter(g => seen.has(g) ? false : seen.add(g))
  if (!isVehicle.value) groups.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
  return groups
})

function itemsInGroup(group) {
  const filtered = items.value.filter(i => groupKey(i) === group)
  if (isVehicle.value) {
    return filtered.slice().sort((a, b) => {
      const ta = evalFormula(a.formulas.tonnage, 1) ?? 0
      const tb = evalFormula(b.formulas.tonnage, 1) ?? 0
      return ta - tb
    })
  }
  return filtered.slice().sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))
}

function isUnlocked(item) {
  if (isVehicle.value) {
    if (!item.techReq) return true
    return (store.researchedLevels[item.techReq.tech] || 0) >= item.techReq.level
  }
  return item.requirements.every(r =>
    (store.researchedLevels[r.tech] || 0) >= r.level
  )
}

// For vehicles: show current tonnage based on researched tech level
function vehicleTonnage(item) {
  if (!item.techReq) return null
  const techLevel = store.researchedLevels[item.techReq.tech] || 0
  if (techLevel === 0) return null
  return evalFormula(item.formulas.tonnage, techLevel)
}

function shortName(name) {
  if (name.length <= 12) return name
  return name.slice(0, 11) + '…'
}

function selectItem(item) {
  if (isVehicle.value) {
    store.selectItem(item, 'vehicle')
  } else {
    store.selectItem(item, props.type)
  }
}
</script>

<style scoped>
.item-browser {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-dim);
  font-size: 13px;
}

/* Grouped layout */
.group-block {
  margin-bottom: 2px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-dim);
  position: sticky;
  top: 0;
  background: var(--bg-deep);
  z-index: 1;
}

.group-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.group-cnt {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-dim);
  background: var(--bg-card);
  padding: 1px 5px;
  border-radius: 8px;
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}

/* Item rows */
.item-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-dim);
  transition: background 0.1s, color 0.1s;
  min-height: 30px;
}
.item-row:hover { background: var(--bg-hover); color: var(--text); }
.item-row.selected { background: var(--bg-hover); color: var(--text); }
.item-row.flat { border-bottom: 1px solid var(--border); }

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.unlocked { background: var(--green); }
.status-dot.locked   { background: #374151; border: 1px solid #4b5563; }

.item-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-tag {
  font-size: 10px;
  color: var(--text-dim);
  background: var(--bg-card);
  padding: 1px 6px;
  border-radius: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}

.req-tags {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.req-tag {
  font-size: 10px;
  color: #60a5fa;
  background: #1e3a5f;
  padding: 1px 5px;
  border-radius: 4px;
  white-space: nowrap;
}

.tonnage-badge {
  font-size: 11px;
  font-weight: 600;
  color: #60a5fa;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>
