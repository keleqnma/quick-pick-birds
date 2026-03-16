import { useState, useEffect } from 'react'

interface Checklist {
  id: number
  checklist_date: string
  location_name: string
  total_species: number
  total_individuals: number
  observer_name?: string
  created_at: string
}

interface ChecklistItem {
  id: number
  species_cn: string
  species_en?: string
  scientific_name?: string
  count: number
  sex?: string
  age?: string
  behavior?: string
  notes?: string
}

interface ChecklistDetail extends Checklist {
  items: ChecklistItem[]
  gps_lat?: number
  gps_lng?: number
  start_time?: string
  duration_minutes?: number
  protocol: string
  weather?: string
  temperature?: number
  wind?: string
  notes?: string
}

export default function Checklists() {
  const [checklists, setChecklists] = useState<Checklist[]>([])
  const [selectedChecklist, setSelectedChecklist] = useState<ChecklistDetail | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<any>(null)

  // 表单状态
  const [formData, setFormData] = useState({
    checklist_date: new Date().toISOString().split('T')[0],
    location_name: '',
    gps_lat: '',
    gps_lng: '',
    start_time: '',
    duration_minutes: '',
    protocol: 'incidental',
    observer_name: '',
    weather: '',
    temperature: '',
    wind: '',
    notes: '',
  })

  const [currentItem, setCurrentItem] = useState({
    species_cn: '',
    species_en: '',
    scientific_name: '',
    count: 1,
    sex: '',
    age: '',
    behavior: '',
    notes: '',
  })

  const [formItems, setFormItems] = useState<any[]>([])

  // 获取清单列表
  const fetchChecklists = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/checklist/checklists')
      const data = await response.json()
      setChecklists(data.checklists || [])
    } catch (error) {
      console.error('获取清单列表失败:', error)
    }
  }

  // 获取统计
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/checklist/checklist/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('获取统计失败:', error)
    }
  }

  useEffect(() => {
    fetchChecklists()
    fetchStats()
  }, [])

  // 获取清单详情
  const viewChecklist = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/checklist/checklist/${id}`)
      const data = await response.json()
      setSelectedChecklist(data)
    } catch (error) {
      console.error('获取清单详情失败:', error)
    }
  }

  // 提交清单
  const handleSubmit = async () => {
    setLoading(true)
    try {
      const payload = {
        ...formData,
        gps_lat: formData.gps_lat ? parseFloat(formData.gps_lat) : null,
        gps_lng: formData.gps_lng ? parseFloat(formData.gps_lng) : null,
        duration_minutes: formData.duration_minutes ? parseInt(formData.duration_minutes) : null,
        temperature: formData.temperature ? parseFloat(formData.temperature) : null,
        items: formItems,
      }

      const response = await fetch('http://localhost:8000/api/checklist/checklist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        alert('清单创建成功!')
        setShowForm(false)
        setFormData({
          checklist_date: new Date().toISOString().split('T')[0],
          location_name: '',
          gps_lat: '',
          gps_lng: '',
          start_time: '',
          duration_minutes: '',
          protocol: 'incidental',
          observer_name: '',
          weather: '',
          temperature: '',
          wind: '',
          notes: '',
        })
        setFormItems([])
        fetchChecklists()
        fetchStats()
      } else {
        const error = await response.json()
        alert(`创建失败：${error.detail}`)
      }
    } catch (error) {
      console.error('创建清单失败:', error)
      alert('创建失败')
    } finally {
      setLoading(false)
    }
  }

  // 添加清单项
  const addItem = () => {
    if (!currentItem.species_cn) {
      alert('请输入鸟种中文名')
      return
    }
    setFormItems([...formItems, { ...currentItem, id: Date.now() }])
    setCurrentItem({
      species_cn: '',
      species_en: '',
      scientific_name: '',
      count: 1,
      sex: '',
      age: '',
      behavior: '',
      notes: '',
    })
  }

  // 删除清单项
  const removeItem = (id: number) => {
    setFormItems(formItems.filter(item => item.id !== id))
  }

  // 导出清单
  const exportChecklist = async (id: number, format: string = 'xlsx') => {
    window.open(`http://localhost:8000/api/checklist/checklist/export/${id}?format=${format}`, '_blank')
  }

  // 删除清单
  const deleteChecklist = async (id: number) => {
    if (!confirm('确定要删除这个清单吗？')) return

    try {
      const response = await fetch(`http://localhost:8000/api/checklist/checklist/${id}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        alert('已删除')
        fetchChecklists()
        fetchStats()
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }

  return (
    <div className="container">
      <div className="page-header">
        <h2>观测清单</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? '取消' : '+ 新建清单'}
        </button>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_checklists}</div>
            <div className="stat-label">总清单数</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_species}</div>
            <div className="stat-label">累计物种</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_individuals}</div>
            <div className="stat-label">累计个体</div>
          </div>
        </div>
      )}

      {/* 新建表单 */}
      {showForm && (
        <div className="card" style={{ marginTop: '20px' }}>
          <h3>新建观测清单</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>观测日期 *</label>
              <input
                type="date"
                value={formData.checklist_date}
                onChange={e => setFormData({ ...formData, checklist_date: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>地点名称 *</label>
              <input
                type="text"
                value={formData.location_name}
                onChange={e => setFormData({ ...formData, location_name: e.target.value })}
                placeholder="例如：北京奥林匹克森林公园"
              />
            </div>
            <div className="form-group">
              <label>GPS 纬度</label>
              <input
                type="number"
                step="0.000001"
                value={formData.gps_lat}
                onChange={e => setFormData({ ...formData, gps_lat: e.target.value })}
                placeholder="例如：39.9042"
              />
            </div>
            <div className="form-group">
              <label>GPS 经度</label>
              <input
                type="number"
                step="0.000001"
                value={formData.gps_lng}
                onChange={e => setFormData({ ...formData, gps_lng: e.target.value })}
                placeholder="例如：116.4074"
              />
            </div>
            <div className="form-group">
              <label>开始时间</label>
              <input
                type="time"
                value={formData.start_time}
                onChange={e => setFormData({ ...formData, start_time: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>观测时长 (分钟)</label>
              <input
                type="number"
                value={formData.duration_minutes}
                onChange={e => setFormData({ ...formData, duration_minutes: e.target.value })}
                placeholder="例如：120"
              />
            </div>
            <div className="form-group">
              <label>观测类型</label>
              <select
                value={formData.protocol}
                onChange={e => setFormData({ ...formData, protocol: e.target.value })}
              >
                <option value="incidental">偶然观测</option>
                <option value="traveling">行进式</option>
                <option value="stationary">定点观测</option>
              </select>
            </div>
            <div className="form-group">
              <label>观察者</label>
              <input
                type="text"
                value={formData.observer_name}
                onChange={e => setFormData({ ...formData, observer_name: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>天气</label>
              <input
                type="text"
                value={formData.weather}
                onChange={e => setFormData({ ...formData, weather: e.target.value })}
                placeholder="例如：晴，多云，小雨"
              />
            </div>
            <div className="form-group">
              <label>温度 (°C)</label>
              <input
                type="number"
                step="0.1"
                value={formData.temperature}
                onChange={e => setFormData({ ...formData, temperature: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>风力</label>
              <input
                type="text"
                value={formData.wind}
                onChange={e => setFormData({ ...formData, wind: e.target.value })}
                placeholder="例如：微风，2-3 级"
              />
            </div>
          </div>

          <div className="form-group">
            <label>备注</label>
            <textarea
              rows={3}
              value={formData.notes}
              onChange={e => setFormData({ ...formData, notes: e.target.value })}
              placeholder="记录本次观测的其他信息..."
            />
          </div>

          <hr style={{ margin: '20px 0', borderColor: 'var(--border-color)' }} />

          <h4>添加鸟种</h4>
          <div className="form-grid">
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label>中文名 *</label>
              <input
                type="text"
                value={currentItem.species_cn}
                onChange={e => setCurrentItem({ ...currentItem, species_cn: e.target.value })}
                placeholder="例如：麻雀"
              />
            </div>
            <div className="form-group">
              <label>英文名</label>
              <input
                type="text"
                value={currentItem.species_en}
                onChange={e => setCurrentItem({ ...currentItem, species_en: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>学名</label>
              <input
                type="text"
                value={currentItem.scientific_name}
                onChange={e => setCurrentItem({ ...currentItem, scientific_name: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>数量</label>
              <input
                type="number"
                min="1"
                value={currentItem.count}
                onChange={e => setCurrentItem({ ...currentItem, count: parseInt(e.target.value) || 1 })}
              />
            </div>
            <div className="form-group">
              <label>性别</label>
              <select
                value={currentItem.sex}
                onChange={e => setCurrentItem({ ...currentItem, sex: e.target.value })}
              >
                <option value="">未知</option>
                <option value="雄">雄</option>
                <option value="雌">雌</option>
              </select>
            </div>
            <div className="form-group">
              <label>年龄</label>
              <select
                value={currentItem.age}
                onChange={e => setCurrentItem({ ...currentItem, age: e.target.value })}
              >
                <option value="">未知</option>
                <option value="成鸟">成鸟</option>
                <option value="亚成">亚成</option>
                <option value="幼鸟">幼鸟</option>
              </select>
            </div>
            <div className="form-group">
              <label>行为</label>
              <input
                type="text"
                value={currentItem.behavior}
                onChange={e => setCurrentItem({ ...currentItem, behavior: e.target.value })}
                placeholder="例如：觅食，鸣叫"
              />
            </div>
          </div>
          <button className="btn btn-secondary" onClick={addItem} style={{ marginTop: '10px' }}>
            + 添加鸟种
          </button>

          {/* 已添加的鸟种列表 */}
          {formItems.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>已添加 {formItems.length} 个鸟种</h4>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>中文名</th>
                    <th>数量</th>
                    <th>性别/年龄</th>
                    <th>行为</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {formItems.map(item => (
                    <tr key={item.id}>
                      <td>{item.species_cn}</td>
                      <td>{item.count}</td>
                      <td>{[item.sex, item.age].filter(Boolean).join(' / ') || '-'}</td>
                      <td>{item.behavior || '-'}</td>
                      <td>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => removeItem(item.id)}
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? '提交中...' : '提交清单'}
            </button>
          </div>
        </div>
      )}

      {/* 清单列表 */}
      <div className="card" style={{ marginTop: '20px' }}>
        <h3>历史清单</h3>
        {checklists.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>暂无观测清单</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>地点</th>
                <th>物种数</th>
                <th>个体数</th>
                <th>观察者</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {checklists.map(list => (
                <tr key={list.id}>
                  <td>{list.checklist_date}</td>
                  <td>{list.location_name}</td>
                  <td>{list.total_species}</td>
                  <td>{list.total_individuals}</td>
                  <td>{list.observer_name || '-'}</td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => viewChecklist(list.id)}
                    >
                      查看
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => exportChecklist(list.id)}
                      style={{ marginLeft: '5px' }}
                    >
                      导出
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => deleteChecklist(list.id)}
                      style={{ marginLeft: '5px' }}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* 清单详情弹窗 */}
      {selectedChecklist && (
        <div className="modal-overlay" onClick={() => setSelectedChecklist(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '800px' }}>
            <div className="modal-header">
              <h3>观测清单详情</h3>
              <button className="btn-close" onClick={() => setSelectedChecklist(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="stats-grid" style={{ marginBottom: '20px' }}>
                <div className="stat-card">
                  <div className="stat-label">观测日期</div>
                  <div className="stat-value" style={{ fontSize: '1.2rem' }}>
                    {selectedChecklist.checklist_date}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">地点</div>
                  <div className="stat-value" style={{ fontSize: '1rem' }}>
                    {selectedChecklist.location_name}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">物种数</div>
                  <div className="stat-value">{selectedChecklist.total_species}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">个体数</div>
                  <div className="stat-value">{selectedChecklist.total_individuals}</div>
                </div>
              </div>

              {(selectedChecklist.weather || selectedChecklist.temperature || selectedChecklist.wind) && (
                <div className="card" style={{ marginBottom: '20px' }}>
                  <h4>观测条件</h4>
                  <div className="form-grid">
                    {selectedChecklist.weather && (
                      <div><strong>天气:</strong> {selectedChecklist.weather}</div>
                    )}
                    {selectedChecklist.temperature && (
                      <div><strong>温度:</strong> {selectedChecklist.temperature}°C</div>
                    )}
                    {selectedChecklist.wind && (
                      <div><strong>风力:</strong> {selectedChecklist.wind}</div>
                    )}
                    {selectedChecklist.duration_minutes && (
                      <div><strong>时长:</strong> {selectedChecklist.duration_minutes} 分钟</div>
                    )}
                    {selectedChecklist.observer_name && (
                      <div><strong>观察者:</strong> {selectedChecklist.observer_name}</div>
                    )}
                  </div>
                </div>
              )}

              <h4>鸟种列表 ({selectedChecklist.items?.length || 0})</h4>
              {selectedChecklist.items && selectedChecklist.items.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>中文名</th>
                      <th>学名</th>
                      <th>数量</th>
                      <th>性别/年龄</th>
                      <th>行为</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedChecklist.items.map((item, idx) => (
                      <tr key={item.id}>
                        <td>{idx + 1}</td>
                        <td>
                          {item.species_cn}
                          {item.species_en && (
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                              {item.species_en}
                            </div>
                          )}
                        </td>
                        <td style={{ fontStyle: 'italic' }}>{item.scientific_name || '-'}</td>
                        <td>{item.count}</td>
                        <td>{[item.sex, item.age].filter(Boolean).join(' / ') || '-'}</td>
                        <td>{item.behavior || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>暂无鸟种记录</p>
              )}

              {selectedChecklist.notes && (
                <div style={{ marginTop: '20px' }}>
                  <h4>备注</h4>
                  <p style={{ whiteSpace: 'pre-wrap' }}>{selectedChecklist.notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
