import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { statsApi } from '../api/api'

const MONTHS = ['1 月', '2 月', '3 月', '4 月', '5 月', '6 月', '7 月', '8 月', '9 月', '10 月', '11 月', '12 月']

export default function AnnualReport() {
  const [loading, setLoading] = useState(true)
  const [report, setReport] = useState<any>(null)
  const [year, setYear] = useState(new Date().getFullYear())

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlYear = params.get('year')
    if (urlYear) setYear(parseInt(urlYear))
  }, [])

  useEffect(() => {
    loadReport()
  }, [year])

  const loadReport = async () => {
    setLoading(true)
    try {
      const data = await statsApi.getAnnualReport(year)
      setReport(data)
    } catch (error) {
      console.error('加载年度报告失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>加载年度报告中...</p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="container">
        <div className="card">
          <h2>暂无数据</h2>
          <p>该年份还没有观测记录</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container" style={{ maxWidth: '1000px' }}>
      {/* 报告头部 */}
      <div style={{ textAlign: 'center', padding: '40px 0', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '3rem', marginBottom: '10px' }}>🐦</div>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>{year} 年度观鸟报告</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          记录每一次与鸟类的相遇
        </p>
        <div style={{ marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
          <button
            className="btn btn-outline"
            onClick={() => setYear(year - 1)}
            disabled={year <= 2020}
          >
            ← {year - 1}
          </button>
          <button
            className="btn btn-outline"
            onClick={() => setYear(year + 1)}
            disabled={year >= new Date().getFullYear()}
          >
            {year + 1} →
          </button>
        </div>
      </div>

      {/* 年度总览 */}
      <div className="card mt-2" style={{ background: 'linear-gradient(135deg, var(--primary-color), var(--primary-dark))', color: 'white' }}>
        <h3 style={{ color: 'white', marginBottom: '20px' }}>年度总览</h3>
        <div className="stats-grid">
          <div className="stat-card" style={{ background: 'rgba(255,255,255,0.1)', border: 'none' }}>
            <div className="stat-value" style={{ color: 'white' }}>{report.summary.total_photos}</div>
            <div className="stat-label" style={{ color: 'rgba(255,255,255,0.8)' }}>拍摄照片</div>
          </div>
          <div className="stat-card" style={{ background: 'rgba(255,255,255,0.1)', border: 'none' }}>
            <div className="stat-value" style={{ color: 'white' }}>{report.summary.total_species}</div>
            <div className="stat-label" style={{ color: 'rgba(255,255,255,0.8)' }}>观测物种</div>
          </div>
          <div className="stat-card" style={{ background: 'rgba(255,255,255,0.1)', border: 'none' }}>
            <div className="stat-value" style={{ color: 'white' }}>{report.summary.observation_days}</div>
            <div className="stat-label" style={{ color: 'rgba(255,255,255,0.8)' }}>观测天数</div>
          </div>
          <div className="stat-card" style={{ background: 'rgba(255,255,255,0.1)', border: 'none' }}>
            <div className="stat-value" style={{ color: 'white' }}>{report.summary.total_individuals}</div>
            <div className="stat-label" style={{ color: 'rgba(255,255,255,0.8)' }}>累计个体</div>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: '20px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.2)' }}>
          <div style={{ fontSize: '1.1rem' }}>
            平均每天观测 <strong style={{ fontSize: '1.5rem' }}>{report.summary.avg_species_per_day}</strong> 种鸟类
          </div>
        </div>
      </div>

      {/* 最佳观测日 */}
      {report.best_days && report.best_days.length > 0 && (
        <div className="card mt-2">
          <h3 className="card-title">🏆 最佳观测日</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
            {report.best_days.map((day: any, idx: number) => (
              <div
                key={idx}
                style={{
                  padding: '15px',
                  background: idx === 0 ? 'linear-gradient(135deg, #FFD700, #FFA500)' : 'var(--background-color)',
                  borderRadius: 'var(--radius-lg)',
                  textAlign: 'center',
                  color: idx === 0 ? 'white' : 'inherit'
                }}
              >
                <div style={{ fontSize: '0.875rem', marginBottom: '5px', opacity: idx === 0 ? 0.9 : 1 }}>
                  {idx === 0 ? '🥇 冠军' : idx === 1 ? '🥈 亚军' : idx === 2 ? '🥉 季军' : `第${idx + 1}名`}
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '5px' }}>{day.species_count}</div>
                <div style={{ fontSize: '0.85rem', opacity: idx === 0 ? 0.9 : 1 }}>{day.date}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 月度趋势 */}
      <div className="card mt-2">
        <h3 className="card-title">📈 月度观测趋势</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={report.monthly_data.map((d: any) => ({
            ...d,
            monthName: MONTHS[d.month - 1]
          }))}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="monthName" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="photos" name="照片数" fill="#4F81BD" />
            <Bar yAxisId="right" dataKey="species" name="物种数" fill="#C0504E" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 物种排行榜 */}
      <div className="card mt-2">
        <h3 className="card-title">🏅 热门物种排行榜</h3>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>物种名</th>
                <th>学名</th>
                <th>观测次数</th>
              </tr>
            </thead>
            <tbody>
              {report.top_species.map((species: any, idx: number) => (
                <tr key={idx}>
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
                  <td style={{ fontWeight: '600' }}>{species.species_cn}</td>
                  <td style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>{species.scientific_name}</td>
                  <td>
                    <span className="bird-tag">{species.count}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 新观测物种 */}
      {report.new_species && report.new_species.length > 0 && (
        <div className="card mt-2">
          <h3 className="card-title">✨ 新观测物种</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {report.new_species.map((species: any, idx: number) => (
              <span
                key={idx}
                className="species-tag"
                style={{ fontSize: '0.875rem' }}
              >
                {species.species_cn}
                <span style={{ marginLeft: '8px', opacity: 0.8, fontSize: '0.75rem' }}>
                  {species.first_seen}
                </span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 热门观测地点 */}
      {report.top_locations && report.top_locations.length > 0 && (
        <div className="card mt-2">
          <h3 className="card-title">📍 热门观测地点</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            {report.top_locations.map((loc: any, idx: number) => (
              <div
                key={idx}
                style={{
                  padding: '15px',
                  background: 'var(--background-color)',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                  第 {idx + 1} 名
                </div>
                <div style={{ fontSize: '0.85rem', marginBottom: '10px' }}>
                  📍 {loc.lat}, {loc.lng}
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--primary-color)' }}>
                  {loc.days} 天
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 页脚 */}
      <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
        Quick Pick Birds • {year} 年度观鸟报告
        <div style={{ marginTop: '10px' }}>
          生成时间：{new Date().toLocaleDateString('zh-CN')}
        </div>
      </div>
    </div>
  )
}
