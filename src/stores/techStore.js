import { defineStore } from 'pinia'
import { lang, setLang } from '../i18n.js'

import techTreeUk from '@parsed/tech_tree_uk.json'
import techTreeEn from '@parsed/tech_tree_en.json'
import componentsUk from '@parsed/components_uk.json'
import componentsEn from '@parsed/components_en.json'
import facilitiesUk from '@parsed/facilities_uk.json'
import facilitiesEn from '@parsed/facilities_en.json'
import empireBonusesUk from '@parsed/empire_bonuses_uk.json'
import empireBonusesEn from '@parsed/empire_bonuses_en.json'
import vehicleSizesUk from '@parsed/vehicle_sizes_uk.json'
import vehicleSizesEn from '@parsed/vehicle_sizes_en.json'

const dataByLang = {
  uk: { techs: techTreeUk, components: componentsUk, facilities: facilitiesUk, empireBonuses: empireBonusesUk, vehicleSizes: vehicleSizesUk },
  en: { techs: techTreeEn, components: componentsEn, facilities: facilitiesEn, empireBonuses: empireBonusesEn, vehicleSizes: vehicleSizesEn },
}

export const useTechStore = defineStore('tech', {
  state: () => ({
    techs: techTreeUk,
    components: componentsUk,
    facilities: facilitiesUk,
    empireBonuses: empireBonusesUk,
    vehicleSizes: vehicleSizesUk,
    researchedLevels: {}, // { techName: currentLevel }
    selectedTech: null,
    selectedItem: null, // { type: 'component'|'facility', data: {...} }
    filterGroup: null,
    filterCategory: null,
    searchQuery: '',
    highlightPath: null, // set of tech names on path to selected
    currentView: 'techs', // 'techs' | 'components' | 'facilities'
    itemFilterGroup: null
  }),

  getters: {
    groups: (state) => [...new Set(state.techs.map(t => t.group))].sort(),

    componentGroups: (state) => [...new Set(state.components.map(c => c.group))].sort(),
    facilityGroups: (state) => [...new Set(state.facilities.map(f => f.group))].sort(),
    vehicleSizeTypes: (state) => [...new Set(state.vehicleSizes.map(v => v.shipType))],

    filteredVehicleSizes: (state) => {
      let result = state.vehicleSizes
      if (state.itemFilterGroup) result = result.filter(v => v.shipType === state.itemFilterGroup)
      if (state.searchQuery) {
        const q = state.searchQuery.toLowerCase()
        result = result.filter(v => v.name.toLowerCase().includes(q))
      }
      return result
    },

    // Vehicle sizes unlocked by a specific tech
    unlockedVehicleSizes: (state) => (techName) => {
      return state.vehicleSizes
        .filter(v => v.techReq?.tech === techName)
        .map(v => ({ ...v, reqLevel: v.techReq.level }))
    },

    filteredComponents: (state) => {
      let result = state.components
      if (state.itemFilterGroup) result = result.filter(c => c.group === state.itemFilterGroup)
      if (state.searchQuery) {
        const q = state.searchQuery.toLowerCase()
        result = result.filter(c => c.name.toLowerCase().includes(q))
      }
      return result
    },

    filteredFacilities: (state) => {
      let result = state.facilities
      if (state.itemFilterGroup) result = result.filter(f => f.group === state.itemFilterGroup)
      if (state.searchQuery) {
        const q = state.searchQuery.toLowerCase()
        result = result.filter(f => f.name.toLowerCase().includes(q))
      }
      return result
    },

    categoriesForGroup: (state) => (group) => {
      return [...new Set(
        state.techs
          .filter(t => t.group === group)
          .map(t => t.category)
      )].sort()
    },

    filteredTechs: (state) => {
      let result = state.techs
      if (state.filterGroup) result = result.filter(t => t.group === state.filterGroup)
      if (state.filterCategory) result = result.filter(t => t.category === state.filterCategory)
      if (state.searchQuery) {
        const q = state.searchQuery.toLowerCase()
        result = result.filter(t => t.name.toLowerCase().includes(q))
      }
      return result
    },

    searchResults: (state) => {
      if (!state.searchQuery) return null
      const q = state.searchQuery.toLowerCase()
      return {
        techs: state.techs.filter(t => t.name.toLowerCase().includes(q)),
        components: state.components.filter(c => c.name.toLowerCase().includes(q)),
        facilities: state.facilities.filter(f => f.name.toLowerCase().includes(q)),
        vehicles: state.vehicleSizes.filter(v => v.name.toLowerCase().includes(q))
      }
    },

    getResearchedLevel: (state) => (techName) => {
      return state.researchedLevels[techName] || 0
    },

    isResearched: (state) => (techName) => {
      return (state.researchedLevels[techName] || 0) > 0
    },

    isUnlocked: (state) => (tech) => {
      // All requirements met at current researched levels
      return tech.requirements.every(req => {
        return (state.researchedLevels[req.tech] || 0) >= req.level
      })
    },

    // Components unlocked by a specific tech (with required level)
    unlockedComponents: (state) => (techName) => {
      return state.components
        .filter(c => c.requirements.some(r => r.tech === techName))
        .map(c => ({ ...c, reqLevel: c.requirements.find(r => r.tech === techName).level }))
        .sort((a, b) => a.reqLevel - b.reqLevel)
    },

    // Empire bonuses unlocked by a specific tech
    unlockedBonuses: (state) => (techName) => {
      return state.empireBonuses
        .filter(b => b.requirements.some(r => r.tech === techName))
        .map(b => ({ ...b, reqLevel: b.requirements.find(r => r.tech === techName).level }))
        .sort((a, b) => a.reqLevel - b.reqLevel)
    },

    // Facilities unlocked by a specific tech (with required level)
    unlockedFacilities: (state) => (techName) => {
      return state.facilities
        .filter(f => f.requirements.some(r => r.tech === techName))
        .map(f => ({ ...f, reqLevel: f.requirements.find(r => r.tech === techName).level }))
        .sort((a, b) => a.reqLevel - b.reqLevel)
    },

    // All prerequisites path to research a tech (BFS)
    prerequisitePath: (state) => (techName) => {
      const visited = new Set()
      const queue = [techName]
      while (queue.length) {
        const name = queue.shift()
        if (visited.has(name)) continue
        visited.add(name)
        const tech = state.techs.find(t => t.name === name)
        if (tech) {
          tech.requirements.forEach(r => queue.push(r.tech))
        }
      }
      visited.delete(techName)
      return visited
    },

    // Total research cost to reach a tech from scratch
    totalResearchCost: (state) => (techName) => {
      const visited = new Set()
      const queue = [techName]
      let total = 0
      while (queue.length) {
        const name = queue.shift()
        if (visited.has(name)) continue
        visited.add(name)
        const tech = state.techs.find(t => t.name === name)
        if (tech) {
          const currentLevel = state.researchedLevels[name] || 0
          const neededLevel = name === techName ? 1 : 1
          if (currentLevel < neededLevel) {
            total += tech.costPerLevel * (neededLevel - currentLevel)
          }
          tech.requirements.forEach(r => queue.push(r.tech))
        }
      }
      return total
    }
  },

  actions: {
    setLanguage(l) {
      const data = dataByLang[l]
      if (!data) return
      setLang(l)
      this.$patch({
        techs: data.techs,
        components: data.components,
        facilities: data.facilities,
        empireBonuses: data.empireBonuses,
        vehicleSizes: data.vehicleSizes,
        selectedTech: null,
        selectedItem: null,
        highlightPath: null,
        currentView: 'techs',
        itemFilterGroup: null,
      })
    },

    selectTech(tech) {
      this.selectedTech = tech
      this.selectedItem = null
      if (tech) {
        this.highlightPath = this.prerequisitePath(tech.name)
      } else {
        this.highlightPath = null
      }
    },

    selectItem(data, type) {
      this.selectedItem = data ? { type, data } : null
      this.selectedTech = null
      this.highlightPath = null
    },

    setResearchedLevel(techName, level) {
      const tech = this.techs.find(t => t.name === techName)
      if (!tech) return
      const clamped = Math.max(0, Math.min(level, tech.maxLevel))
      if (clamped === 0) {
        delete this.researchedLevels[techName]
      } else {
        this.researchedLevels[techName] = clamped
      }
    },

    toggleResearched(techName) {
      const current = this.researchedLevels[techName] || 0
      const tech = this.techs.find(t => t.name === techName)
      if (!tech) return
      if (current === 0) {
        this.researchedLevels[techName] = 1
      } else if (current < tech.maxLevel) {
        this.researchedLevels[techName] = current + 1
      } else {
        delete this.researchedLevels[techName]
      }
    },

    setFilter(group, category = null) {
      this.filterGroup = group
      this.filterCategory = category
    },

    clearFilter() {
      this.filterGroup = null
      this.filterCategory = null
    },

    setView(v) {
      this.currentView = v
      this.itemFilterGroup = null
      this.selectedTech = null
      this.selectedItem = null
      this.highlightPath = null
      this.searchQuery = ''
    },

    setItemFilterGroup(group) {
      this.itemFilterGroup = this.itemFilterGroup === group ? null : group
    }
  }
})
