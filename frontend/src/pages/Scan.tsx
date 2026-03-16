import { useState, useRef, useEffect } from 'react'
import { scanApi, birdsApi, checkLLMConfigured } from '../api/api'
import { useNavigate } from 'react-router-dom'

interface Photo {
  file_path: string
  file_name: string
  file_size: number
  capture_time: string | null
  gps_lat: number | null
  gps_lon: number | null
  is_raw: boolean
}

interface ScanResult {
  total_photos: number
  raw_photos: number
  jpeg_photos: number
  photos_with_gps: number
  photos: Photo[]
}

export default function Scan() {
  const navigate = useNavigate()
  const [folderPath, setFolderPath] = useState('')
  const [includeSubfolders, setIncludeSubfolders] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [identifying, setIdentifying] = useState(false)
  const [birdResults, setBirdResults] = useState<any>(null)
  const [llmNotConfigured, setLlmNotConfigured] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 检查 LLM 配置
  useEffect(() => {
    const { configured } = checkLLMConfigured()
    setLlmNotConfigured(!configured)
  }, [])

  const handleSelectFolder = async () => {
    // 尝试使用 Electron API
    if (window.electronAPI) {
      const selectedPath = await window.electronAPI.selectFolder()
      if (selectedPath) {
        setFolderPath(selectedPath)
      }
    } else {
      // Web 模式：触发隐藏的 input
      fileInputRef.current?.click()
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      // 获取文件夹路径（webkitRelativePath 的第一级目录）
      const firstFile = files[0]
      const pathParts = (firstFile as any).webkitRelativePath?.split('/')
      if (pathParts && pathParts.length > 1) {
        setFolderPath(pathParts[0])
      } else {
        setFolderPath('已选择文件夹')
      }
    }
  }

  const handleScan = async () => {
    if (!folderPath.trim()) {
      setError('请输入文件夹路径')
      return
    }

    setScanning(true)
    setError(null)
    setResult(null)

    try {
      const response = await scanApi.scan(folderPath, includeSubfolders)
      setResult(response.data)
    } catch (err: any) {
      setError(err.message || '扫描失败，请检查路径是否正确')
    } finally {
      setScanning(false)
    }
  }

  const handleIdentify = async () => {
    if (!result?.photos.length) return

    // 检查 LLM 配置
    const { configured } = checkLLMConfigured()
    if (!configured) {
      setError('未配置大模型 API，无法进行鸟类识别')
      setLlmNotConfigured(true)
      return
    }

    setIdentifying(true)
    try {
      const photoPaths = result.photos.map(p => p.file_path)
      const response = await birdsApi.identify(photoPaths)
      setBirdResults(response.data)
    } catch (err: any) {
      if (err.name === 'LLM_CONFIG_REQUIRED') {
        setError('请先配置大模型 API')
        setLlmNotConfigured(true)
      } else {
        setError(err.message || '识别失败')
      }
    } finally {
      setIdentifying(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h2 className="card-title">扫描照片文件夹</h2>

        {/* 隐藏的 input 用于 Web 模式文件夹选择 */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          // @ts-ignore - webkitdirectory is not in React types
          webkitdirectory=""
          // @ts-ignore
          mozdirectory=""
          // @ts-ignore
          msdirectory=""
          // @ts-ignore
          odirectory=""
          directory=""
          multiple
          onChange={handleFileInputChange}
        />

        <div className="input-group">
          <input
            type="text"
            className="input"
            placeholder="点击「选择文件夹」或输入路径"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleScan()}
            readOnly
          />
          <button className="btn btn-outline" onClick={handleSelectFolder}>
            选择文件夹
          </button>
          <button className="btn btn-primary" onClick={handleScan} disabled={scanning}>
            {scanning ? '扫描中...' : '开始扫描'}
          </button>
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px', color: 'var(--text-secondary)' }}>
          <input
            type="checkbox"
            checked={includeSubfolders}
            onChange={(e) => setIncludeSubfolders(e.target.checked)}
          />
          包含子文件夹
        </label>

        {llmNotConfigured && (
          <div style={{
            marginTop: '15px',
            padding: '15px',
            background: '#fff7ed',
            borderRadius: '8px',
            border: '1px solid #ffedd5',
            color: '#9a3412'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div>
                <strong>⚠️ 未配置大模型 API</strong>
                <p style={{ margin: '8px 0 0 0', fontSize: '0.9rem' }}>
                  鸟类识别功能需要配置大模型 API（支持 OpenAI GPT-4o、Anthropic Claude 等）
                </p>
              </div>
              <button
                className="btn btn-primary"
                onClick={() => navigate('/settings')}
                style={{ marginLeft: '15px', whiteSpace: 'nowrap' }}
              >
                去配置
              </button>
            </div>
          </div>
        )}

        {error && (
          <div style={{ padding: '15px', background: '#fef2f2', borderRadius: '8px', border: '1px solid #fee2e2', color: '#991b1b' }}>
            {error}
          </div>
        )}
      </div>

      {result && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{result.total_photos}</div>
              <div className="stat-label">总照片数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{result.raw_photos}</div>
              <div className="stat-label">RAW 照片</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{result.jpeg_photos}</div>
              <div className="stat-label">JPEG 照片</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{result.photos_with_gps}</div>
              <div className="stat-label">带 GPS 信息</div>
            </div>
          </div>

          <div className="card">
            <div className="flex-between mb-1">
              <h3 className="card-title" style={{ marginBottom: 0 }}>照片列表</h3>
              <button
                className="btn btn-secondary"
                onClick={handleIdentify}
                disabled={identifying || !result.photos.length}
              >
                {identifying ? '识别中...' : '识别鸟类'}
              </button>
            </div>

            <div className="photo-grid">
              {result.photos.slice(0, 50).map((photo, index) => (
                <div key={index} className="photo-card">
                  <div className="photo-overlay">
                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>{photo.file_name}</div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>
                      {photo.is_raw ? 'RAW' : 'JPEG'}
                      {photo.capture_time && ` • ${photo.capture_time.slice(0, 16).replace('T', ' ')}`}
                    </div>
                  </div>
                  {photo.is_raw && <span className="photo-badge">RAW</span>}
                </div>
              ))}
            </div>

            {result.photos.length > 50 && (
              <p className="text-muted mt-2">
                显示前 50 张，共 {result.photos.length} 张照片
              </p>
            )}
          </div>

          {birdResults && (
            <div className="card">
              <h3 className="card-title">识别结果</h3>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value">{birdResults.total_photos}</div>
                  <div className="stat-label">已分析照片</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{birdResults.photos_with_birds}</div>
                  <div className="stat-label">检测到鸟类</div>
                </div>
              </div>

              {birdResults.detections?.length > 0 && (
                <div className="mt-2">
                  <h4 style={{ marginBottom: '10px', fontSize: '1rem' }}>检测到的鸟类</h4>
                  <div>
                    {birdResults.detections.map((d: any, i: number) => (
                      <span key={i} className="bird-tag">
                        {d.species_cn}
                        <span className="count">{Math.round(d.confidence * 100)}%</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {birdResults.burst_groups?.length > 0 && (
                <div className="mt-2">
                  <h4 style={{ marginBottom: '10px', fontSize: '1rem' }}>连拍分组 ({birdResults.burst_groups.length}组)</h4>
                  {birdResults.burst_groups.map((group: any) => (
                    <div key={group.group_id} className="burst-group">
                      <div className="burst-header">
                        <span>连拍 {group.photo_count} 张 (耗时 {group.time_span_seconds?.toFixed(1)}秒)</span>
                        <span className="bird-tag">{group.detections[0]?.species_cn || '未知'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
