import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('app', {
  version: () => ipcRenderer.invoke('get-version')
})
