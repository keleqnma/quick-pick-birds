import { useState, useEffect } from 'react'
import { summaryApi } from '../api/api'

interface CalendarDay {
  date: string
  day: number
  photo_count: number
  species_count: number
  species_list: string[]
}

type ViewMode = 'year' | 'month' | 'day'

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<ViewMode>('month')
  const [calendarData, setCalendarData] = useState<CalendarDay[]>([])
  const [selectedDay, setSelectedDay] = useState<CalendarDay | null>(null)
  const [loading, setLoading] = useState(false)
  const [yearlySummary, setYearlySummary] = useState<{
    total_photos: number
    total_species: number
    observation_days: number
    recommended_photos: number
  } | null>(null)

  // 加载日历数据
  useEffect(() => {
    loadCalendarData()
    loadYearlySummary()
  }, [currentDate, viewMode])

  const loadCalendarData = async () => {
    setLoading(true)
    try {
      if (viewMode === 'month' || viewMode === 'day') {
        const response = await summaryApi.get_calendar(
          currentDate.getFullYear(),
          currentDate.getMonth() + 1
        )
        setCalendarData(response.data.days || [])
      }
    } catch (err: any) {
      console.error('加载日历数据失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadYearlySummary = async () => {
    try {
      const response = await summaryApi.get_yearly_summary(currentDate.getFullYear())
      setYearlySummary(response.data)
    } catch (err: any) {
      console.error('加载年度摘要失败:', err)
    }
  }

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))
  }

  const prevYear = () => {
    setCurrentDate(new Date(currentDate.getFullYear() - 1, 0, 1))
  }

  const nextYear = () => {
    setCurrentDate(new Date(currentDate.getFullYear() + 1, 0, 1))
  }

  const goToToday = () => {
    setCurrentDate(new Date())
    setViewMode('month')
  }

  const handleDayClick = (day: CalendarDay) => {
    setSelectedDay(day)
    setViewMode('day')
  }

  const getDayData = (day: number) => {
    return calendarData.find(d => d.day === day)
  }

  const renderYearView = () => {
    const months = '一月，二月，三月，四月，五月，六月，七月，八月，九月，十月，十一月，十二月'.split('，')
    const year = currentDate.getFullYear()

    return (
      <div className="card">
        <div className="flex-between mb-3">
          <button className="btn btn-outline" onClick={prevYear}>{'<'}</button>
          <h3 style={{ margin: 0 }}>{year}年</h3>
          <button className="btn btn-outline" onClick={nextYear}>{'>'}</button>
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '15px'
        }}>
          {months.map((month, i) => {
            const isCurrentMonth = i === new Date().getMonth() && year === new Date().getFullYear()
            return (
              <div
                key={month}
                className="clickable-card"
                onClick={() => {
                  setCurrentDate(new Date(year, i, 1))
                  setViewMode('month')
                }}
                style={{
                  padding: '20px',
                  borderRadius: '8px',
                  border: isCurrentMonth ? '2px solid var(--primary)' : '1px solid var(--border)',
                  background: isCurrentMonth ? 'var(--bg-secondary)' : 'white',
                  cursor: 'pointer',
                  textAlign: 'center'
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: '8px' }}>{month}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {year}年
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  const renderMonthView = () => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth() + 1
    const monthNames = '一月，二月，三月，四月，五月，六月，七月，八月，九月，十月，十一月，十二月'.split('，')
    const weekDays = '日，一，二，三，四，五，六'.split('，')
    const daysInMonth = new Date(year, month, 0).getDate()
    const firstDayOfMonth = new Date(year, month - 1, 1).getDay()

    return (
      <div className="card">
        <div className="flex-between mb-3">
          <button className="btn btn-outline" onClick={prevMonth}>{'<'}</button>
          <div style={{ textAlign: 'center' }}>
            <h3 style={{ margin: 0 }}>{year}年{monthNames[month - 1]}</h3>
            {yearlySummary && (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                本月观测：{yearlySummary.observation_days}天 · {yearlySummary.total_photos}张照片 · {yearlySummary.total_species}种鸟类
              </p>
            )}
          </div>
          <button className="btn btn-outline" onClick={nextMonth}>{'>'}</button>
        </div>

        {/* 星期标题 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '4px',
          marginBottom: '8px'
        }}>
          {weekDays.map(day => (
            <div key={day} style={{
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '0.85rem',
              color: 'var(--text-secondary)',
              padding: '8px 0'
            }}>
              {day}
            </div>
          ))}
        </div>

        {/* 日历网格 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '4px'
        }}>
          {/* 空白占位 */}
          {Array.from({ length: firstDayOfMonth }).map((_, i) => (
            <div key={`empty-${i}`} style={{ padding: '10px' }} />
          ))}

          {/* 日期 */}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1
            const dayData = getDayData(day)
            const isToday = day === new Date().getDate() &&
              month === new Date().getMonth() + 1 &&
              year === new Date().getFullYear()
            const hasData = !!dayData

            return (
              <div
                key={day}
                className={`calendar-day ${hasData ? 'has-data' : ''} ${isToday ? 'today' : ''}`}
                onClick={() => dayData && handleDayClick(dayData)}
                style={{
                  aspectRatio: '1',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '8px 4px',
                  borderRadius: '8px',
                  border: isToday ? '2px solid var(--primary)' : '1px solid var(--border)',
                  background: hasData ? 'var(--bg-secondary)' : 'white',
                  cursor: hasData ? 'pointer' : 'default',
                  transition: 'all 0.2s',
                  position: 'relative'
                }}
              >
                <span style={{
                  fontWeight: hasData ? 600 : 400,
                  fontSize: '0.95rem',
                  marginBottom: '4px'
                }}>
                  {day}
                </span>
                {hasData && (
                  <>
                    <span style={{
                      fontSize: '0.7rem',
                      color: 'var(--text-secondary)'
                    }}>
                      {dayData.photo_count}张
                    </span>
                    {dayData.species_count > 0 && (
                      <span
                        style={{
                          position: 'absolute',
                          bottom: '4px',
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          background: 'var(--primary)'
                        }}
                      />
                    )}
                  </>
                )}
              </div>
            )
          })}
        </div>

        {/* 图例 */}
        <div style={{
          display: 'flex',
          gap: '20px',
          marginTop: '15px',
          paddingTop: '15px',
          borderTop: '1px solid var(--border)',
          fontSize: '0.85rem',
          color: 'var(--text-secondary)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '16px',
              height: '16px',
              borderRadius: '4px',
              border: '2px solid var(--primary)'
            }} />
            <span>今天</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '16px',
              height: '16px',
              borderRadius: '4px',
              background: 'var(--bg-secondary)'
            }} />
            <span>有观测记录</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: 'var(--primary)'
            }} />
            <span>有物种记录</span>
          </div>
        </div>
      </div>
    )
  }

  const renderDayView = () => {
    if (!selectedDay) return null

    return (
      <div className="card">
        <div className="flex-between mb-3">
          <button
            className="btn btn-outline"
            onClick={() => setViewMode('month')}
          >
            {'<'} 返回月视图
          </button>
          <h3 style={{ margin: 0 }}>
            {currentDate.getFullYear()}年{currentDate.getMonth() + 1}月{selectedDay.day}日
          </h3>
          <div style={{ width: '100px' }} />
        </div>

        <div className="stats-grid" style={{ marginBottom: '20px' }}>
          <div className="stat-card">
            <div className="stat-value">{selectedDay.photo_count}</div>
            <div className="stat-label">照片数量</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{selectedDay.species_count}</div>
            <div className="stat-label">物种数量</div>
          </div>
        </div>

        {selectedDay.species_list.length > 0 ? (
          <>
            <h4 style={{ marginBottom: '12px' }}>观测物种</h4>
            <div className="species-list">
              {selectedDay.species_list.map((species, i) => (
                <span key={i} className="species-tag">{species}</span>
              ))}
            </div>
          </>
        ) : (
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '30px' }}>
            暂无物种记录
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="container">
      <div className="card mb-3">
        <div className="flex-between">
          <h2 className="card-title" style={{ margin: 0 }}>观鸟日历</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className={`btn ${viewMode === 'year' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setViewMode('year')}
            >
              年视图
            </button>
            <button
              className={`btn ${viewMode === 'month' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setViewMode('month')}
            >
              月视图
            </button>
            <button
              className="btn btn-outline"
              onClick={goToToday}
            >
              今天
            </button>
          </div>
        </div>
      </div>

      {loading && (
        <div className="card">
          <p style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            加载中...
          </p>
        </div>
      )}

      {!loading && (
        <>
          {viewMode === 'year' && renderYearView()}
          {viewMode === 'month' && renderMonthView()}
          {viewMode === 'day' && renderDayView()}
        </>
      )}
    </div>
  )
}
