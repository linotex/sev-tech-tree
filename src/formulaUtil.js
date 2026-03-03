/**
 * Evaluates a Space Empires V formula string at a given level.
 * Handles: [%Level%], [%Range%], Мин(), Макс(), iif().
 * Returns a rounded integer, or null if the formula cannot be evaluated.
 */
export function evalFormula(formula, level, range = 0) {
  if (!formula || formula === '0') return 0

  const expr = formula
    .replace(/\[%Level%\]/g, level)
    .replace(/\[%Range%\]/g, range)
    .replace(/\bМин\b/g, 'Math.min')
    .replace(/\bМакс\b/g, 'Math.max')
    .replace(/\biif\s*\(/gi, '_iif(')

  try {
    // eslint-disable-next-line no-new-func
    return Math.round(new Function('_iif', `return (${expr})`)((c, t, f) => (c ? t : f)))
  } catch {
    return null
  }
}

/**
 * Renders an ability description, substituting [%Amount1%] and [%Amount2%]
 * with computed values at the given level.
 */
export function renderAbilityDesc(ability, level) {
  let desc = ability.description || ''
  if (!desc) return ''

  const a1 = evalFormula(ability.amount1, level)
  const a2 = evalFormula(ability.amount2, level)

  if (a1 !== null) desc = desc.replace(/\[%Amount1%\]/g, a1)
  if (a2 !== null) desc = desc.replace(/\[%Amount2%\]/g, a2)

  return desc
}

/**
 * Returns the effective display level for a component/facility,
 * clamped to its maxLevel and always at least 1.
 */
export function effectiveLevel(item, techLevel) {
  return Math.max(1, Math.min(techLevel || 1, item.maxLevel || 1))
}
