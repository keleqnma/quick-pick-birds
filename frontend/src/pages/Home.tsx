import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { checkLLMConfigured } from '../api/api'

// 小鸟 Logo SVG 组件
function BirdLogo() {
  return (
    <svg viewBox="0 0 200 200" width="140" height="140" style={{ margin: '0 auto 20px' }}>
      <defs>
        {/* 身体渐变 */}
        <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#5BA3D0">
            <animate attributeName="stop-color" values="#5BA3D0;#6FB8D6;#5BA3D0" dur="3s" repeatCount="indefinite" />
          </stop>
          <stop offset="100%" stopColor="#3B7A9E">
            <animate attributeName="stop-color" values="#3B7A9E;#4A90D9;#3B7A9E" dur="3s" repeatCount="indefinite" />
          </stop>
        </linearGradient>
        {/* 头部渐变 */}
        <linearGradient id="headGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#6FB8D6" />
          <stop offset="100%" stopColor="#4A90D9" />
        </linearGradient>
        {/* 翅膀渐变 */}
        <linearGradient id="wingGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#4A90D9" />
          <stop offset="100%" stopColor="#357ABD" />
        </linearGradient>
      </defs>

      {/* 尾巴 */}
      <path d="M 50 110 L 20 100 L 25 115 L 15 110 L 50 115 Z" fill="#4A90D9" />

      {/* 身体 */}
      <ellipse cx="100" cy="110" rx="50" ry="40" fill="url(#bodyGradient)" />

      {/* 翅膀 - 添加动画 */}
      <path d="M 70 105 Q 100 95 120 110 Q 100 125 70 115 Z" fill="url(#wingGradient)">
        <animate attributeName="d" values="M 70 105 Q 100 95 120 110 Q 100 125 70 115 Z;M 65 100 Q 95 85 125 105 Q 95 130 65 110 Z;M 70 105 Q 100 95 120 110 Q 100 125 70 115 Z" dur="2s" repeatCount="indefinite" />
      </path>

      {/* 头部 */}
      <circle cx="130" cy="85" r="28" fill="url(#headGradient)" />

      {/* 眼睛 - 添加眨眼动画 */}
      <g>
        <circle cx="138" cy="78" r="8" fill="white" />
        <circle cx="140" cy="78" r="4" fill="#333" />
        <circle cx="142" cy="76" r="1.5" fill="white" />
        <animate attributeName="opacity" values="1;1;0;1" dur="4s" repeatCount="indefinite" keyTimes="0;0.9;0.95;1" />
      </g>

      {/* 鸟喙 */}
      <path d="M 155 85 L 175 90 L 155 95 Z" fill="#FFA500">
        <animate attributeName="d" values="M 155 85 L 175 90 L 155 95 Z;M 155 87 L 172 90 L 155 93 Z;M 155 85 L 175 90 L 155 95 Z" dur="3s" repeatCount="indefinite" />
      </path>

      {/* 脚 */}
      <path d="M 90 145 L 85 160 M 100 145 L 100 160 M 110 145 L 115 160" stroke="#FFA500" strokeWidth="3" fill="none" />

      {/* 音符装饰 - 表示鸟在唱歌 */}
      <g opacity="0.6">
        <ellipse cx="165" cy="65" rx="8" ry="12" fill="#FFD700">
          <animate attributeName="cy" values="65;55" dur="1.5s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.6;0" dur="1.5s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="175" cy="55" rx="6" ry="10" fill="#FFD700">
          <animate attributeName="cy" values="55;45" dur="1.5s" begin="0.3s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.6;0" dur="1.5s" begin="0.3s" repeatCount="indefinite" />
        </ellipse>
      </g>
    </svg>
  )
}

export default function Home() {
  const navigate = useNavigate()
  const [showConfigReminder, setShowConfigReminder] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'scan' | 'scoring' | 'birds'>('overview')

  useEffect(() => {
    const { configured } = checkLLMConfigured()
    if (!configured) {
      setShowConfigReminder(true)
    }
  }, [])

  return (
    <div className="container">
      {/* Logo 和标题 */}
      <div style={{ textAlign: 'center', padding: '20px 0' }}>
        <BirdLogo />
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px', color: 'var(--primary)' }}>
          Quick Pick Birds
        </h1>
        <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto' }}>
          观鸟照片识别工具 — 扫描 RAW 照片，识别鸟类，记录观测地点
        </p>
      </div>

      {/* LLM 配置提示 */}
      {showConfigReminder && (
        <div style={{
          margin: '20px 0',
          padding: '16px',
          background: '#fff7ed',
          borderRadius: '12px',
          border: '1px solid #ffedd5',
          color: '#9a3412',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <strong style={{ fontSize: '1rem' }}>⚠️ 欢迎使用 Quick Pick Birds</strong>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.9rem' }}>
              首次使用请先配置大模型 API，以便进行鸟类识别和照片评分功能
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => navigate('/settings')}
            style={{ marginLeft: '16px', whiteSpace: 'nowrap' }}
          >
            去配置
          </button>
        </div>
      )}

      {/* 主导航按钮 */}
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '30px' }}>
        <button
          className={`btn ${activeTab === 'overview' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('overview')}
        >
          🏠 概览
        </button>
        <button
          className={`btn ${activeTab === 'scan' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('scan')}
        >
          📁 扫描
        </button>
        <button
          className={`btn ${activeTab === 'scoring' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('scoring')}
        >
          ⭐ 筛图
        </button>
        <button
          className={`btn ${activeTab === 'birds' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('birds')}
        >
          🐦 鸟类识别
        </button>
      </div>

      {/* 概览 Tab */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          <div className="card" style={{ cursor: 'pointer' }} onClick={() => setActiveTab('scan')}>
            <div style={{ fontSize: '3rem', marginBottom: '10px' }}>📁</div>
            <h3 className="card-title">文件夹扫描</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              支持扫描本地文件夹中的 RAW 照片（CR2、CR3、NEF、ARW 等格式），
              自动提取 EXIF 信息包括拍摄时间、GPS 坐标、相机参数等。
            </p>
          </div>

          <div className="card" style={{ cursor: 'pointer' }} onClick={() => setActiveTab('birds')}>
            <div style={{ fontSize: '3rem', marginBottom: '10px' }}>🐦</div>
            <h3 className="card-title">鸟类识别</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              使用 AI 模型识别照片中的鸟类品种，支持连拍分组分析，
              自动筛选最佳照片，识别多种常见鸟类。
            </p>
          </div>

          <div className="card" style={{ cursor: 'pointer' }} onClick={() => setActiveTab('scoring')}>
            <div style={{ fontSize: '3rem', marginBottom: '10px' }}>⭐</div>
            <h3 className="card-title">智能筛图</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              使用大模型评估照片质量，从对焦、清晰度、构图三个维度进行评分，
              自动推荐最佳照片。
            </p>
          </div>
        </div>
      )}

      {/* 扫描 Tab */}
      {activeTab === 'scan' && (
        <div className="card">
          <h3 className="card-title">📁 扫描照片文件夹</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
            扫描文件夹中的照片，提取 EXIF 信息和 GPS 坐标
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Link to="/scan" className="btn btn-primary" style={{ flex: 1, textAlign: 'center' }}>
              进入扫描页面
            </Link>
            <button className="btn btn-outline" onClick={() => setActiveTab('overview')}>
              返回概览
            </button>
          </div>
        </div>
      )}

      {/* 筛图 Tab */}
      {activeTab === 'scoring' && (
        <div className="card">
          <h3 className="card-title">⭐ 智能筛图</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
            使用大模型评估照片质量，从对焦、清晰度、构图三个维度进行评分
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Link to="/scoring" className="btn btn-primary" style={{ flex: 1, textAlign: 'center' }}>
              进入筛图页面
            </Link>
            <button className="btn btn-outline" onClick={() => setActiveTab('overview')}>
              返回概览
            </button>
          </div>
        </div>
      )}

      {/* 鸟类识别 Tab */}
      {activeTab === 'birds' && (
        <div className="card">
          <h3 className="card-title">🐦 鸟类识别</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
            识别照片中的鸟类品种，支持连拍分组分析
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Link to="/scan" className="btn btn-primary" style={{ flex: 1, textAlign: 'center' }}>
              进入扫描页面
            </Link>
            <button className="btn btn-outline" onClick={() => setActiveTab('overview')}>
              返回概览
            </button>
          </div>
        </div>
      )}

      {/* 功能链接卡片 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '30px' }}>
        <Link to="/map" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>🗺️</div>
          <h4 style={{ margin: '0 0 8px 0' }}>观鸟地图</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
            查看观测地点分布
          </p>
        </Link>
        <Link to="/calendar" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>📅</div>
          <h4 style={{ margin: '0 0 8px 0' }}>观鸟日历</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
            按日期浏览照片
          </p>
        </Link>
        <Link to="/summary" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>📊</div>
          <h4 style={{ margin: '0 0 8px 0' }}>观鸟小结</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
            生成观测统计报告
          </p>
        </Link>
        <Link to="/settings" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>⚙️</div>
          <h4 style={{ margin: '0 0 8px 0' }}>设置</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
            配置 API 和偏好
          </p>
        </Link>
      </div>
    </div>
  )
}
