import { useState, useEffect } from 'react'
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { statsApi } from '../api/api'

// 颜色配色
const COLORS = ['#4F81BD', '#C0504E', '#9BBB58', '#8064A2', '#4AACC5', '#F79646', '#815E87', '#76A035', '#3465A4', '#B74D29']

const MONTHS = ['1 月', '2 月', '3 月', '4 月', '5 月', '6 月', '7 月', '8 月', '9 月', '10 月', '11 月', '12 月']

export default function Statistics() {
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<any>(null)
  const [speciesData, setSpeciesData] = useState<any[]>([])
  const [monthlyData, setMonthlyData] = useState<any[]>([])
  const [topSpecies, setTopSpecies] = useState<any[]>([])
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())

  useEffect(() => {
    loadStatistics()
  }, [selectedYear])

  const loadStatistics = async () => {
    setLoading(true)
    try {
      // 加载概览数据
      const overviewData = await statsApi.getOverview()
      setOverview(overviewData)

      // 加载物种分布
      const speciesDist = await statsApi.getSpeciesDistribution(selectedYear)
      setSpeciesData(speciesDist.data)

      // 加载月度趋势
      const monthly = await statsApi.getMonthlyTrend(selectedYear)
      setMonthlyData(monthly.data.map((d: any) => ({
        ...d,
        monthName: MONTHS[parseInt(d.month) - 1]
      })))

      // 加载热门物种
      const top = await statsApi.getTopSpecies(10)
      setTopSpecies(top)
    } catch (err: any) {
      console.error('Failed to load statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>加载统计数据中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      {/* 概览统计卡片 */}
      {overview && (
        <div className="card mb-2">
          <h2 className="card-title">总体概览</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{overview.total_photos}</div>
              <div className="stat-label">总照片数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.total_species}</div>
              <div className="stat-label">物种数量</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.observation_days}</div>
              <div className="stat-label">观测天数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.recommended_photos}</div>
              <div className="stat-label">推荐照片</div>
            </div>
          </div>
          <div className="mt-2" style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#4F81BD' }}>
                {overview.month_stats?.photos || 0}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#666' }}>本月照片</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#C0504E' }}>
                {overview.month_stats?.species || 0}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#666' }}>本月物种</div>
            </div>
          </div>
        </div>
      )}

      {/* 年份选择器 */}
      <div className="card mb-2">
        <div className="flex-between">
          <h2 className="card-title" style={{ marginBottom: 0 }}>统计图表</h2>
          <div className="flex gap-1">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              年份：
              <input
                type="number"
                className="input"
                style={{ width: '80px' }}
                value={selectedYear}
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                min={2020}
                max={new Date().getFullYear()}
              />
            </label>
          </div>
        </div>
      </div>

      {/* 物种分布饼图和月度趋势图 */}
      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* 物种分布 */}
        <div className="card">
          <h3 className="card-title">物种分布</h3>
          {speciesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={speciesData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ species_cn, percentage }) => `${species_cn}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {speciesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty">
              <div className="empty-icon">📊</div>
              <p>暂无物种数据</p>
            </div>
          )}
        </div>

        {/* 月度趋势 */}
        <div className="card">
          <h3 className="card-title">{selectedYear} 年月度趋势</h3>
          {monthlyData.some(d => d.photo_count > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="monthName" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="photo_count" name="照片数" fill="#4F81BD" />
                <Bar yAxisId="right" dataKey="species_count" name="物种数" fill="#C0504E" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty">
              <div className="empty-icon">📈</div>
              <p>暂无观测数据</p>
            </div>
          )}
        </div>
      </div>

      {/* 月度观测天数趋势 */}
      <div className="card mt-2">
        <h3 className="card-title">{selectedYear} 年观测天数趋势</h3>
        {monthlyData.some(d => d.observation_days > 0) ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="monthName" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="observation_days" name="观测天数" stroke="#9BBB58" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty">
            <div className="empty-icon">📉</div>
            <p>暂无观测数据</p>
          </div>
        )}
      </div>

      {/* 热门物种排行榜 */}
      <div className="card mt-2">
        <h3 className="card-title">热门物种排行榜 (Top 10)</h3>
        {topSpecies.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>排名</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>物种名</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>学名</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd' }}>观测次数</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd' }}>观测天数</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd' }}>首次观测</th>
                  <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd' }}>最近观测</th>
                </tr>
              </thead>
              <tbody>
                {topSpecies.map((species, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        display: 'inline-block',
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: index < 3 ? '#FFD700' : index < 5 ? '#C0C0C0' : '#CD7F32',
                        color: index < 3 ? '#000' : '#fff',
                        textAlign: 'center',
                        lineHeight: '24px',
                        fontSize: '0.875rem'
                      }}>
                        {index + 1}
                      </span>
                    </td>
                    <td style={{ padding: '12px', fontWeight: '500' }}>{species.species_cn}</td>
                    <td style={{ padding: '12px', fontStyle: 'italic', color: '#666' }}>{species.species_en}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span className="bird-tag">{species.count}</span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{species.observation_days}</td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#666' }}>{species.first_seen || '-'}</td>
                    <td style={{ padding: '12px', textAlign: 'center', color: '#666' }}>{species.last_seen || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty">
            <div className="empty-icon">🏆</div>
            <p>暂无物种数据</p>
          </div>
        )}
      </div>
    </div>
  )
}
