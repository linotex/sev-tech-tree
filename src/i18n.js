import { ref } from 'vue'
import uk from './locales/uk.json'
import en from './locales/en.json'

const locales = { uk, en }

export const lang = ref('uk')

export function t(key) {
  return locales[lang.value]?.[key] ?? key
}

export function setLang(l) {
  if (locales[l]) lang.value = l
}
