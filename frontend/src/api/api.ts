// API 调用 - 支持 Electron IPC 和 HTTP

const API_BASE_URL = 'http://localhost:8000'

// 获取保存的 LLM API 配置
function getLLMConfig() {
  const configStr = localStorage.getItem('llm_api_config')
  if (configStr) {
    try {
      return JSON.parse(configStr)
    } catch (e) {
      console.error('Failed to load LLM config:', e)
    }
  }
  return null
}

// 检查是否已配置 LLM Key
export function checkLLMConfigured(): { configured: boolean; config: any } {
  const config = getLLMConfig()
  if (!config || !config.apiKey) {
    return { configured: false, config: null }
  }
  return { configured: true, config }
}

// 抛出未配置错误
export function throwLLMConfigError() {
  const error = new Error('请先配置大模型 API')
  error.name = 'LLM_CONFIG_REQUIRED'
  throw error
}

export const scanApi = {
  scan: async (folderPath: string, includeSubfolders = true) => {
    // 优先使用 Electron IPC
    if (window.electronAPI) {
      const result = await window.electronAPI.scanFolder(folderPath, includeSubfolders)
      if (!result.success) {
        throw new Error(result.error)
      }
      return { data: result.data }
    }

    // Web 模式：调用后端 HTTP API
    const response = await fetch(`${API_BASE_URL}/api/scan/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_path: folderPath, include_subfolders: includeSubfolders }),
    })

    if (!response.ok) {
      throw new Error(`扫描失败：${response.statusText}`)
    }

    return { data: await response.json() }
  },

  getSupportedFormats: async () => {
    const response = await fetch(`${API_BASE_URL}/api/scan/supported-formats`)
    return { data: await response.json() }
  }
}

export const scoringApi = {
  get_default_criteria: async () => {
    const response = await fetch(`${API_BASE_URL}/api/scoring/criteria/defaults`)
    return { data: await response.json() }
  },

  batch_score: async (imagePaths: string[], criteria?: { focus_weight: number; clarity_weight: number; composition_weight: number }) => {
    const { configured, config } = checkLLMConfigured()
    if (!configured) {
      throwLLMConfigError()
    }

    // 添加重试逻辑
    const maxRetries = 2
    let lastError: any = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/scoring/batch-score`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_paths: imagePaths,
            criteria: criteria || {
              focus_weight: 0.40,
              clarity_weight: 0.35,
              composition_weight: 0.25
            },
            llm_config: {
              base_url: config.baseUrl,
              api_key: config.apiKey,
              model: config.model,
              timeout: config.timeout || 60,
            },
            // 启用校验和重试
            enable_validation: true,
            max_retries: maxRetries - attempt,
          }),
        })

        if (!response.ok) {
          const error = await response.text()
          // 如果是 LLM 幻觉校验失败，自动重试
          if (response.status === 422) {
            lastError = new Error('LLM 返回格式无效，正在重试...')
            continue
          }
          throw new Error(`评分失败：${error}`)
        }

        return { data: await response.json() }
      } catch (err: any) {
        lastError = err
        if (attempt < maxRetries) {
          // 等待指数退避时间后重试
          await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)))
          continue
        }
      }
    }

    throw lastError
  }
}

export const summaryApi = {
  generate_summary: async (sessionId: number, outputPath?: string) => {
    const response = await fetch(`${API_BASE_URL}/api/summary/generate-summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        output_path: outputPath,
      }),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`生成小结失败：${error}`)
    }

    return { data: await response.json() }
  },

  get_calendar: async (year: number, month: number) => {
    const response = await fetch(`${API_BASE_URL}/api/summary/calendar/${year}/${month}`)
    if (!response.ok) {
      throw new Error(`获取日历失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  get_session: async (sessionId: number) => {
    const response = await fetch(`${API_BASE_URL}/api/summary/summary/${sessionId}`)
    if (!response.ok) {
      throw new Error(`获取会话详情失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  get_sessions: async (limit = 50, offset = 0) => {
    const response = await fetch(`${API_BASE_URL}/api/summary/sessions?limit=${limit}&offset=${offset}`)
    if (!response.ok) {
      throw new Error(`获取会话列表失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  get_yearly_summary: async (year: number) => {
    const response = await fetch(`${API_BASE_URL}/api/summary/yearly-summary/${year}`)
    if (!response.ok) {
      throw new Error(`获取年度摘要失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  get_species_list: async () => {
    const response = await fetch(`${API_BASE_URL}/api/summary/species/list`)
    if (!response.ok) {
      throw new Error(`获取物种列表失败：${response.statusText}`)
    }
    return { data: await response.json() }
  }
}

export const birdsApi = {
  identify: async (photoPaths: string[]) => {
    // 优先使用 Electron API
    if (window.electronAPI) {
      const result = await window.electronAPI.identifyBirds(photoPaths)
      if (!result.success) {
        throw new Error(result.error)
      }
      return { data: result.data }
    }

    // Web 模式：调用后端 HTTP API
    const response = await fetch(`${API_BASE_URL}/api/birds/identify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ photo_paths: photoPaths }),
    })

    if (!response.ok) {
      throw new Error(`识别失败：${response.statusText}`)
    }

    return { data: await response.json() }
  },

  getSpeciesList: async () => {
    if (window.electronAPI) {
      const result = await window.electronAPI.getSpeciesList()
      if (!result.success) {
        throw new Error(result.error)
      }
      return { data: result.data }
    }

    const response = await fetch(`${API_BASE_URL}/api/birds/species-list`)
    return { data: await response.json() }
  },

  detectBird: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/birds/detect-bird`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('检测失败')
    }

    return { data: await response.json() }
  },

  // 使用大模型 API 进行识别
  identifyWithLLM: async (imagePath: string) => {
    const { configured, config } = checkLLMConfigured()
    if (!configured) {
      throwLLMConfigError()
    }

    const maxRetries = 2
    let lastError: any = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/llm/llm-identify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_path: imagePath,
            config: {
              base_url: config.baseUrl,
              api_key: config.apiKey,
              model: config.model,
              timeout: config.timeout,
            },
            enable_validation: true,
          }),
        })

        if (!response.ok) {
          const error = await response.text()
          if (response.status === 422) {
            lastError = new Error('LLM 返回格式无效，正在重试...')
            continue
          }
          throw new Error(`LLM 识别失败：${error}`)
        }

        return { data: await response.json() }
      } catch (err: any) {
        lastError = err
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)))
          continue
        }
      }
    }

    throw lastError
  },

  getBurstGroups: async (photoPaths: string[], timeThreshold = 5) => {
    if (window.electronAPI) {
      return { data: { burst_groups: [] } }
    }

    const response = await fetch(`${API_BASE_URL}/api/birds/burst-groups`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ photo_paths: photoPaths, time_threshold: timeThreshold }),
    })

    return { data: await response.json() }
  }
}

export const exportApi = {
  exportPhotos: async (sessionId?: number, format: string = 'xlsx') => {
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId.toString())
    params.append('format', format)

    const url = `${API_BASE_URL}/api/export/photos?${params.toString()}`
    // 直接返回下载链接，由前端触发下载
    return { downloadUrl: url }
  },

  exportDetections: async (sessionId?: number, format: string = 'xlsx') => {
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId.toString())
    params.append('format', format)

    const url = `${API_BASE_URL}/api/export/detections?${params.toString()}`
    return { downloadUrl: url }
  },

  exportSummary: async (sessionId: number, format: string = 'xlsx') => {
    const params = new URLSearchParams()
    params.append('session_id', sessionId.toString())
    params.append('format', format)

    const url = `${API_BASE_URL}/api/export/summary?${params.toString()}`
    return { downloadUrl: url }
  }
}

export const statsApi = {
  getSpeciesDistribution: async (year?: number, sessionId?: number) => {
    const params = new URLSearchParams()
    if (year) params.append('year', year.toString())
    if (sessionId) params.append('session_id', sessionId.toString())

    const response = await fetch(`${API_BASE_URL}/api/stats/species-distribution?${params.toString()}`)
    if (!response.ok) {
      throw new Error(`获取物种分布失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getMonthlyTrend: async (year: number) => {
    const response = await fetch(`${API_BASE_URL}/api/stats/monthly-trend?year=${year}`)
    if (!response.ok) {
      throw new Error(`获取月度趋势失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getDailyActivity: async (year?: number, month?: number) => {
    const params = new URLSearchParams()
    if (year) params.append('year', year.toString())
    if (month) params.append('month', month.toString())

    const response = await fetch(`${API_BASE_URL}/api/stats/daily-activity?${params.toString()}`)
    if (!response.ok) {
      throw new Error(`获取每日活动失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getLocationFrequency: async () => {
    const response = await fetch(`${API_BASE_URL}/api/stats/location-frequency`)
    if (!response.ok) {
      throw new Error(`获取地点频率失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getTopSpecies: async (limit: number = 10) => {
    const response = await fetch(`${API_BASE_URL}/api/stats/top-species?limit=${limit}`)
    if (!response.ok) {
      throw new Error(`获取热门物种失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getCameraStats: async (year?: number) => {
    const params = new URLSearchParams()
    if (year) params.append('year', year.toString())

    const response = await fetch(`${API_BASE_URL}/api/stats/camera-stats?${params.toString()}`)
    if (!response.ok) {
      throw new Error(`获取相机统计失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getOverview: async () => {
    const response = await fetch(`${API_BASE_URL}/api/stats/overview`)
    if (!response.ok) {
      throw new Error(`获取总览统计失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getAnnualReport: async (year: number) => {
    const response = await fetch(`${API_BASE_URL}/api/stats/annual-report?year=${year}`)
    if (!response.ok) {
      throw new Error(`获取年度报告失败：${response.statusText}`)
    }
    return { data: await response.json() }
  }
}

export const achievementsApi = {
  getAchievements: async () => {
    const response = await fetch(`${API_BASE_URL}/api/leaderboard/achievements/check`)
    if (!response.ok) {
      throw new Error(`获取成就失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getStats: async () => {
    const response = await fetch(`${API_BASE_URL}/api/leaderboard/achievements/stats`)
    if (!response.ok) {
      throw new Error(`获取统计失败：${response.statusText}`)
    }
    return { data: await response.json() }
  }
}

export const hotspotsApi = {
  getHotspots: async (limit: number = 100) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/hotspots?limit=${limit}`)
    if (!response.ok) {
      throw new Error(`获取热点失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getRecommended: async (lat: number, lng: number, limit: number = 20) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/hotspots/recommended?lat=${lat}&lng=${lng}&limit=${limit}`)
    if (!response.ok) {
      throw new Error(`获取推荐热点失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  createHotspot: async (hotspot: { name: string; description: string; gps_lat: number; gps_lng: number; city?: string; province?: string; habitat_type?: string }) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/hotspot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(hotspot)
    })
    if (!response.ok) {
      throw new Error(`创建热点失败：${response.statusText}`)
    }
    return { data: await response.json() }
  }
}

export const subscriptionsApi = {
  getSubscriptions: async (userName: string) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/subscriptions?user_name=${encodeURIComponent(userName)}`)
    if (!response.ok) {
      throw new Error(`获取订阅失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  createSubscription: async (subscription: { user_name: string; location_name: string; radius_km: number; min_species_count: number; gps_lat?: number; gps_lng?: number; notification_enabled?: boolean; email_enabled?: boolean; wechat_enabled?: boolean }) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/subscription`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription)
    })
    if (!response.ok) {
      throw new Error(`创建订阅失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  toggleSubscription: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/subscription/${id}/toggle`, {
      method: 'PUT'
    })
    if (!response.ok) {
      throw new Error(`切换订阅状态失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  deleteSubscription: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/hotspots/subscription/${id}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      throw new Error(`删除订阅失败：${response.statusText}`)
    }
    return { data: await response.json() }
  }
}

export const mapApi = {
  getDailyMap: async (mapDate?: string, photoLocations?: any[]) => {
    const result = await window.electronAPI.getDailyMap(mapDate || new Date().toISOString().split('T')[0], photoLocations)
    if (!result.success) {
      throw new Error(result.error)
    }
    return { data: result.data }
  },

  generateMap: async (_photoData: any) => {
    // Electron 环境下使用简化实现
    return { data: { map_html: null } }
  },

  getHeatmap: async (sessionId?: number) => {
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId.toString())

    const response = await fetch(`${API_BASE_URL}/api/map/heatmap?${params.toString()}`)
    if (!response.ok) {
      throw new Error(`获取热力图失败：${response.statusText}`)
    }
    return { data: await response.json() }
  },

  getHeatmapData: async (year?: number, month?: number) => {
    const params = new URLSearchParams()
    if (year) params.append('year', year.toString())
    if (month) params.append('month', month.toString())

    const response = await fetch(`${API_BASE_URL}/api/stats/daily-activity?${params.toString()}`)
    if (!response.ok) {
      throw new Error(`获取热力数据失败：${response.statusText}`)
    }
    return { data: await response.json() }
  }
}

// 检查后端连接状态
export const checkBackend = async () => {
  return await window.electronAPI.checkBackend()
}

export default {
  scanApi,
  birdsApi,
  mapApi,
  scoringApi,
  summaryApi,
  exportApi,
  statsApi,
  achievementsApi,
  hotspotsApi,
  subscriptionsApi,
  checkBackend
}
