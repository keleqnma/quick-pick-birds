import { useState, useEffect } from 'react'
import { summaryApi, exportApi } from '../api/api'

interface Session {
  id: number
  folder_path: string
  scan_date: string
  total_photos: number
  location_name: string | null
  notes: string | null
}

interface SessionSummary {
  session: Session
  stats: {
    total_photos: number
    recommended_count: number
    photos_with_gps: number
    species_count: number
    species_list: string
  }
  gps_points: Array<{ gps_lat: number; gps_lng: number; cnt: number }>
  detections: Array<{
    species_cn: string
    species_en: string
    description: string
    behavior: string
    file_path: string
    capture_time: string
  }>
}

export default function Summary() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [htmlPath, setHtmlPath] = useState<string | null>(null)

  // 加载会话列表
  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const response = await summaryApi.get_sessions(50, 0)
      setSessions(response.data.sessions || [])
    } catch (err: any) {
      console.error('加载会话列表失败:', err)
    }
  }

  const handleSelectSession = async (session: Session) => {
    setSelectedSession(session)
    setLoading(true)
    setError(null)
    setSummary(null)
    setHtmlPath(null)

    try {
      const response = await summaryApi.get_session(session.id)
      setSummary(response.data)
    } catch (err: any) {
      setError(err.message || '加载会话详情失败')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateHtml = async () => {
    if (!selectedSession) return

    setGenerating(true)
    setError(null)

    try {
      const response = await summaryApi.generate_summary(selectedSession.id)
      setHtmlPath(response.data.html_path)
    } catch (err: any) {
      setError(err.message || '生成小结失败')
    } finally {
      setGenerating(false)
    }
  }

  const handleOpenHtml = () => {
    if (htmlPath) {
      window.open(`file://${htmlPath}`, '_blank')
    }
  }

  const handleExport = (type: 'photos' | 'detections' | 'summary') => {
    if (!selectedSession) return

    let downloadUrl = ''
    if (type === 'photos') {
      downloadUrl = exportApi.exportPhotos(selectedSession.id).downloadUrl
    } else if (type === 'detections') {
      downloadUrl = exportApi.exportDetections(selectedSession.id).downloadUrl
    } else if (type === 'summary') {
      downloadUrl = exportApi.exportSummary(selectedSession.id).downloadUrl
    }

    // 触发下载
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const formatDate = (dateStr: string) => {
    try {
      const dt = new Date(dateStr)
      return dt.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateStr
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h2 className="card-title">观鸟小结</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
          查看历史观测记录，生成精美的 HTML 小结
        </p>

        {/* 会话列表 */}
        <div className="mb-3">
          <h3 style={{ fontSize: '1rem', marginBottom: '12px' }}>观测会话</h3>
          {sessions.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>
              暂无观测记录，请先扫描照片
            </p>
          ) : (
            <div style={{ display: 'grid', gap: '10px' }}>
              {sessions.map(session => (
                <div
                  key={session.id}
                  className={`clickable-card ${selectedSession?.id === session.id ? 'active' : ''}`}
                  onClick={() => handleSelectSession(session)}
                  style={{
                    padding: '15px',
                    borderRadius: '8px',
                    border: selectedSession?.id === session.id
                      ? '2px solid var(--primary)'
                      : '1px solid var(--border)',
                    background: selectedSession?.id === session.id
                      ? 'var(--bg-secondary)'
                      : 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                        {session.location_name || '未命名地点'}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {formatDate(session.scan_date)} · {session.total_photos} 张照片
                      </div>
                    </div>
                    <span className="bird-tag">
                      #{session.id}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && (
          <div style={{
            padding: '15px',
            background: '#fef2f2',
            borderRadius: '8px',
            border: '1px solid #fee2e2',
            color: '#991b1b',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}
      </div>

      {/* 会话详情 */}
      {loading && (
        <div className="card">
          <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            加载中...
          </p>
        </div>
      )}

      {summary && !loading && (
        <>
          {/* 统计卡片 */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{summary.stats.total_photos}</div>
              <div className="stat-label">总照片数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{summary.stats.recommended_count}</div>
              <div className="stat-label">推荐照片</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{summary.stats.species_count}</div>
              <div className="stat-label">物种数量</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{summary.stats.photos_with_gps}</div>
              <div className="stat-label">带 GPS 照片</div>
            </div>
          </div>

          {/* 物种列表 */}
          {summary.stats.species_list && (
            <div className="card">
              <h3 className="card-title">观测物种</h3>
              <div className="species-list">
                {summary.stats.species_list.split(',').filter(s => s.trim()).map((species, i) => (
                  <span key={i} className="species-tag">{species.trim()}</span>
                ))}
              </div>
            </div>
          )}

          {/* 观测记录 */}
          {summary.detections.length > 0 && (
            <div className="card">
              <h3 className="card-title">观测记录</h3>
              <div style={{ display: 'grid', gap: '12px' }}>
                {summary.detections.map((det, i) => (
                  <div
                    key={i}
                    className="detection-card"
                    style={{
                      background: 'var(--bg-secondary)',
                      borderRadius: '8px',
                      padding: '15px',
                      borderLeft: '4px solid var(--accent)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
                      <h4 style={{ color: 'var(--primary)', margin: 0 }}>{det.species_cn}</h4>
                      <span style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                        {det.species_en}
                      </span>
                    </div>
                    {det.description && (
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                        {det.description}
                      </p>
                    )}
                    {det.behavior && (
                      <p style={{ fontSize: '0.85rem', color: 'var(--primary)', marginBottom: '8px' }}>
                        🔍 {det.behavior}
                      </p>
                    )}
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
                      📷 {det.file_path.split(/[\\/]/).pop()}
                      {det.capture_time && ` · ${det.capture_time.slice(0, 16).replace('T', ' ')}`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 生成 HTML 和导出按钮 */}
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                className="btn btn-primary"
                onClick={handleGenerateHtml}
                disabled={generating}
              >
                {generating ? '生成中...' : '生成 HTML 小结'}
              </button>
              <button
                className="btn btn-outline"
                onClick={() => handleExport('summary')}
              >
                导出摘要 Excel
              </button>
              <button
                className="btn btn-outline"
                onClick={() => handleExport('photos')}
              >
                导出照片数据
              </button>
              <button
                className="btn btn-outline"
                onClick={() => handleExport('detections')}
              >
                导出鸟类检测
              </button>
            </div>
            {htmlPath && (
              <p style={{ marginTop: '15px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                已生成：{htmlPath}
              </p>
            )}
          </div>
        </>
      )}
    </div>
  )
}
