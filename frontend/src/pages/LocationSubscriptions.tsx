import { useState, useEffect } from 'react'
import { subscriptionsApi } from '../api/api'

interface Subscription {
  id: number
  user_name: string
  location_name: string
  gps_lat?: number
  gps_lng?: number
  radius_km: number
  notification_enabled: boolean
  email_enabled: boolean
  wechat_enabled: boolean
  min_species_count: number
  created_at: string
  last_notified_at?: string
  is_active: boolean
}

export default function LocationSubscriptions() {
  const [loading, setLoading] = useState(true)
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [showForm, setShowForm] = useState(false)
  const [userName, setUserName] = useState('birdwatcher')
  const [newSubscription, setNewSubscription] = useState({
    location_name: '',
    gps_lat: '',
    gps_lng: '',
    radius_km: 5,
    notification_enabled: true,
    email_enabled: false,
    wechat_enabled: false,
    min_species_count: 1
  })

  useEffect(() => {
    loadSubscriptions()
  }, [userName])

  const loadSubscriptions = async () => {
    setLoading(true)
    try {
      const data = await subscriptionsApi.getSubscriptions(userName)
      setSubscriptions(data.data.subscriptions || [])
    } catch (error) {
      console.error('加载订阅失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSubscription = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = await subscriptionsApi.createSubscription({
        user_name: userName,
        ...newSubscription,
        gps_lat: newSubscription.gps_lat ? parseFloat(newSubscription.gps_lat) : undefined,
        gps_lng: newSubscription.gps_lng ? parseFloat(newSubscription.gps_lng) : undefined
      })
      if (data.data.id) {
        alert('订阅创建成功!')
        setShowForm(false)
        setNewSubscription({
          location_name: '',
          gps_lat: '',
          gps_lng: '',
          radius_km: 5,
          notification_enabled: true,
          email_enabled: false,
          wechat_enabled: false,
          min_species_count: 1
        })
        loadSubscriptions()
      }
    } catch (error) {
      console.error('创建订阅失败:', error)
      alert('创建失败，请重试')
    }
  }

  const handleToggleSubscription = async (id: number) => {
    try {
      await subscriptionsApi.toggleSubscription(id)
      loadSubscriptions()
    } catch (error) {
      console.error('切换订阅状态失败:', error)
    }
  }

  const handleDeleteSubscription = async (id: number) => {
    if (!confirm('确定要删除这个订阅吗？')) return
    try {
      await subscriptionsApi.deleteSubscription(id)
      loadSubscriptions()
    } catch (error) {
      console.error('删除订阅失败:', error)
    }
  }

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          setNewSubscription(prev => ({
            ...prev,
            gps_lat: latitude.toFixed(6),
            gps_lng: longitude.toFixed(6)
          }))
        },
        (error) => {
          console.error('获取位置失败:', error)
        }
      )
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>加载订阅列表中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-header">
        <h2>🔔 地点订阅管理</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          ➕ 新增订阅
        </button>
      </div>

      {/* 用户设置 */}
      <div className="card mb-2">
        <h3 className="card-title">订阅设置</h3>
        <div className="form-group">
          <label>用户名</label>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              className="input"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="输入您的用户名"
              style={{ flex: 1 }}
            />
            <button className="btn btn-outline" onClick={loadSubscriptions}>
              加载订阅
            </button>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
            💡 订阅后，当指定地点附近有新观测记录时，您会收到通知
          </p>
        </div>
      </div>

      {/* 订阅统计 */}
      {subscriptions.length > 0 && (
        <div className="card mb-2">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{subscriptions.length}</div>
              <div className="stat-label">订阅地点</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {subscriptions.filter(s => s.is_active).length}
              </div>
              <div className="stat-label">活跃订阅</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {subscriptions.filter(s => s.notification_enabled).length}
              </div>
              <div className="stat-label">开启通知</div>
            </div>
          </div>
        </div>
      )}

      {/* 订阅列表 */}
      <div className="card">
        <h3 className="card-title">我的订阅</h3>
        {subscriptions.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>地点名称</th>
                  <th>半径</th>
                  <th>最小物种数</th>
                  <th>通知方式</th>
                  <th>创建时间</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {subscriptions.map(sub => (
                  <tr key={sub.id} style={{ opacity: sub.is_active ? 1 : 0.6 }}>
                    <td style={{ fontWeight: '600' }}>{sub.location_name}</td>
                    <td>{sub.radius_km} km</td>
                    <td>{sub.min_species_count} 种</td>
                    <td>
                      <div style={{ display: 'flex', gap: '5px' }}>
                        {sub.notification_enabled && (
                          <span className="bird-tag" style={{ fontSize: '0.75rem' }}>🔔</span>
                        )}
                        {sub.email_enabled && (
                          <span className="bird-tag" style={{ fontSize: '0.75rem' }}>📧</span>
                        )}
                        {sub.wechat_enabled && (
                          <span className="bird-tag" style={{ fontSize: '0.75rem' }}>💬</span>
                        )}
                      </div>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {new Date(sub.created_at).toLocaleDateString('zh-CN')}
                    </td>
                    <td>
                      <span
                        className={`bird-tag ${sub.is_active ? '' : 'bird-tag-outline'}`}
                        style={{ fontSize: '0.75rem' }}
                      >
                        {sub.is_active ? '✓ 活跃' : '○ 已禁用'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button
                          className="btn btn-sm btn-outline"
                          onClick={() => handleToggleSubscription(sub.id)}
                        >
                          {sub.is_active ? '禁用' : '启用'}
                        </button>
                        <button
                          className="btn btn-sm btn-outline"
                          onClick={() => handleDeleteSubscription(sub.id)}
                          style={{ color: 'var(--error-color)' }}
                        >
                          删除
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty">
            <div className="empty-icon">🔔</div>
            <p>暂无订阅地点</p>
            <button className="btn btn-primary mt-2" onClick={() => setShowForm(true)}>
              创建第一个订阅
            </button>
          </div>
        )}
      </div>

      {/* 新增订阅模态框 */}
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h3>新增地点订阅</h3>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>
            <form onSubmit={handleCreateSubscription}>
              <div className="form-group">
                <label>地点名称 *</label>
                <input
                  type="text"
                  className="input"
                  value={newSubscription.location_name}
                  onChange={e => setNewSubscription(prev => ({ ...prev, location_name: e.target.value }))}
                  placeholder="如：我家附近的公园"
                  required
                />
              </div>

              <div className="form-group">
                <label>地理位置（可选）</label>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input
                    type="number"
                    step="0.000001"
                    className="input"
                    value={newSubscription.gps_lat}
                    onChange={e => setNewSubscription(prev => ({ ...prev, gps_lat: e.target.value }))}
                    placeholder="纬度"
                    style={{ flex: 1 }}
                  />
                  <input
                    type="number"
                    step="0.000001"
                    className="input"
                    value={newSubscription.gps_lng}
                    onChange={e => setNewSubscription(prev => ({ ...prev, gps_lng: e.target.value }))}
                    placeholder="经度"
                    style={{ flex: 1 }}
                  />
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={getUserLocation}
                    title="使用当前位置"
                  >
                    📍
                  </button>
                </div>
              </div>

              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div className="form-group">
                  <label>监控半径 (km)</label>
                  <input
                    type="number"
                    className="input"
                    value={newSubscription.radius_km}
                    onChange={e => setNewSubscription(prev => ({ ...prev, radius_km: parseInt(e.target.value) }))}
                    min="1"
                    max="50"
                  />
                </div>
                <div className="form-group">
                  <label>最小物种数</label>
                  <input
                    type="number"
                    className="input"
                    value={newSubscription.min_species_count}
                    onChange={e => setNewSubscription(prev => ({ ...prev, min_species_count: parseInt(e.target.value) }))}
                    min="1"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>通知方式</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={newSubscription.notification_enabled}
                      onChange={e => setNewSubscription(prev => ({ ...prev, notification_enabled: e.target.checked }))}
                    />
                    🔔 应用内通知
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={newSubscription.email_enabled}
                      onChange={e => setNewSubscription(prev => ({ ...prev, email_enabled: e.target.checked }))}
                    />
                    📧 邮件通知（暂未实现）
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={newSubscription.wechat_enabled}
                      onChange={e => setNewSubscription(prev => ({ ...prev, wechat_enabled: e.target.checked }))}
                    />
                    💬 微信通知（暂未实现）
                  </label>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>
                  取消
                </button>
                <button type="submit" className="btn btn-primary">
                  创建订阅
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
