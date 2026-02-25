import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateApi, trackApi } from '../api'

const GUEST_WORD_LIMIT = 50

export default function Guest() {
  const [wordsText, setWordsText] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [scenes, setScenes] = useState(null)
  const [currentScene, setCurrentScene] = useState(0)
  const [lang, setLang] = useState('zh')
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const parseWords = (text) => {
    const words = text
      .split(/[\n\r,;，；\t]+/)
      .map(w => w.trim())
      .filter(w => w.length > 0)
    
    return words.map(item => {
      const match = item.match(/^([a-zA-Z\-']+)(?:\s*[:：]\s*)?(?:([a-z]+\.)\s*)?(.*)$/i)
      if (match) {
        return { word: match[1].trim(), pos: match[2]?.trim() || '', meaning: match[3]?.trim() || '' }
      }
      const wordOnly = item.match(/^([a-zA-Z\-']+)/)
      if (wordOnly) {
        return { word: wordOnly[1], pos: '', meaning: '' }
      }
      return null
    }).filter(w => w !== null)
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setStatus('正在解析文件...')
    try {
      const res = await fetch('/api/parse-file', {
        method: 'POST',
        body: formData
      })
      
      if (!res.ok) throw new Error('文件解析失败')
      
      const data = await res.json()
      setWordsText(data.text)
      setStatus('✓ 文件解析成功')
    } catch (err) {
      setStatus(`✗ ${err.message}`)
    }
  }

  const handleGenerate = async () => {
    const words = parseWords(wordsText)
    if (words.length === 0) {
      setStatus('请输入至少一个单词')
      return
    }
    if (words.length > GUEST_WORD_LIMIT) {
      setStatus(`游客模式最多 ${GUEST_WORD_LIMIT} 词，当前 ${words.length} 词。注册后可解锁无限制。`)
      return
    }

    setLoading(true)
    setStatus('正在生成场景...')
    trackApi.track('guest_generate_start', { word_count: words.length })

    try {
      const res = await generateApi.guestGenerate('游客词库', words)
      setScenes(res.data.scenes)
      setStatus('')
      trackApi.track('guest_generate_success', { scene_count: res.data.scenes.length })
    } catch (err) {
      setStatus(`✗ ${err.response?.data?.detail || err.message}`)
      trackApi.track('guest_generate_error')
    } finally {
      setLoading(false)
    }
  }

  const handleParaClick = (e) => {
    const wrapper = e.target.closest('.para-wrapper')
    if (!wrapper || e.target.closest('.tooltip')) return
    const trans = wrapper.querySelector('.para-trans')
    if (trans) {
      wrapper.classList.toggle('expanded')
      trans.classList.toggle('expanded')
    }
  }

  const wordCount = parseWords(wordsText).length
  const isOverLimit = wordCount > GUEST_WORD_LIMIT

  // 场景展示模式
  if (scenes) {
    const scene = scenes[currentScene]
    return (
      <div className="min-h-screen relative">
        {scene?.bgImage && (
          <div className="fixed inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${scene.bgImage})` }}>
            <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/50"></div>
          </div>
        )}

        {/* Header */}
        <header className="sticky top-0 z-40 px-4 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="glass-card px-4 py-3 flex items-center justify-between">
              <button onClick={() => setScenes(null)} className="icon-btn-back">
                <i className="fa fa-arrow-left"></i>
              </button>
              
              {/* 游客提示 */}
              <div className="pill-tag-dark text-xs flex items-center gap-2">
                <i className="fa fa-user-o"></i>
                <span>游客模式</span>
                <button 
                  onClick={() => navigate('/login')}
                  className="ml-2 px-2 py-0.5 bg-emerald-500/30 rounded-full text-emerald-300 hover:bg-emerald-500/50 transition"
                >
                  注册保存
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button className="icon-btn" onClick={() => setLang(l => l === 'zh' ? 'en' : 'zh')}>
                  <i className={`fa ${lang === 'zh' ? 'fa-language' : 'fa-globe'}`}></i>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* 场景内容 */}
        <main className="relative z-10 px-4 py-4 pb-32">
          <div className="max-w-3xl mx-auto">
            <div className="glass-card-dark p-6 mb-4">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/30 flex items-center justify-center">
                  <i className={`fa ${scene?.icon || 'fa-book'} text-emerald-400`}></i>
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-cream">{scene?.[lang]?.title || '场景'}</h2>
                  <p className="text-sage text-sm">{scene?.[lang]?.anchors}</p>
                </div>
              </div>

              <div className="text-xs text-sage/60 mb-4 flex items-center gap-2">
                <i className="fa fa-hand-pointer-o"></i>
                <span>点击段落查看翻译</span>
              </div>

              <div 
                className="text-cream/90 leading-relaxed"
                onClick={handleParaClick}
                dangerouslySetInnerHTML={{ __html: renderContent(scene, lang) }}
              />
            </div>

            {/* 导航 */}
            <div className="glass-card p-4 flex items-center justify-between">
              <button
                onClick={() => setCurrentScene(s => Math.max(0, s - 1))}
                disabled={currentScene === 0}
                className="icon-btn disabled:opacity-30"
              >
                <i className="fa fa-chevron-left"></i>
              </button>

              <div className="flex items-center gap-2">
                {scenes.map((_, idx) => (
                  <button
                    key={idx}
                    onClick={() => setCurrentScene(idx)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      idx === currentScene ? 'w-6 bg-emerald-500' : 'bg-white/30 hover:bg-white/50'
                    }`}
                  />
                ))}
              </div>

              <button
                onClick={() => setCurrentScene(s => Math.min(scenes.length - 1, s + 1))}
                disabled={currentScene === scenes.length - 1}
                className="icon-btn disabled:opacity-30"
              >
                <i className="fa fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  // 输入模式
  return (
    <div className="min-h-screen relative pb-24">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-20 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-40 left-10 w-48 h-48 bg-yellow-500/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          <div className="glass-card px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/login')} className="icon-btn-back">
                <i className="fa fa-arrow-left"></i>
              </button>
              <h1 className="text-lg font-bold text-cream">游客体验</h1>
            </div>
            <span className="pill-tag-dark text-xs">
              <i className="fa fa-user-o mr-1"></i>限{GUEST_WORD_LIMIT}词
            </span>
          </div>
        </div>
      </header>

      {/* 游客提示 */}
      <div className="max-w-2xl mx-auto px-4 py-4">
        <div className="glass-card p-4 flex items-center gap-3" style={{ background: 'rgba(201, 162, 39, 0.15)', borderColor: 'rgba(201, 162, 39, 0.3)' }}>
          <i className="fa fa-info-circle text-gold"></i>
          <div className="flex-1 text-sm text-cream/80">
            游客模式最多支持 {GUEST_WORD_LIMIT} 个单词，且不会保存数据。
            <button onClick={() => navigate('/login')} className="text-emerald-400 hover:underline ml-1">
              注册账号
            </button>
            解锁无限制。
          </div>
        </div>
      </div>

      {/* 输入区域 */}
      <main className="max-w-2xl mx-auto px-4 relative z-10">
        <div className="space-y-6">
          {/* 文件上传 */}
          <div className="glass-card p-6">
            <label className="block text-sm font-medium text-cream mb-3">
              <i className="fa fa-cloud-upload mr-2 text-emerald-400"></i>上传文件
            </label>
            <input ref={fileInputRef} type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleFileUpload} className="hidden" />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-full py-6 rounded-2xl border-2 border-dashed border-white/20 hover:border-emerald-500/50 transition-colors flex flex-col items-center gap-2"
            >
              <i className="fa fa-file-text-o text-xl text-emerald-400"></i>
              <span className="text-cream/80 text-sm">点击选择文件</span>
            </button>
          </div>

          {/* 分隔线 */}
          <div className="flex items-center gap-4 px-4">
            <div className="flex-1 h-px bg-white/10"></div>
            <span className="text-sage/60 text-sm">或直接粘贴</span>
            <div className="flex-1 h-px bg-white/10"></div>
          </div>

          {/* 单词输入 */}
          <div className="glass-card p-6">
            <label className="block text-sm font-medium text-cream mb-3">
              <i className="fa fa-pencil mr-2 text-emerald-400"></i>单词列表
            </label>
            <textarea
              value={wordsText}
              onChange={(e) => setWordsText(e.target.value)}
              className="input-glass min-h-[180px] font-mono text-sm resize-none"
              placeholder="粘贴单词，支持任意分隔符..."
            />
            
            <div className="mt-4 flex items-center justify-between">
              <span className={`text-sm ${isOverLimit ? 'text-red-400' : 'text-sage'}`}>
                已识别 <span className={`font-bold ${isOverLimit ? 'text-red-400' : 'text-emerald-400'}`}>{wordCount}</span> / {GUEST_WORD_LIMIT} 词
                {isOverLimit && <span className="ml-2">（超出限制）</span>}
              </span>
            </div>
          </div>

          {/* 状态 */}
          {status && (
            <div className={`glass-card p-4 ${status.includes('✗') ? 'border-red-500/30' : ''}`}>
              <div className="flex items-center gap-3">
                {loading && <i className="fa fa-spinner fa-spin text-emerald-400"></i>}
                <span className={status.includes('✗') ? 'text-red-400' : 'text-cream'}>{status}</span>
              </div>
            </div>
          )}

          {/* 生成按钮 */}
          <button
            onClick={handleGenerate}
            disabled={loading || wordCount === 0 || isOverLimit}
            className="btn-primary w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
          >
            {loading ? (
              <><i className="fa fa-spinner fa-spin"></i><span>生成中...</span></>
            ) : (
              <><i className="fa fa-magic"></i><span>生成场景</span></>
            )}
          </button>
        </div>
      </main>
    </div>
  )
}

function renderContent(scene, lang) {
  if (!scene) return ''
  const content = scene[lang]?.content || ''
  const paragraphs = content.match(/<p[^>]*>[\s\S]*?<\/p>/g) || []
  const enParagraphs = (scene.en?.content || '').match(/<p[^>]*>[\s\S]*?<\/p>/g) || []
  const cnParagraphs = scene.zh?.translationParagraphs || []
  
  return paragraphs.map((p, idx) => {
    const mainContent = p.replace(/<\/?p[^>]*>/g, '')
    const enContent = (enParagraphs[idx] || '').replace(/<\/?p[^>]*>/g, '')
    const cnContent = cnParagraphs[idx] || scene.zh?.translation || ''
    
    return `
      <div class="para-wrapper" data-para-idx="${idx}">
        <div class="para-main">${mainContent}</div>
        <div class="para-trans">
          <div class="trans-en"><span class="text-xs text-sage/60 mr-2">EN</span>${enContent}</div>
          <div class="trans-cn"><span class="text-xs text-sage/60 mr-2">CN</span>${cnContent}</div>
        </div>
      </div>
    `
  }).join('')
}
