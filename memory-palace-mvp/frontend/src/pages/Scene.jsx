import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Scene() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentScene, setCurrentScene] = useState(0)
  const [lang, setLang] = useState('zh')
  const [cardCollapsed, setCardCollapsed] = useState(false)
  const [expandedPara, setExpandedPara] = useState(null)
  const contentRef = useRef(null)

  useEffect(() => {
    const historyIndex = localStorage.getItem('currentHistoryIndex')
    const storedHistories = localStorage.getItem('sceneHistories')
    
    if (storedHistories && historyIndex !== null) {
      try {
        const histories = JSON.parse(storedHistories)
        const index = parseInt(historyIndex)
        if (histories[index]) {
          setData(histories[index])
        } else {
          navigate('/')
        }
      } catch (e) {
        navigate('/')
      }
    } else {
      navigate('/')
    }
    setLoading(false)
  }, [navigate])

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!data?.scenes?.length) return
      if (e.key === 'ArrowLeft') setCurrentScene(s => Math.max(0, s - 1))
      if (e.key === 'ArrowRight') setCurrentScene(s => Math.min((data?.scenes?.length || 1) - 1, s + 1))
      if (e.key === 'l' || e.key === 'L') setLang(l => l === 'zh' ? 'en' : 'zh')
      if (e.key === 'Escape') setCardCollapsed(c => !c)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [data])

  // 切换场景时重置展开状态
  useEffect(() => {
    setExpandedPara(null)
  }, [currentScene])

  const prevScene = () => setCurrentScene(s => Math.max(0, s - 1))
  const nextScene = () => setCurrentScene(s => Math.min((data?.scenes?.length || 1) - 1, s + 1))
  const toggleLang = () => setLang(l => l === 'zh' ? 'en' : 'zh')

  // 处理段落点击
  const handleParaClick = (idx) => {
    setExpandedPara(expandedPara === idx ? null : idx)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
            <i className="fa fa-spinner fa-spin text-3xl text-emerald-400"></i>
          </div>
          <p className="text-sage">加载中...</p>
        </div>
      </div>
    )
  }

  const scenes = data?.scenes || []
  const scene = scenes[currentScene]
  const translationParagraphs = scene?.zh?.translationParagraphs || []

  // 解析内容为段落数组
  const parseContent = (html) => {
    if (!html) return []
    const matches = html.match(/<p[^>]*>([\s\S]*?)<\/p>/gi) || []
    return matches.map(p => p.replace(/<\/?p[^>]*>/gi, ''))
  }

  const contentParagraphs = parseContent(scene?.[lang]?.content || '')

  return (
    <div className="min-h-screen relative">
      {/* 背景图 */}
      {scene?.bgImage && (
        <div 
          className="fixed inset-0 bg-cover bg-center z-0"
          style={{ backgroundImage: `url(${scene.bgImage})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/50"></div>
        </div>
      )}

      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="scene-header px-4 py-3 flex items-center justify-between">
            <button onClick={() => navigate('/create')} className="icon-btn-back">
              <i className="fa fa-arrow-left"></i>
            </button>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🌿</span>
              <span className="text-gray-800 font-bold">记了么</span>
              {data?.name && <span className="scene-tag ml-2">{data.name}</span>}
            </div>
            <button onClick={() => navigate('/')} className="icon-btn">
              <i className="fa fa-home"></i>
            </button>
          </div>
        </div>
      </header>

      {/* 展开按钮（卡片收起时显示） */}
      {cardCollapsed && (
        <div 
          className="fixed top-20 left-1/2 -translate-x-1/2 z-50 cursor-pointer"
          onClick={() => setCardCollapsed(false)}
        >
          <div className="w-10 h-6 bg-white/80 rounded-b-xl flex items-center justify-center shadow-lg hover:bg-white transition-colors">
            <i className="fa fa-chevron-down text-gray-600"></i>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="relative z-10 px-4 py-4 pb-32">
        {scenes.length === 0 ? (
          <div className="max-w-md mx-auto mt-20">
            <div className="content-card p-8 text-center">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-yellow-100 flex items-center justify-center">
                <i className="fa fa-exclamation-circle text-3xl text-yellow-500"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">暂无场景</h3>
              <p className="text-gray-600 mb-6">请返回创建新的词库</p>
              <button onClick={() => navigate('/create')} className="btn-primary w-full">
                <i className="fa fa-plus mr-2"></i>创建词库
              </button>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            {/* 场景信息卡片 */}
            <div 
              className={`content-card p-6 mb-4 transition-all duration-300 ${
                cardCollapsed ? 'opacity-0 -translate-y-full pointer-events-none' : 'opacity-100 translate-y-0'
              }`}
            >
              {/* 标题栏 */}
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center">
                  <i className={`fa ${scene?.icon || 'fa-book'} text-emerald-600`}></i>
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-800">{scene?.[lang]?.title || '场景'}</h2>
                  <p className="text-gray-500 text-sm">{scene?.[lang]?.anchors}</p>
                </div>
                <div className="text-gray-500 text-sm">{currentScene + 1} / {scenes.length}</div>
                <button 
                  onClick={() => setCardCollapsed(true)} 
                  className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 transition-colors"
                >
                  <i className="fa fa-chevron-up text-sm"></i>
                </button>
              </div>

              {/* 快捷键提示 */}
              <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
                <i className="fa fa-keyboard-o"></i>
                <span>按 ← → 翻页，按 L 切换语言，点击段落查看翻译</span>
              </div>

              {/* 内容 - 支持段落点击展开翻译 */}
              <div ref={contentRef} className="scene-content">
                {contentParagraphs.map((para, idx) => (
                  <div 
                    key={idx} 
                    className={`para-wrapper ${expandedPara === idx ? 'expanded' : ''}`}
                    onClick={() => handleParaClick(idx)}
                  >
                    <p 
                      className="mb-3 text-gray-700 leading-relaxed cursor-pointer"
                      dangerouslySetInnerHTML={{ __html: para }}
                    />
                    {/* 翻译展开区域 */}
                    <div className={`para-trans ${expandedPara === idx ? 'expanded' : ''}`}>
                      {/* 中文模式：显示英文对照 + 中文翻译 */}
                      {lang === 'zh' && (
                        <>
                          {parseContent(scene?.en?.content || '')[idx] && (
                            <div className="trans-en mb-2">
                              <span className="trans-label">EN:</span>
                              <span dangerouslySetInnerHTML={{ __html: parseContent(scene.en.content)[idx] }} />
                            </div>
                          )}
                          {translationParagraphs[idx] && (
                            <div className="trans-cn">
                              <span className="trans-label">译:</span>
                              <span dangerouslySetInnerHTML={{ __html: translationParagraphs[idx] }} />
                            </div>
                          )}
                        </>
                      )}
                      {/* 英文模式：显示中文翻译 */}
                      {lang === 'en' && translationParagraphs[idx] && (
                        <div className="trans-cn">
                          <span className="trans-label">中:</span>
                          <span dangerouslySetInnerHTML={{ __html: translationParagraphs[idx] }} />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 场景导航 */}
            {scenes.length > 1 && (
              <div className={`content-card p-4 flex items-center justify-between transition-all duration-300 ${
                cardCollapsed ? 'opacity-0 -translate-y-full pointer-events-none' : 'opacity-100 translate-y-0'
              }`}>
                <button onClick={prevScene} disabled={currentScene === 0} className="nav-btn disabled:opacity-30">
                  <i className="fa fa-chevron-left"></i>
                </button>
                <div className="flex items-center gap-2 flex-wrap justify-center max-w-md">
                  {scenes.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentScene(idx)}
                      className={`w-2 h-2 rounded-full transition-all ${
                        idx === currentScene ? 'w-6 bg-emerald-500' : 'bg-gray-300 hover:bg-gray-400'
                      }`}
                    />
                  ))}
                </div>
                <button onClick={nextScene} disabled={currentScene === scenes.length - 1} className="nav-btn disabled:opacity-30">
                  <i className="fa fa-chevron-right"></i>
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* 底部操作栏 */}
      {scenes.length > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
          <div className="content-card px-6 py-3 flex items-center gap-4">
            <button 
              onClick={toggleLang} 
              className="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-lg hover:scale-110 transition-transform"
            >
              <span className="text-sm font-bold">{lang === 'zh' ? 'EN' : '中'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
