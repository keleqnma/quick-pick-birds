import { useState, useEffect } from 'react'

interface Species {
  id: number
  species_cn: string
  species_en?: string
  scientific_name: string
  family_cn?: string
  family_en?: string
  order_cn?: string
  order_en?: string
  conservation_level?: string
  china_endemic: boolean
  common: boolean
  description?: string
  distribution?: string
  habitat?: string
  voice?: string
  similar_species?: string
}

export default function SpeciesExplorer() {
  const [species, setSpecies] = useState<Species[]>([])
  const [selectedSpecies, setSelectedSpecies] = useState<Species | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFamily, setSelectedFamily] = useState<string>('')
  const [families, setFamilies] = useState<any[]>([])
  const [orders, setOrders] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState<'list' | 'detail'>('list')

  // 获取物种列表
  const fetchSpecies = async (family?: string, search?: string) => {
    setLoading(true)
    try {
      let url = 'http://localhost:8000/api/species/species?limit=200'
      if (family) url += `&family=${family}`
      if (search) url = `http://localhost:8000/api/species/search?q=${search}&limit=200`

      const response = await fetch(url)
      const data = await response.json()
      setSpecies(data.results || [])
    } catch (error) {
      console.error('获取物种列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 获取科列表
  const fetchFamilies = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/species/families')
      const data = await response.json()
      setFamilies(data.families || [])
    } catch (error) {
      console.error('获取科列表失败:', error)
    }
  }

  // 获取目列表
  const fetchOrders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/species/orders')
      const data = await response.json()
      setOrders(data.orders || [])
    } catch (error) {
      console.error('获取目列表失败:', error)
    }
  }

  // 获取统计
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/species/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('获取统计失败:', error)
    }
  }

  useEffect(() => {
    fetchSpecies()
    fetchFamilies()
    fetchOrders()
    fetchStats()
  }, [])

  // 搜索
  const handleSearch = () => {
    if (searchQuery.trim()) {
      fetchSpecies(undefined, searchQuery.trim())
    } else {
      fetchSpecies(selectedFamily || undefined)
    }
  }

  // 查看物种详情
  const viewSpecies = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/species/species/${id}`)
      const data = await response.json()
      setSelectedSpecies(data)
      setView('detail')
    } catch (error) {
      console.error('获取物种详情失败:', error)
    }
  }

  // 保护级别标签颜色
  const getConservationColor = (level?: string) => {
    if (!level) return 'var(--text-muted)'
    if (level.includes('一级') || level.includes('CR')) return '#c0392b'
    if (level.includes('二级') || level.includes('EN')) return '#e67e22'
    if (level.includes('三有') || level.includes('VU')) return '#f39c12'
    if (level.includes('NT')) return '#27ae60'
    return 'var(--text-muted)'
  }

  return (
    <div className="container">
      <div className="page-header">
        <h2>鸟类物种百科</h2>
        {view === 'detail' && (
          <button className="btn btn-secondary" onClick={() => setView('list')}>
            ← 返回列表
          </button>
        )}
      </div>

      {/* 统计卡片 */}
      {stats && view === 'list' && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total || 0}</div>
            <div className="stat-label">物种总数</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.common || 0}</div>
            <div className="stat-label">常见种</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.endemic || 0}</div>
            <div className="stat-label">中国特有种</div>
          </div>
        </div>
      )}

      {view === 'list' && (
        <>
          {/* 搜索和筛选 */}
          <div className="card" style={{ marginTop: '20px' }}>
            <div className="input-group">
              <input
                type="text"
                className="input"
                placeholder="搜索鸟种（中文名/学名/英文名）..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && handleSearch()}
              />
              <button className="btn btn-primary" onClick={handleSearch}>
                搜索
              </button>
            </div>

            <div style={{ marginTop: '15px' }}>
              <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginRight: '10px' }}>
                按科筛选：
              </label>
              <select
                value={selectedFamily}
                onChange={e => {
                  setSelectedFamily(e.target.value)
                  fetchSpecies(e.target.value || undefined)
                  setSearchQuery('')
                }}
                style={{ padding: '8px 12px', borderRadius: 'var(--radius)', border: '1px solid var(--border-color)' }}
              >
                <option value="">全部</option>
                {Array.from(new Set(families.map(f => f.family_cn)))
                  .filter(Boolean)
                  .map((family, idx) => (
                    <option key={idx} value={family}>{family}</option>
                  ))}
              </select>
            </div>

            <div style={{ marginTop: '15px' }}>
              <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginRight: '10px' }}>
                按目浏览：
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                {orders.map((order: any, idx: number) => (
                  <button
                    key={idx}
                    className="btn btn-outline"
                    style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                    onClick={() => {
                      setSelectedFamily('')
                      fetchSpecies(undefined, order.order_cn)
                      setSearchQuery(order.order_cn)
                    }}
                  >
                    {order.order_cn} {order.order_en && `(${order.order_en})`}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 物种列表 */}
          <div className="card" style={{ marginTop: '20px' }}>
            <h3>
              {searchQuery ? `搜索结果：${species.length}` : selectedFamily ? `${selectedFamily} (${species.length})` : `全部物种 (${species.length})`}
            </h3>

            {loading ? (
              <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                加载中...
              </p>
            ) : species.length === 0 ? (
              <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                暂无数据，请输入搜索条件
              </p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>中文名</th>
                    <th>学名</th>
                    <th>英文名</th>
                    <th>科</th>
                    <th>保护级别</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {species.map(s => (
                    <tr key={s.id}>
                      <td>
                        <strong>{s.species_cn}</strong>
                        {s.china_endemic && (
                          <span style={{ marginLeft: '6px', fontSize: '0.75rem', color: '#c0392b', background: 'rgba(192, 57, 43, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                            中国特有
                          </span>
                        )}
                      </td>
                      <td style={{ fontStyle: 'italic' }}>{s.scientific_name}</td>
                      <td>{s.species_en || '-'}</td>
                      <td>{s.family_cn || '-'}</td>
                      <td>
                        {s.conservation_level && (
                          <span style={{
                            color: getConservationColor(s.conservation_level),
                            fontWeight: 600,
                            fontSize: '0.85rem'
                          }}>
                            {s.conservation_level}
                          </span>
                        )}
                        {!s.conservation_level && '-'}
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => viewSpecies(s.id)}
                        >
                          详情
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {/* 物种详情 */}
      {view === 'detail' && selectedSpecies && (
        <div className="card">
          <div className="mb-2">
            <h2 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>
              {selectedSpecies.species_cn}
              {selectedSpecies.china_endemic && (
                <span style={{ marginLeft: '10px', fontSize: '0.85rem', background: '#c0392b', color: 'white', padding: '3px 8px', borderRadius: '4px' }}>
                  中国特有
                </span>
              )}
            </h2>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
              {selectedSpecies.scientific_name}
            </p>
            {selectedSpecies.species_en && (
              <p style={{ color: 'var(--text-muted)' }}>{selectedSpecies.species_en}</p>
            )}
          </div>

          {/* 分类信息 */}
          <div className="card" style={{ background: 'var(--background-color)' }}>
            <h4>分类信息</h4>
            <div className="form-grid">
              {selectedSpecies.order_cn && (
                <div><strong>目:</strong> {selectedSpecies.order_cn} {selectedSpecies.order_en && `(${selectedSpecies.order_en})`}</div>
              )}
              {selectedSpecies.family_cn && (
                <div><strong>科:</strong> {selectedSpecies.family_cn} {selectedSpecies.family_en && `(${selectedSpecies.family_en})`}</div>
              )}
              {selectedSpecies.genus_cn && (
                <div><strong>属:</strong> {selectedSpecies.genus_cn} {selectedSpecies.genus_en && `(${selectedSpecies.genus_en})`}</div>
              )}
              {selectedSpecies.conservation_level && (
                <div>
                  <strong>保护级别:</strong>{' '}
                  <span style={{ color: getConservationColor(selectedSpecies.conservation_level), fontWeight: 600 }}>
                    {selectedSpecies.conservation_level}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* 生态信息 */}
          {(selectedSpecies.distribution || selectedSpecies.habitat || selectedSpecies.voice) && (
            <div className="card">
              <h4>生态信息</h4>
              {selectedSpecies.distribution && (
                <div style={{ marginBottom: '15px' }}>
                  <strong>分布:</strong>
                  <p style={{ marginTop: '5px', lineHeight: 1.8 }}>{selectedSpecies.distribution}</p>
                </div>
              )}
              {selectedSpecies.habitat && (
                <div style={{ marginBottom: '15px' }}>
                  <strong>生境:</strong>
                  <p style={{ marginTop: '5px', lineHeight: 1.8 }}>{selectedSpecies.habitat}</p>
                </div>
              )}
              {selectedSpecies.voice && (
                <div>
                  <strong>叫声:</strong>
                  <p style={{ marginTop: '5px', lineHeight: 1.8 }}>{selectedSpecies.voice}</p>
                </div>
              )}
            </div>
          )}

          {/* 形态描述 */}
          {selectedSpecies.description && (
            <div className="card">
              <h4>形态描述</h4>
              <p style={{ lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>{selectedSpecies.description}</p>
            </div>
          )}

          {/* 相似物种 */}
          {selectedSpecies.similar_species && (
            <div className="card">
              <h4>相似物种</h4>
              <p>{selectedSpecies.similar_species}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
