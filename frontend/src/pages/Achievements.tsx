import { useState, useEffect } from 'react'
import { achievementsApi } from '../api/api'

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  category: string
  unlocked: boolean
}

interface AchievementStats {
  total_species: number
  total_photos: number
  total_observation_days: number
  total_checklists: number
  best_day_species_count: number
  next_milestones: Array<{
    name: string
    current: number
    next: number | null
  }>
}

export default function Achievements() {
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [stats, setStats] = useState<AchievementStats | null>(null)
  const [unlockedCount, setUnlockedCount] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [progress, setProgress] = useState(0)
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await achievementsApi.getAchievements()
      setAchievements(data.data.achievements || [])
      setUnlockedCount(data.data.unlocked_count || 0)
      setTotalCount(data.data.total_count || 0)
      setProgress(data.data.progress || 0)

      const statsData = await achievementsApi.getStats()
      setStats(statsData.data)
    } catch (error) {
      console.error('加载成就失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>加载成就数据中...</p>
        </div>
      </div>
    )
  }

  // 分类过滤
  const categories = ['all', ...Array.from(new Set(achievements.map(a => a.category)))]
  const filteredAchievements = selectedCategory === 'all'
    ? achievements
    : achievements.filter(a => a.category === selectedCategory)

  // 按完成状态排序
  const sortedAchievements = [...filteredAchievements].sort((a, b) => {
    if (a.unlocked !== b.unlocked) return a.unlocked ? 1 : -1
    return a.name.localeCompare(b.name)
  })

  return (
    <div className="container">
      <div className="page-header">
        <h2>成就系统</h2>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {unlockedCount} / {totalCount}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>已完成成就</div>
        </div>
      </div>

      {/* 进度条 */}
      <div className="card mb-2">
        <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>成就进度</strong>
          <span style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>{progress}%</span>
        </div>
        <div style={{
          height: '12px',
          background: 'var(--border-light)',
          borderRadius: '6px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            background: `linear-gradient(90deg, var(--primary-color), var(--primary-light))`,
            width: `${progress}%`,
            transition: 'width 0.5s ease'
          }} />
        </div>
      </div>

      {/* 统计概览 */}
      {stats && (
        <div className="card mb-2">
          <h3 className="card-title">我的统计</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total_species}</div>
              <div className="stat-label">累计物种</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_photos}</div>
              <div className="stat-label">累计照片</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_observation_days}</div>
              <div className="stat-label">观测天数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_checklists}</div>
              <div className="stat-label">观测清单</div>
            </div>
          </div>

          {/* 下一个里程碑 */}
          <div style={{ marginTop: '20px' }}>
            <h4 style={{ marginBottom: '10px' }}>下一个里程碑</h4>
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
              {stats.next_milestones.map((milestone, idx) => {
                if (!milestone.next) return null
                const percent = Math.min(100, Math.round(milestone.current / milestone.next * 100))
                return (
                  <div key={idx} style={{ flex: '1', minWidth: '150px', background: 'var(--background-color)', padding: '15px', borderRadius: 'var(--radius-lg)' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '5px' }}>{milestone.name}</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '8px' }}>
                      {milestone.current} <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>/ {milestone.next}</span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--border-light)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', background: 'var(--primary-color)', width: `${percent}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* 分类筛选 */}
      <div className="card mb-2">
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {categories.map(cat => (
            <button
              key={cat}
              className={`btn ${selectedCategory === cat ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setSelectedCategory(cat)}
              style={{ fontSize: '0.875rem', padding: '8px 16px' }}
            >
              {cat === 'all' ? '全部' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* 成就列表 */}
      <div className="card">
        <h3 className="card-title">成就列表</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '15px'
        }}>
          {sortedAchievements.map(achievement => (
            <div
              key={achievement.id}
              style={{
                padding: '15px',
                border: `1px solid ${achievement.unlocked ? 'var(--primary-color)' : 'var(--border-color)'}`,
                borderRadius: 'var(--radius-lg)',
                background: achievement.unlocked
                  ? 'rgba(45, 106, 79, 0.05)'
                  : 'var(--card-background)',
                opacity: achievement.unlocked ? 1 : 0.7,
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
                <div style={{
                  fontSize: '2rem',
                  filter: achievement.unlocked ? 'none' : 'grayscale(100%)'
                }}>
                  {achievement.icon}
                </div>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>{achievement.name}</div>
                  <div style={{
                    fontSize: '0.75rem',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: achievement.unlocked ? 'var(--primary-color)' : 'var(--border-light)',
                    color: achievement.unlocked ? 'white' : 'var(--text-secondary)',
                    display: 'inline-block',
                    marginTop: '4px'
                  }}>
                    {achievement.category}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                {achievement.description}
              </div>
              {achievement.unlocked && (
                <div style={{
                  marginTop: '10px',
                  fontSize: '0.75rem',
                  color: 'var(--primary-color)',
                  fontWeight: '500'
                }}>
                  ✓ 已解锁
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
