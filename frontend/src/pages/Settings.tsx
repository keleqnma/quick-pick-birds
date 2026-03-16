import { useState, useEffect } from 'react'

interface ApiConfig {
  provider: string
  baseUrl: string
  apiKey: string
  model: string
  timeout: number
  systemPrompt: string
}

const DEFAULT_BIRD_PROMPT = `你是一位专业的鸟类学家和观鸟专家。请仔细分析这张照片，识别其中的鸟类。

请按照以下格式返回 JSON：
{
  "has_bird": true/false,
  "detections": [
    {
      "species_cn": "中文名称",
      "species_en": "English Name",
      "scientific_name": "学名 (如有把握)",
      "confidence": 0.0-1.0,
      "description": "外观特征描述",
      "behavior": "行为观察 (如有)",
      "similar_species": ["易混淆物种 1", "易混淆物种 2"]
    }
  ],
  "notes": "其他观察说明"
}

识别要点：
1. 观察体型大小、整体轮廓
2. 注意喙的形状和颜色
3. 观察羽毛颜色、斑纹 pattern
4. 注意腿脚颜色
5. 考虑栖息地和季节
6. 如无法确定到种，请识别到属或科

如果照片中没有鸟或无法识别，返回 {"has_bird": false, "detections": []}
置信度说明：
- 0.9-1.0: 特征清晰，确定无疑
- 0.7-0.9: 主要特征可见，较有把握
- 0.5-0.7: 部分特征可见， tentative identification
- <0.5: 图像质量差或特征不足，仅作猜测`

const PRESET_PROVIDERS = [
  { name: 'OpenAI', baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o-2024-08-06' },
  { name: 'Anthropic', baseUrl: 'https://api.anthropic.com/v1', model: 'claude-sonnet-4-20250514' },
  { name: 'DeepSeek', baseUrl: 'https://api.deepseek.com', model: 'deepseek-chat' },
  { name: 'Moonshot', baseUrl: 'https://api.moonshot.cn/v1', model: 'moonshot-v1-32k' },
  { name: 'SiliconFlow', baseUrl: 'https://api.siliconflow.cn/v1', model: 'Qwen/Qwen2.5-VL-72B-Instruct' },
  { name: '智谱 AI', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4v-plus' },
  { name: '自定义', baseUrl: '', model: '' },
]

export default function Settings() {
  const [config, setConfig] = useState<ApiConfig>({
    provider: 'OpenAI',
    baseUrl: 'https://api.openai.com/v1',
    apiKey: '',
    model: 'gpt-4o-2024-08-06',
    timeout: 60,
    systemPrompt: DEFAULT_BIRD_PROMPT,
  })
  const [saved, setSaved] = useState(false)
  const [showKey, setShowKey] = useState(false)

  useEffect(() => {
    const savedConfig = localStorage.getItem('llm_api_config')
    if (savedConfig) {
      try {
        setConfig(JSON.parse(savedConfig))
      } catch (e) {
        console.error('Failed to load config:', e)
      }
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('llm_api_config', JSON.stringify(config))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handlePresetChange = (presetName: string) => {
    const preset = PRESET_PROVIDERS.find(p => p.name === presetName)
    if (preset) {
      setConfig(prev => ({
        ...prev,
        provider: presetName,
        baseUrl: preset.baseUrl,
        model: preset.model,
      }))
    }
  }

  const handleResetPrompt = () => {
    setConfig(prev => ({ ...prev, systemPrompt: DEFAULT_BIRD_PROMPT }))
  }

  const handleTestConnection = async () => {
    // 优先使用 Electron IPC（避免 CORS 问题）
    if (window.electronAPI) {
      const result = await window.electronAPI.testLLMConnection({
        baseUrl: config.baseUrl,
        apiKey: config.apiKey,
        model: config.model,
        timeout: Math.min(config.timeout, 30),
      })

      if (result.success) {
        alert('连接成功！')
      } else {
        alert(`连接失败：${result.message}`)
      }
      return
    }

    // Web 模式：调用后端 HTTP API
    try {
      const response = await fetch('http://localhost:8000/api/llm/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base_url: config.baseUrl,
          api_key: config.apiKey,
          model: config.model,
          timeout: Math.min(config.timeout, 30),
        }),
      })

      const result = await response.json()

      if (result.status === 'success') {
        alert('连接成功！')
      } else {
        alert(`连接失败：${result.message}`)
      }
    } catch (error: any) {
      alert(`连接失败：${error.message}`)
    }
  }

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h2 className="card-title">大模型 API 配置</h2>

        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
          配置用于鸟类识别的大模型 API。支持 OpenAI 兼容格式的主流服务商。
        </p>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>预设服务商</label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {PRESET_PROVIDERS.map(preset => (
              <button
                key={preset.name}
                className={`btn ${config.provider === preset.name ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => handlePresetChange(preset.name)}
                style={{ fontSize: '0.85rem', padding: '8px 14px' }}
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>API Base URL</label>
          <input
            type="text"
            className="input"
            value={config.baseUrl}
            onChange={(e) => setConfig(prev => ({ ...prev, baseUrl: e.target.value }))}
            placeholder="https://api.example.com/v1"
          />
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            基础 API 地址，通常由服务商提供
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>API Key</label>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type={showKey ? 'text' : 'password'}
              className="input"
              value={config.apiKey}
              onChange={(e) => setConfig(prev => ({ ...prev, apiKey: e.target.value }))}
              placeholder="输入 API Key"
            />
            <button
              className="btn btn-outline"
              onClick={() => setShowKey(!showKey)}
              style={{ minWidth: '80px' }}
            >
              {showKey ? '隐藏' : '显示'}
            </button>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            您的 API Key 仅存储在本地浏览器，不会上传到服务器
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>模型名称</label>
          <input
            type="text"
            className="input"
            value={config.model}
            onChange={(e) => setConfig(prev => ({ ...prev, model: e.target.value }))}
            placeholder="gpt-4o, claude-sonnet-4-6, etc."
          />
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            用于图像识别的模型，需要支持视觉理解
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>超时时间（秒）</label>
          <input
            type="number"
            className="input"
            value={config.timeout}
            onChange={(e) => setConfig(prev => ({ ...prev, timeout: parseInt(e.target.value) || 60 }))}
            min="10"
            max="300"
          />
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            图像识别可能需要较长时间，建议设置为 60 秒以上
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <label style={{ fontWeight: 600 }}>识别 Prompt</label>
            <button className="btn btn-outline" onClick={handleResetPrompt} style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
              重置为默认
            </button>
          </div>
          <textarea
            className="input"
            rows={10}
            value={config.systemPrompt}
            onChange={(e) => setConfig(prev => ({ ...prev, systemPrompt: e.target.value }))}
            style={{ fontFamily: 'monospace', fontSize: '0.85rem', resize: 'vertical' }}
          />
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            发送给大模型的系统提示，指导 AI 如何识别和描述鸟类
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button className="btn btn-primary" onClick={handleSave}>
            {saved ? '已保存' : '保存配置'}
          </button>
          <button className="btn btn-outline" onClick={handleTestConnection}>
            测试连接
          </button>
          <button
            className="btn btn-outline"
            onClick={() => {
              setConfig({
                provider: 'OpenAI',
                baseUrl: 'https://api.openai.com/v1',
                apiKey: '',
                model: 'gpt-4o-2024-08-06',
                timeout: 60,
                systemPrompt: DEFAULT_BIRD_PROMPT,
              })
              localStorage.removeItem('llm_api_config')
            }}
          >
            重置全部
          </button>
        </div>
      </div>

      <div className="card" style={{ maxWidth: '800px', margin: '24px auto' }}>
        <h3 className="card-title">支持的服务商</h3>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.9 }}>
          <p><strong>OpenAI</strong> - GPT-4o、GPT-4 Turbo 等，支持图像识别</p>
          <p><strong>Anthropic</strong> - Claude 系列，强大的视觉理解能力</p>
          <p><strong>DeepSeek</strong> - 深度求索，高性价比</p>
          <p><strong>Moonshot</strong> - 月之暗面 Kimi，国产大模型</p>
          <p><strong>SiliconFlow</strong> - 硅基流动，提供多种开源模型</p>
          <p><strong>智谱 AI</strong> - GLM 系列，支持多模态</p>
          <p><strong>自定义</strong> - 任何兼容 OpenAI 格式的 API</p>
        </div>
      </div>
    </div>
  )
}
