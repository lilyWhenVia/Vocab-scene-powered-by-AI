import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { wordListApi } from '../api'

export default function Dashboard({ user, setUser }) {
  const [wordLists, setWordLists] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    wordListApi.getAll()
      .then(res => setWordLists(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
    navigate('/login')
  }

  return (
    <div className="min-h-screen relative">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-yellow-500/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-4">
        <div className="max-w-6xl mx-auto">
          <div className="glass-card px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🌿</span>
              <h1 className="text-lg font-bold text-cream">词境</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="pill-tag-dark text-sm">
                <i className="fa fa-user mr-2"></i>{user.email}
              </span>
              <button onClick={handleLogout} className="icon-btn">
                <i className="fa fa-sign-out"></i>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-6xl mx-auto px-4 py-8 relative z-10">
        {/* 欢迎区域 */}
        <div className="glass-card p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-cream mb-2">探索你的词境</h2>
              <p className="text-sage">点击词库开始沉浸式学习之旅</p>
            </div>
            <button
              onClick={() => navigate('/create')}
              className="btn-primary flex items-center gap-2"
            >
              <i className="fa fa-plus"></i>
              <span>创建词库</span>
            </button>
          </div>
        </div>

        {/* 词库列表 */}
        {loading ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <i className="fa fa-spinner fa-spin text-2xl text-emerald-400"></i>
            </div>
            <p className="text-sage">加载中...</p>
          </div>
        ) : wordLists.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-emerald-500/20 to-green-600/20 flex items-center justify-center">
              <span className="text-4xl animate-float">🌱</span>
            </div>
            <h3 className="text-xl font-bold text-cream mb-2">开始你的词境之旅</h3>
            <p className="text-sage mb-6">创建第一个词库，让 AI 为你构建专属场景</p>
            <button
              onClick={() => navigate('/create')}
              className="btn-primary"
            >
              <i className="fa fa-magic mr-2"></i>创建第一个词库
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {wordLists.map(wl => (
              <div
                key={wl.id}
                className="glass-card p-6 cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl group"
                onClick={() => navigate(`/scene/${wl.id}`)}
              >
                {/* 卡片头部 */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-green-600/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <i className="fa fa-book text-emerald-400"></i>
                  </div>
                  <span className="pill-tag text-xs">
                    {wl.word_count} 词
                  </span>
                </div>

                {/* 卡片内容 */}
                <h3 className="text-lg font-bold text-cream mb-2 truncate">{wl.name}</h3>
                
                <div className="flex items-center gap-4 text-sm text-sage">
                  <span className="flex items-center gap-1">
                    <i className="fa fa-image"></i>
                    {wl.scene_count} 场景
                  </span>
                  <span className="flex items-center gap-1">
                    <i className="fa fa-clock-o"></i>
                    {new Date(wl.created_at).toLocaleDateString()}
                  </span>
                </div>

                {/* 进入按钮 */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-sage/60">点击进入</span>
                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center group-hover:bg-emerald-500 transition-colors">
                      <i className="fa fa-arrow-right text-emerald-400 group-hover:text-white text-sm"></i>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
