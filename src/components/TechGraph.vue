<template>
  <div class="graph-wrap">
    <div ref="cyEl" class="cy-container" />
    <div class="graph-controls">
      <button @click="panHome" title="На початок">⌂</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'
import { useTechStore } from '../stores/techStore'

cytoscape.use(dagre)

const store = useTechStore()
const { filteredTechs, selectedTech, highlightPath, researchedLevels } = storeToRefs(store)

const cyEl = ref(null)
let cy = null

const GROUP_COLORS = {
  'Культура':            '#c084fc',
  'Теоретические науки': '#60a5fa',
  'Прикладные науки':    '#34d399',
  'Вооружение':          '#fb923c'
}

function nodeColor(tech) {
  return GROUP_COLORS[tech.group] || '#94a3b8'
}

function buildElements(techs) {
  const techSet = new Set(techs.map(t => t.name))
  const nodes = techs.map(t => ({
    data: {
      id: t.name,
      label: t.name,
      group: t.group,
      color: nodeColor(t),
      maxLevel: t.maxLevel,
      researched: store.getResearchedLevel(t.name)
    }
  }))

  const edges = []
  techs.forEach(t => {
    t.requirements.forEach(r => {
      if (techSet.has(r.tech)) {
        edges.push({
          data: {
            id: `${r.tech}->${t.name}`,
            source: r.tech,
            target: t.name,
            reqLevel: r.level
          }
        })
      }
    })
  })

  return [...nodes, ...edges]
}

function initCy() {
  if (!cyEl.value) return
  cy = cytoscape({
    container: cyEl.value,
    elements: buildElements(filteredTechs.value),
    style: getCyStyle(),
    layout: { name: 'dagre', rankDir: 'LR', nodeSep: 40, rankSep: 120, padding: 30 },
    zoom: 1,
    userZoomingEnabled: false,
    minZoom: 1,
    maxZoom: 1,
  })

  panHome()

  // Wheel → pan (no zoom)
  cyEl.value.addEventListener('wheel', (e) => {
    e.preventDefault()
    cy.panBy({ x: -e.deltaX, y: -e.deltaY })
  }, { passive: false })

  cy.on('tap', 'node', (evt) => {
    const techName = evt.target.id()
    const tech = store.techs.find(t => t.name === techName)
    store.selectTech(tech)
  })

  cy.on('tap', (evt) => {
    if (evt.target === cy) store.selectTech(null)
  })

  applyHighlight()
}

function getCyStyle() {
  return [
    {
      selector: 'node',
      style: {
        'background-color': 'data(color)',
        'background-opacity': 0.15,
        'border-color': 'data(color)',
        'border-width': 2,
        'label': 'data(label)',
        'color': '#e0e6f0',
        'font-size': 11,
        'text-wrap': 'wrap',
        'text-max-width': 120,
        'text-valign': 'center',
        'text-halign': 'center',
        'width': 130,
        'height': 40,
        'shape': 'round-rectangle',
        'padding': 8
      }
    },
    {
      selector: 'node.researched',
      style: {
        'background-opacity': 0.55,
        'border-width': 3
      }
    },
    {
      selector: 'node.selected',
      style: {
        'background-opacity': 0.8,
        'border-width': 3,
        'border-color': '#ffffff',
        'color': '#ffffff',
        'font-weight': 'bold'
      }
    },
    {
      selector: 'node.prereq',
      style: {
        'background-opacity': 0.45,
        'border-width': 2.5
      }
    },
    {
      selector: 'node.dimmed',
      style: {
        'background-opacity': 0.05,
        'border-opacity': 0.2,
        'color': '#3a4a5a'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 1.5,
        'line-color': '#2a3a5a',
        'target-arrow-color': '#2a3a5a',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'arrow-scale': 0.8,
        'opacity': 0.6
      }
    },
    {
      selector: 'edge.highlighted',
      style: {
        'line-color': '#4a9eff',
        'target-arrow-color': '#4a9eff',
        'width': 2.5,
        'opacity': 1
      }
    },
    {
      selector: 'edge.dimmed',
      style: { 'opacity': 0.1 }
    }
  ]
}

function applyHighlight() {
  if (!cy) return
  cy.batch(() => {
    cy.elements().removeClass('selected prereq dimmed highlighted researched')

    // Mark researched
    Object.entries(researchedLevels.value).forEach(([name, lvl]) => {
      if (lvl > 0) cy.$id(name).addClass('researched')
    })

    if (!selectedTech.value) return

    const selectedName = selectedTech.value.name
    const prereqs = highlightPath.value || new Set()

    cy.nodes().forEach(n => {
      const id = n.id()
      if (id === selectedName) n.addClass('selected')
      else if (prereqs.has(id)) n.addClass('prereq')
      else n.addClass('dimmed')
    })

    cy.edges().forEach(e => {
      const src = e.data('source')
      const tgt = e.data('target')
      if (prereqs.has(src) && (prereqs.has(tgt) || tgt === selectedName)) {
        e.addClass('highlighted')
      } else if (!prereqs.has(src) && src !== selectedName) {
        e.addClass('dimmed')
      }
    })
  })
}

function rebuildGraph() {
  if (!cy) { initCy(); return }
  cy.elements().remove()
  cy.add(buildElements(filteredTechs.value))
  const layout = cy.layout({ name: 'dagre', rankDir: 'LR', nodeSep: 40, rankSep: 120, padding: 30 })
  cy.one('layoutstop', () => { panHome(); applyHighlight() })
  layout.run()
}

// Pan so the left edge of the graph is visible with padding, vertically centred
function panHome() {
  if (!cy || !cyEl.value) return
  const bb = cy.elements().boundingBox()
  cy.pan({
    x: 30 - bb.x1,
    y: cyEl.value.clientHeight / 2 - (bb.y1 + bb.h / 2)
  })
}

watch(filteredTechs, rebuildGraph, { deep: true })
watch([selectedTech, highlightPath, researchedLevels], applyHighlight, { deep: true })

let dpiCleanup = null

function watchDPI() {
  const mq = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`)
  const handler = () => {
    cy?.resize()
    dpiCleanup?.()
    dpiCleanup = watchDPI()
  }
  mq.addEventListener('change', handler, { once: true })
  return () => mq.removeEventListener('change', handler)
}

onMounted(() => {
  initCy()
  dpiCleanup = watchDPI()
})

onUnmounted(() => {
  dpiCleanup?.()
  cy?.destroy()
})
</script>

<style scoped>
.graph-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}
.cy-container {
  width: 100%;
  height: 100%;
  background: var(--bg-deep);
}
.graph-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.graph-controls button {
  width: 32px;
  height: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.graph-controls button:hover { background: var(--bg-hover); }
</style>
