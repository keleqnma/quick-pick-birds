import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

interface Hotspot {
  id: number
  name: string
  gps_lat: number
  gps_lng: number
  city?: string
  province?: string
  habitat_type?: string
  visit_count: number
  distance_km?: number
}

interface MapCenterProps {
  lat: number
  lng: number
  zoom: number
}

// 修复 Leaflet 默认图标问题
const birdIcon = L.icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

function MapCenter({ lat, lng, zoom }: MapCenterProps) {
  const map = useMap()
  useEffect(() => {
    map.flyTo([lat, lng], zoom)
  }, [lat, lng, zoom, map])
  return null
}

export default function HotspotsMap() {
  const [loading, setLoading] = useState(true)
  const [hotspots, setHotspots] = useState<Hotspot[]>([])
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(null)
  const [mapCenter, setMapCenter] = useState({ lat: 35.8617, lng: 104.1954, zoom: 4 })
  const [showForm, setShowForm] = useState(false)
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null)
  const [newHotspot, setNewHotspot] = useState({
    name: '',
    description: '',
    gps_lat: '',
    gps_lng: '',
    city: '',
    province: '',
    habitat_type: ''
  })

  useEffect(() => {
    loadHotspots()
  }, [])

  const loadHotspots = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/hotspots/hotspots?limit=100')
      const data = await response.json()
      setHotspots(data.hotspots || [])
    } catch (error) {
      console.error('加载热点失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          setUserLocation({ lat: latitude, lng: longitude })
          setMapCenter({ lat: latitude, lng: longitude, zoom: 12 })
          loadNearbyHotspots(latitude, longitude)
        },
        (error) => {
          console.error('获取位置失败:', error)
          alert('无法获取您的位置，请允许浏览器访问位置信息')
        }
      )
    } else {
      alert('您的浏览器不支持地理位置功能')
    }
  }

  const loadNearbyHotspots = async (lat: number, lng: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/hotspots/hotspots/recommended?lat=${lat}&lng=${lng}&limit=20`)
      const data = await response.json()
      setHotspots(data.recommended || [])
    } catch (error) {
      console.error('加载附近热点失败:', error)
    }
  }

  const handleCreateHotspot = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:8000/api/hotspots/hotspot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newHotspot,
          gps_lat: parseFloat(newHotspot.gps_lat),
          gps_lng: parseFloat(newHotspot.gps_lng)
        })
      })
      const data = await response.json()
      if (data.id) {
        alert('热点创建成功!')
        setShowForm(false)
        setNewHotspot({
          name: '', description: '', gps_lat: '', gps_lng: '',
          city: '', province: '', habitat_type: ''
        })
        loadHotspots()
      }
    } catch (error) {
      console.error('创建热点失败:', error)
      alert('创建失败，请重试')
    }
  }

  const handleMapClick = (e: any) => {
    const { lat, lng } = e.latlng
    setNewHotspot(prev => ({
      ...prev,
      gps_lat: lat.toFixed(6),
      gps_lng: lng.toFixed(6)
    }))
    setShowForm(true)
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>加载热点地图中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container" style={{ maxWidth: '100%' }}>
      <div className="page-header">
        <h2>🗺️ 观鸟热点地图</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-outline" onClick={getUserLocation}>
            📍 我在哪
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            ➕ 新增热点
          </button>
        </div>
      </div>

      {/* 热点统计 */}
      <div className="card mb-2">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{hotspots.length}</div>
            <div className="stat-label">热点数量</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {hotspots.reduce((sum, h) => sum + (h.visit_count || 0), 0)}
            </div>
            <div className="stat-label">累计访问</div>
          </div>
        </div>
      </div>

      {/* 地图 */}
      <div className="card">
        <h3 className="card-title">热点分布</h3>
        <div style={{ height: '600px', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
          <MapContainer
            center={[mapCenter.lat, mapCenter.lng]}
            zoom={mapCenter.zoom}
            style={{ height: '100%', width: '100%' }}
            onClick={handleMapClick}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapCenter lat={mapCenter.lat} lng={mapCenter.lng} zoom={mapCenter.zoom} />

            {/* 用户位置标记 */}
            {userLocation && (
              <Marker
                position={[userLocation.lat, userLocation.lng]}
                icon={L.icon({
                  ...birdIcon.options,
                  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-green.png'
                })}
              >
                <Popup>📍 我的位置</Popup>
              </Marker>
            )}

            {/* 热点标记 */}
            {hotspots.map(hotspot => (
              <Marker
                key={hotspot.id}
                position={[hotspot.gps_lat, hotspot.gps_lng]}
                icon={birdIcon}
                eventHandlers={{
                  click: () => setSelectedHotspot(hotspot)
                }}
              >
                <Popup>
                  <div style={{ minWidth: '200px' }}>
                    <h4 style={{ margin: '0 0 8px 0', color: 'var(--primary-color)' }}>
                      {hotspot.name}
                    </h4>
                    {hotspot.city && <p style={{ margin: '4px 0' }}>📍 {hotspot.city}</p>}
                    {hotspot.province && <p style={{ margin: '4px 0' }}>🏔️ {hotspot.province}</p>}
                    {hotspot.habitat_type && <p style={{ margin: '4px 0' }}>🌿 {hotspot.habitat_type}</p>}
                    {hotspot.distance_km !== undefined && (
                      <p style={{ margin: '4px 0', color: 'var(--text-secondary)' }}>
                        📏 距离：{hotspot.distance_km} km
                      </p>
                    )}
                    <p style={{ margin: '4px 0', fontWeight: '600' }}>
                      🔥 访问：{hotspot.visit_count} 次
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '10px' }}>
          💡 点击地图可以添加新热点，点击标记查看详情
        </p>
      </div>

      {/* 热点列表 */}
      <div className="card mt-2">
        <h3 className="card-title">热点列表</h3>
        {hotspots.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>名称</th>
                  <th>位置</th>
                  <th>栖息地</th>
                  <th>访问次数</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {hotspots.map((hotspot, idx) => (
                  <tr key={hotspot.id}>
                    <td>
                      <span style={{
                        display: 'inline-block',
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: idx === 0 ? '#FFD700' : idx === 1 ? '#C0C0C0' : idx === 2 ? '#CD7F32' : 'var(--border-light)',
                        color: idx < 3 ? '#000' : 'inherit',
                        textAlign: 'center',
                        lineHeight: '28px',
                        fontWeight: 'bold'
                      }}>
                        {idx + 1}
                      </span>
                    </td>
                    <td style={{ fontWeight: '600' }}>{hotspot.name}</td>
                    <td>
                      {hotspot.province}{hotspot.city && `·${hotspot.city}`}
                    </td>
                    <td>{hotspot.habitat_type || '-'}</td>
                    <td>
                      <span className="bird-tag">{hotspot.visit_count}</span>
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => {
                          setMapCenter({ lat: hotspot.gps_lat, lng: hotspot.gps_lng, zoom: 14 })
                        }}
                      >
                        定位
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty">
            <div className="empty-icon">🗺️</div>
            <p>暂无热点数据</p>
          </div>
        )}
      </div>

      {/* 新增热点模态框 */}
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h3>新增观鸟热点</h3>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>
            <form onSubmit={handleCreateHotspot}>
              <div className="form-group">
                <label>热点名称 *</label>
                <input
                  type="text"
                  className="input"
                  value={newHotspot.name}
                  onChange={e => setNewHotspot(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="如：北京奥林匹克森林公园"
                  required
                />
              </div>
              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div className="form-group">
                  <label>纬度 *</label>
                  <input
                    type="number"
                    step="0.000001"
                    className="input"
                    value={newHotspot.gps_lat}
                    onChange={e => setNewHotspot(prev => ({ ...prev, gps_lat: e.target.value }))}
                    placeholder="39.9042"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>经度 *</label>
                  <input
                    type="number"
                    step="0.000001"
                    className="input"
                    value={newHotspot.gps_lng}
                    onChange={e => setNewHotspot(prev => ({ ...prev, gps_lng: e.target.value }))}
                    placeholder="116.4074"
                    required
                  />
                </div>
              </div>
              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div className="form-group">
                  <label>省份</label>
                  <input
                    type="text"
                    className="input"
                    value={newHotspot.province}
                    onChange={e => setNewHotspot(prev => ({ ...prev, province: e.target.value }))}
                    placeholder="北京市"
                  />
                </div>
                <div className="form-group">
                  <label>城市</label>
                  <input
                    type="text"
                    className="input"
                    value={newHotspot.city}
                    onChange={e => setNewHotspot(prev => ({ ...prev, city: e.target.value }))}
                    placeholder="北京市"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>栖息地类型</label>
                <select
                  className="input"
                  value={newHotspot.habitat_type}
                  onChange={e => setNewHotspot(prev => ({ ...prev, habitat_type: e.target.value }))}
                >
                  <option value="">请选择</option>
                  <option value="森林">森林</option>
                  <option value="湿地">湿地</option>
                  <option value="公园">公园</option>
                  <option value="草原">草原</option>
                  <option value="农田">农田</option>
                  <option value="海岸">海岸</option>
                  <option value="山地">山地</option>
                  <option value="城市">城市</option>
                  <option value="荒漠">荒漠</option>
                </select>
              </div>
              <div className="form-group">
                <label>描述</label>
                <textarea
                  className="input"
                  rows={3}
                  value={newHotspot.description}
                  onChange={e => setNewHotspot(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="简要描述该热点的特点..."
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>
                  取消
                </button>
                <button type="submit" className="btn btn-primary">
                  创建热点
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
