// Electron API 类型定义
export interface ElectronAPI {
  // 文件夹选择
  selectFolder: () => Promise<string | null>

  // 文件选择
  selectFiles: (options?: any) => Promise<string[]>

  // API 调用
  scanFolder: (folderPath: string, includeSubfolders?: boolean) => Promise<{
    success: boolean
    data?: any
    error?: string
  }>

  identifyBirds: (photoPaths: string[]) => Promise<{
    success: boolean
    data?: any
    error?: string
  }>

  getDailyMap: (mapDate: string, photoLocations?: any[]) => Promise<{
    success: boolean
    data?: any
    error?: string
  }>

  getSpeciesList: () => Promise<{
    success: boolean
    data?: any
    error?: string
  }>

  // 测试 LLM 连接
  testLLMConnection: (config: {
    baseUrl: string
    apiKey: string
    model: string
    timeout: number
  }) => Promise<{
    success: boolean
    message?: string
  }>

  // 系统功能
  openExternal: (url: string) => Promise<void>
  getAppPath: (name: string) => Promise<string>
  checkBackend: () => Promise<{
    success: boolean
    error?: string
  }>

  // 版本信息
  platform: string
  versions: {
    node: string
    chrome: string
    electron: string
  }
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

export {}
