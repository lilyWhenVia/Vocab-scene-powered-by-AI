import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { trackApi } from '../api'

export default function Login() {
  const navigate = useNavigate()
  const [histories, setHistories] = useState([])

  useEffect(() => {
    // 从 localStorage 读取历史词库
    const stored = localStorage.getItem('sceneHistories')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setHistories(parsed)
      } catch (e) {
        console.error('Failed to parse histories:', e)
      }
    }
  }, [])

  const handleStart = () => {
    trackApi.track('start_click')
    navigate('/create')
  }

  const handleViewHistory = (index) => {
    localStorage.setItem('currentHistoryIndex', index.toString())
    navigate('/scene/view')
  }

  const handleDeleteHistory = (index, e) => {
    e.stopPropagation()
    const newHistories = histories.filter((_, i) => i !== index)
    setHistories(newHistories)
    localStorage.setItem('sceneHistories', JSON.stringify(newHistories))
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-32 h-32 bg-emerald-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-40 h-40 bg-yellow-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-green-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="glass-card p-8 w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-6">
          <div className="w-20 h-20 mx-auto mb-3 rounded-full bg-gradient-to-br from-emerald-400 to-green-600 flex items-center justify-center shadow-lg">
            <span className="text-3xl">🌿</span>
          </div>
          <h1 className="text-3xl font-bold text-cream">记了么</h1>
          <p className="text-sage mt-2">AI 自动生成沉浸式记忆场景</p>
        </div>

        {/* 历史词库列表 */}
        {histories.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm text-sage mb-3 flex items-center gap-2">
              <i className="fa fa-history"></i>
              历史词库
            </h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {histories.map((item, index) => (
                <div
                  key={index}
                  onClick={() => handleViewHistory(index)}
                  className="glass-card-dark p-3 cursor-pointer hover:bg-white/10 transition-colors flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                      <i className="fa fa-book text-emerald-400 text-sm"></i>
                    </div>
                    <div>
                      <div className="text-cream text-sm">{item.name}</div>
                      <div className="text-sage/60 text-xs">
                        {item.scenes?.length || 0} 个场景 · {new Date(item.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteHistory(index, e)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-300 p-1"
                  >
                    <i className="fa fa-trash text-sm"></i>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 开始按钮 */}
        <button
          onClick={handleStart}
          className="btn-primary w-full py-4 text-lg flex items-center justify-center gap-3"
        >
          <i className="fa fa-plus"></i>
          <span>创建新词库</span>
        </button>

        {/* 底部装饰 */}
        <div className="mt-4 text-center">
          <p className="text-sage/60 text-xs">
            🌿 在场景中记忆，让单词自然生长
          </p>
        </div>
      </div>
    </div>
  )
}
