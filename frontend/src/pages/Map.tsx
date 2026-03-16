import { useState, useEffect } from 'react'
import { mapApi } from '../api/api'

export default function Map() {
  const [mapDate, setMapDate] = useState(new Date().toISOString().split('T')[0])
  const [loading, setLoading] = useState(false)
  const [mapData, setMapData] = useState<any>(null)
  const [mapHtml, setMapHtml] = useState<string>('')
  const [heatmapMode, setHeatmapMode] = useState(false)
  const [heatmapData, setHeatmapData] = useState<any>(null)

  const loadDailyMap = async () => {
    setLoading(true)
    setHeatmapMode(false)
    try {
      const response = await mapApi.getDailyMap(mapDate)
      setMapData(response.data)
      if (response.data.map_html) {
        setMapHtml(response.data.map_html)
      }
    } catch (err: any) {
      console.error('Failed to load map:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadHeatmap = async () => {
    setLoading(true)
    setHeatmapMode(true)
    try {
      const response = await mapApi.getHeatmap()
      setHeatmapData(response.data)
      if (response.data.map_html) {
        setMapHtml(response.data.map_html)
      }
    } catch (err: any) {
      console.error('Failed to load heatmap:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDailyMap()
  }, [mapDate])

  return (
    <div className="container">
      <div className="card">
        <div className="flex-between mb-2">
          <h2 className="card-title" style={{ marginBottom: 0 }}>观鸟地图</h2>
          <div className="flex gap-1">
            <input
              type="date"
              className="input"
              value={mapDate}
              onChange={(e) => setMapDate(e.target.value)}
              disabled={heatmapMode}
            />
            <button
              className={`btn ${heatmapMode ? 'btn-outline' : 'btn-primary'}`}
              onClick={() => !heatmapMode && loadHeatmap()}
            >
              🔥 热力图
            </button>
            <button className="btn btn-primary" onClick={loadDailyMap} disabled={loading}>
              {loading ? '加载中...' : '刷新'}
            </button>
          </div>
        </div>

        {mapData && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{mapData.total_photos}</div>
                <div className="stat-label">当日照片</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{mapData.total_locations}</div>
                <div className="stat-label">观测地点</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{mapData.bird_species_count}</div>
                <div className="stat-label">鸟种数量</div>
              </div>
            </div>

            {mapData.species_summary && Object.keys(mapData.species_summary).length > 0 && (
              <div className="mb-2">
                <h4 style={{ marginBottom: '10px', fontSize: '1rem' }}>鸟种统计</h4>
                <div>
                  {Object.entries(mapData.species_summary as Record<string, number>).map(([species, count]) => (
                    <span key={species} className="bird-tag">
                      {species}
                      <span className="count">{count}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <div className="card">
        <div className="flex-between mb-2">
          <h3 className="card-title" style={{ marginBottom: 0 }}>观测地点分布</h3>
          {heatmapData && (
            <span className="bird-tag">热力点：{heatmapData.hotspot_count}</span>
          )}
        </div>
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>加载地图中...</p>
          </div>
        ) : mapHtml ? (
          <div
            className="map-container"
            dangerouslySetInnerHTML={{ __html: mapHtml }}
          />
        ) : (
          <div className="empty">
            <div className="empty-icon">🗺️</div>
            <p>暂无地图数据</p>
            <p className="text-muted">
              请先在「扫描」页面扫描带有 GPS 信息的照片
            </p>
          </div>
        )}
      </div>

      {mapData?.points?.length > 0 && (
        <div className="card">
          <h3 className="card-title">观测点详情</h3>
          <div className="grid">
            {mapData.points.map((point: any, index: number) => (
              <div key={index} className="card" style={{ padding: '15px' }}>
                <div className="flex-between">
                  <strong>{point.title}</strong>
                  <span className="bird-tag">{point.icon_color}</span>
                </div>
                <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '8px' }}>
                  坐标：{point.lat.toFixed(4)}, {point.lon.toFixed(4)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
