import { useState, useEffect } from 'react'
import { scoringApi, scanApi, checkLLMConfigured } from '../api/api'
import { useNavigate } from 'react-router-dom'

interface PhotoScore {
  image_path: string
  overall_score: number
  focus_score: number
  clarity_score: number
  composition_score: number
  explanation: string
  is_recommended: boolean
}

interface ScoringCriteria {
  focus_weight: number
  clarity_weight: number
  composition_weight: number
}

export default function PhotoScoring() {
  const navigate = useNavigate()
  const [folderPath, setFolderPath] = useState('')
  const [photos, setPhotos] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [scoring, setScoring] = useState(false)
  const [scores, setScores] = useState<PhotoScore[]>([])
  const [error, setError] = useState<string | null>(null)
  const [criteria, setCriteria] = useState<ScoringCriteria>({
    focus_weight: 0.40,
    clarity_weight: 0.35,
    composition_weight: 0.25
  })
  const [showRecommendedOnly, setShowRecommendedOnly] = useState(false)
  const [totalScored, setTotalScored] = useState(0)
  const [recommendedCount, setRecommendedCount] = useState(0)
  const [llmNotConfigured, setLlmNotConfigured] = useState(false)

  // 检查 LLM 配置
  useEffect(() => {
    const { configured } = checkLLMConfigured()
    setLlmNotConfigured(!configured)
  }, [])

  // 获取默认权重
  useEffect(() => {
    scoringApi.get_default_criteria().then(res => {
      setCriteria(res.data)
    }).catch(console.error)
  }, [])

  const handleSelectFolder = async () => {
    if (window.electronAPI) {
      const selectedPath = await window.electronAPI.selectFolder()
      if (selectedPath) {
        setFolderPath(selectedPath)
      }
    }
  }

  const handleScanFolder = async () => {
    if (!folderPath.trim()) {
      setError('请输入文件夹路径')
      return
    }

    setLoading(true)
    setError(null)
    setPhotos([])
    setScores([])

    try {
      const response = await scanApi.scan(folderPath, true)
      const photoPaths = response.data.photos.map((p: any) => p.file_path)
      setPhotos(photoPaths)
      setTotalScored(0)
      setRecommendedCount(0)
    } catch (err: any) {
      setError(err.message || '扫描失败')
    } finally {
      setLoading(false)
    }
  }

  const handleScore = async () => {
    if (photos.length === 0) return

    // 检查 LLM 配置
    const { configured } = checkLLMConfigured()
    if (!configured) {
      setError('未配置大模型 API，请先配置后重试')
      setLlmNotConfigured(true)
      return
    }

    setScoring(true)
    setError(null)

    try {
      const response = await scoringApi.batch_score(photos, criteria)
      setScores(response.data.scores)
      setTotalScored(response.data.total)
      setRecommendedCount(response.data.recommended_count)
    } catch (err: any) {
      if (err.name === 'LLM_CONFIG_REQUIRED') {
        setError('请先配置大模型 API')
        setLlmNotConfigured(true)
      } else {
        setError(err.message || '评分失败')
      }
    } finally {
      setScoring(false)
    }
  }

  const handleWeightChange = (key: keyof ScoringCriteria, value: number) => {
    setCriteria(prev => ({
      ...prev,
      [key]: value / 100
    }))
  }

  // 归一化权重，确保总和为 1
  useEffect(() => {
    const total = criteria.focus_weight + criteria.clarity_weight + criteria.composition_weight
    if (Math.abs(total - 1) > 0.001 && total > 0) {
      const scale = 1 / total
      setCriteria(prev => ({
        focus_weight: prev.focus_weight * scale,
        clarity_weight: prev.clarity_weight * scale,
        composition_weight: prev.composition_weight * scale
      }))
    }
  }, [criteria.focus_weight, criteria.clarity_weight, criteria.composition_weight])

  const filteredScores = showRecommendedOnly
    ? scores.filter(s => s.is_recommended)
    : scores

  const getScoreColor = (score: number) => {
    if (score >= 85) return '#22c55e'
    if (score >= 70) return '#84cc16'
    if (score >= 55) return '#eab308'
    return '#ef4444'
  }

  return (
    <div className="container">
      <div className="card">
        <h2 className="card-title">智能筛图</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
          使用大模型评估照片质量，从对焦、清晰度、构图三个维度进行评分
        </p>

        {/* 文件夹选择 */}
        <div className="input-group mb-3">
          <input
            type="text"
            className="input"
            placeholder="照片文件夹路径"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            readOnly
          />
          <button className="btn btn-outline" onClick={handleSelectFolder}>
            选择文件夹
          </button>
          <button
            className="btn btn-outline"
            onClick={handleScanFolder}
            disabled={loading || !folderPath}
          >
            {loading ? '扫描中...' : '扫描照片'}
          </button>
        </div>

        {photos.length > 0 && (
          <div className="mb-3">
            <p style={{ color: 'var(--text-secondary)' }}>
              已扫描到 {photos.length} 张照片
            </p>
          </div>
        )}

        {/* 权重配置 */}
        <div className="card" style={{ background: 'var(--bg-secondary)', marginBottom: '20px' }}>
          <h3 style={{ marginBottom: '15px', fontSize: '1rem' }}>评分权重配置</h3>
          <div style={{ display: 'grid', gap: '15px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <label style={{ fontWeight: 500 }}>对焦准确性（鸟眼清晰）</label>
                <span style={{ fontWeight: 600, color: 'var(--primary)' }}>
                  {(criteria.focus_weight * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={criteria.focus_weight * 100}
                onChange={(e) => handleWeightChange('focus_weight', parseInt(e.target.value))}
                style={{ width: '100%', height: '8px' }}
              />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <label style={{ fontWeight: 500 }}>主体清晰度（羽毛锐度）</label>
                <span style={{ fontWeight: 600, color: 'var(--primary)' }}>
                  {(criteria.clarity_weight * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={criteria.clarity_weight * 100}
                onChange={(e) => handleWeightChange('clarity_weight', parseInt(e.target.value))}
                style={{ width: '100%', height: '8px' }}
              />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <label style={{ fontWeight: 500 }}>构图美学</label>
                <span style={{ fontWeight: 600, color: 'var(--primary)' }}>
                  {(criteria.composition_weight * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={criteria.composition_weight * 100}
                onChange={(e) => handleWeightChange('composition_weight', parseInt(e.target.value))}
                style={{ width: '100%', height: '8px' }}
              />
            </div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            className="btn btn-primary"
            onClick={handleScore}
            disabled={scoring || photos.length === 0}
          >
            {scoring ? '评分中...' : '开始评分'}
          </button>
          {scores.length > 0 && (
            <>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={showRecommendedOnly}
                  onChange={(e) => setShowRecommendedOnly(e.target.checked)}
                />
                仅看推荐（≥75 分）
              </label>
              <span style={{ color: 'var(--text-secondary)' }}>
                推荐 {recommendedCount} / {totalScored} 张
              </span>
            </>
          )}
        </div>

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
                  智能筛图功能需要配置大模型 API（支持 OpenAI GPT-4o、Anthropic Claude 等）
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
          <div style={{
            marginTop: '15px',
            padding: '15px',
            background: '#fef2f2',
            borderRadius: '8px',
            border: '1px solid #fee2e2',
            color: '#991b1b'
          }}>
            {error}
          </div>
        )}
      </div>

      {/* 评分结果 */}
      {filteredScores.length > 0 && (
        <div className="card">
          <h3 className="card-title">
            评分结果 {showRecommendedOnly && `(仅推荐 ${filteredScores.length} 张)`}
          </h3>
          <div className="photo-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
            {filteredScores.map((score, index) => (
              <div
                key={index}
                className="photo-card"
                style={{
                  border: score.is_recommended ? '2px solid var(--primary)' : '1px solid var(--border)',
                  position: 'relative'
                }}
              >
                {score.is_recommended && (
                  <span
                    className="photo-badge"
                    style={{
                      background: 'var(--primary)',
                      top: '8px',
                      right: '8px',
                      left: 'auto'
                    }}
                  >
                    推荐
                  </span>
                )}
                <div className="photo-overlay" style={{ padding: '12px' }}>
                  <div style={{ fontWeight: 600, marginBottom: '8px', fontSize: '0.9rem' }}>
                    {score.image_path.split(/[\\/]/).pop()}
                  </div>

                  {/* 总分 */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '10px'
                  }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>总分</span>
                    <span style={{
                      fontSize: '1.5rem',
                      fontWeight: 700,
                      color: getScoreColor(score.overall_score)
                    }}>
                      {score.overall_score}
                    </span>
                  </div>

                  {/* 详细分数 */}
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span>对焦</span>
                      <span style={{ color: getScoreColor(score.focus_score) }}>{score.focus_score}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span>清晰度</span>
                      <span style={{ color: getScoreColor(score.clarity_score) }}>{score.clarity_score}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>构图</span>
                      <span style={{ color: getScoreColor(score.composition_score) }}>{score.composition_score}</span>
                    </div>
                  </div>

                  {/* 评语 */}
                  {score.explanation && (
                    <div style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)',
                      background: 'rgba(0,0,0,0.3)',
                      padding: '8px',
                      borderRadius: '6px',
                      maxHeight: '60px',
                      overflow: 'auto'
                    }}>
                      {score.explanation}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
