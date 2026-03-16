const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 文件夹选择
  selectFolder: () => ipcRenderer.invoke('select-folder'),

  // 文件选择
  selectFiles: (options) => ipcRenderer.invoke('select-files', options),

  // API 调用
  scanFolder: (folderPath, includeSubfolders) =>
    ipcRenderer.invoke('scan-folder', { folderPath, includeSubfolders }),

  identifyBirds: (photoPaths) =>
    ipcRenderer.invoke('identify-birds', photoPaths),

  getDailyMap: (mapDate, photoLocations) =>
    ipcRenderer.invoke('get-daily-map', mapDate, photoLocations),

  getSpeciesList: () => ipcRenderer.invoke('get-species-list'),

  // 测试 LLM 连接
  testLLMConnection: (config) => ipcRenderer.invoke('test-llm-connection', config),

  // 系统功能
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  getAppPath: (name) => ipcRenderer.invoke('get-app-path', name),
  checkBackend: () => ipcRenderer.invoke('check-backend'),

  // 版本信息
  platform: process.platform,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron,
  },
})
