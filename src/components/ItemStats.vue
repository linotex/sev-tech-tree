<template>
  <div class="item-stats">
    <div class="stats-level-badge">{{ t('stat_level_prefix') }} {{ level }}</div>

    <!-- Core stats row -->
    <div class="stats-row">
      <span class="stat-chip">
        <span class="stat-label">{{ t('stat_size') }}</span>
        {{ evalFormula(item.formulas.size, level) }}t
      </span>
      <span class="stat-chip">
        <span class="stat-label">{{ t('stat_structure') }}</span>
        {{ evalFormula(item.formulas.structure, level) }} HP
      </span>
    </div>

    <!-- Cost row — only show non-zero values -->
    <div class="cost-row">
      <span v-if="minerals"              class="cost-chip minerals"><b>{{ t('res_min') }}</b> {{ minerals }}</span>
      <span v-if="organics"              class="cost-chip organics"><b>{{ t('res_org') }}</b> {{ organics }}</span>
      <span v-if="radioactives"          class="cost-chip radio"   ><b>{{ t('res_rad') }}</b> {{ radioactives }}</span>
      <span v-if="showFuel && fuel"      class="cost-chip fuel"    ><b>{{ t('res_fuel') }}</b> {{ fuel }}</span>
      <span v-if="showFuel && ammo"      class="cost-chip ammo"    ><b>{{ t('res_ammo') }}</b> {{ ammo }}</span>
    </div>

    <!-- Abilities -->
    <div v-if="renderedAbilities.length" class="abilities">
      <div v-for="(ab, i) in renderedAbilities" :key="i" class="ability-line">
        {{ ab }}
      </div>
    </div>

    <!-- Weapon damage -->
    <div v-if="item.weapon && (minDmg !== null || maxDmg !== null)" class="weapon-row">
      <span class="stat-label">{{ t('stat_damage') }}</span>
      <span class="dmg-value">
        {{ minDmg === maxDmg ? minDmg : `${minDmg}–${maxDmg}` }}
        <span class="dmg-note">({{ t('stat_pt_blank') }})</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { t } from '../i18n.js'
import { evalFormula, renderAbilityDesc } from '../formulaUtil.js'

const props = defineProps({
  item: { type: Object, required: true },
  level: { type: Number, required: true },
  showFuel: { type: Boolean, default: false },
})

const f = computed(() => props.item.formulas || {})
const l = computed(() => props.level)

const minerals     = computed(() => evalFormula(f.value.minerals, l.value) || 0)
const organics     = computed(() => evalFormula(f.value.organics, l.value) || 0)
const radioactives = computed(() => evalFormula(f.value.radioactives, l.value) || 0)
const fuel         = computed(() => evalFormula(f.value.fuel, l.value) || 0)
const ammo         = computed(() => evalFormula(f.value.ammo, l.value) || 0)

const renderedAbilities = computed(() => {
  return (props.item.abilities || [])
    .map(ab => renderAbilityDesc(ab, l.value))
    .filter(Boolean)
})

const minDmg = computed(() =>
  props.item.weapon ? evalFormula(props.item.weapon.minDamageFormula, l.value, 0) : null
)
const maxDmg = computed(() =>
  props.item.weapon ? evalFormula(props.item.weapon.maxDamageFormula, l.value, 0) : null
)
</script>

<style scoped>
.item-stats {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stats-level-badge {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--accent-dim);
  font-weight: 600;
}

.stats-row {
  display: flex;
  gap: 6px;
}

.stat-chip {
  display: flex;
  align-items: baseline;
  gap: 4px;
  background: var(--bg-deep);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 3px 7px;
  font-size: 12px;
  color: var(--text);
}
.stat-label {
  font-size: 10px;
  color: var(--text-dim);
}

.cost-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.cost-chip {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--bg-deep);
}
.cost-chip.minerals    { color: #94a3b8; }
.cost-chip.organics    { color: #34d399; }
.cost-chip.radio       { color: #fb923c; }
.cost-chip.fuel        { color: #60a5fa; }
.cost-chip.ammo        { color: #f87171; }

.abilities {
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

.weapon-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-dim);
}
.dmg-value {
  color: #f87171;
  font-weight: 600;
  font-size: 13px;
}
.dmg-note {
  font-size: 10px;
  color: var(--text-dim);
  font-weight: 400;
}
</style>
