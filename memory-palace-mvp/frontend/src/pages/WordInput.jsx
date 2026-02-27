import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function WordInput() {
  const [name, setName] = useState('')
  const [wordsText, setWordsText] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [fileName, setFileName] = useState('')
  const [remainingWords, setRemainingWords] = useState(null)
  const [parsedWords, setParsedWords] = useState([])
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)
  const dropZoneRef = useRef(null)
  const navigate = useNavigate()

  // 检查是否有剩余单词待生成
  useEffect(() => {
    const stored = localStorage.getItem('remainingWords')
    if (stored) {
      try {
        setRemainingWords(JSON.parse(stored))
      } catch (e) {
        console.error('Failed to parse remaining words:', e)
      }
    }
  }, [])

  // 实时解析单词
  useEffect(() => {
    const words = parseWords(wordsText)
    setParsedWords(words)
  }, [wordsText])

  const generateRandomName = () => {
    const adjectives = ['晨光', '星辰', '月影', '云端', '海风', '山林', '花语', '雨露']
    const nouns = ['词库', '记忆', '宝典', '手册', '笔记', '集锦']
    const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
    const noun = nouns[Math.floor(Math.random() * nouns.length)]
    const num = Math.floor(Math.random() * 1000)
    return `${adj}${noun}${num}`
  }

  const parseWords = (text) => {
    if (!text || !text.trim()) return []
    
    const lines = text.split(/[\n\r]+/).map(w => w.trim()).filter(w => w.length > 0)
    const words = []
    
    for (const line of lines) {
      // 跳过标题行
      if (/^(Word|Meaning|共|扫描|全部|复习)/.test(line)) continue
      if (/^\d+\/\d+/.test(line)) continue
      
      // 格式1: "1 ubiquitous 无处不在的" 或 "1. ubiquitous"
      const numberedMatch = line.match(/^\d+[\.\s]+([a-zA-Z\-']+)(?:\s+(.*))?$/)
      if (numberedMatch) {
        words.push({ word: numberedMatch[1].trim(), pos: '', meaning: numberedMatch[2]?.trim() || '' })
        continue
      }
      
      // 格式2: "ubiquitous (adj.) 无处不在的" 或 "ubiquitous: adj. 无处不在的"
      const match = line.match(/^([a-zA-Z\-']+)\s*(?:\(([a-z]+\.?)\)|[:：]\s*([a-z]+\.?))?\s*(.*)$/i)
      if (match && match[1].length > 1) {
        const pos = match[2] || match[3] || ''
        words.push({ word: match[1].trim(), pos: pos.trim(), meaning: match[4]?.trim() || '' })
        continue
      }
      
      // 格式3: 逗号/分号分隔的单词列表
      const parts = line.split(/[,;，；\t]+/).map(p => p.trim()).filter(p => p)
      for (const part of parts) {
        // 提取单词和可能的释义
        const wordMatch = part.match(/^([a-zA-Z\-']+)(?:\s*\(([^)]+)\))?(?:\s+(.*))?$/)
        if (wordMatch && wordMatch[1].length > 1) {
          words.push({ 
            word: wordMatch[1], 
            pos: wordMatch[2]?.trim() || '', 
            meaning: wordMatch[3]?.trim() || '' 
          })
        }
      }
    }
    
    // 去重
    const seen = new Set()
    return words.filter(w => {
      const key = w.word.toLowerCase()
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }

  // 处理文件（支持上传和拖拽）
  const processFile = async (file) => {
    if (!file) return
    
    const validTypes = ['.pdf', '.doc', '.docx', '.txt']
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!validTypes.includes(ext)) {
      setStatus('✗ 不支持的文件格式，请上传 PDF、Word 或 TXT 文件')
      return
    }

    setFileName(file.name)
    setName(file.name.replace(/\.(pdf|doc|docx|txt)$/i, ''))

    // TXT 文件直接在前端读取
    if (ext === '.txt') {
      setStatus('正在读取文件...')
      try {
        const text = await file.text()
        setWordsText(text)
        setStatus('✓ 文件读取成功')
      } catch (err) {
        setStatus(`✗ 文件读取失败: ${err.message}`)
      }
      return
    }

    // PDF/Word 发送到后端解析
    const formData = new FormData()
    formData.append('file', file)

    setStatus('正在解析文件...')
    try {
      const res = await fetch('/api/parse-file', { method: 'POST', body: formData })
      if (!res.ok) throw new Error((await res.json()).detail || '文件解析失败')
      const data = await res.json()
      setWordsText(data.text)
      setStatus('✓ 文件解析成功')
    } catch (err) {
      setStatus(`✗ ${err.message}`)
    }
  }

  const handleFileUpload = (e) => {
    processFile(e.target.files[0])
  }

  // 拖拽处理
  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.target === dropZoneRef.current) {
      setIsDragging(false)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      processFile(files[0])
    }
  }

  const saveToHistory = (sceneData) => {
    let histories = []
    try {
      histories = JSON.parse(localStorage.getItem('sceneHistories') || '[]')
    } catch (e) {}
    histories.unshift(sceneData)
    if (histories.length > 10) histories = histories.slice(0, 10)
    localStorage.setItem('sceneHistories', JSON.stringify(histories))
    localStorage.setItem('currentHistoryIndex', '0')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (parsedWords.length === 0) {
      setStatus('请输入至少一个单词')
      return
    }

    const finalName = name.trim() || generateRandomName()
    setLoading(true)
    setStatus(parsedWords.length > 200 ? `正在生成前 200 个单词的场景...（共 ${parsedWords.length} 词）` : '正在生成记忆场景...')

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: finalName, words: parsedWords })
      })
      if (!res.ok) throw new Error('生成失败')
      
      const data = await res.json()
      setStatus(data.message)
      
      saveToHistory({ name: finalName, scenes: data.scenes, createdAt: new Date().toISOString() })
      
      if (data.remaining_words?.length > 0) {
        localStorage.setItem('remainingWords', JSON.stringify({ words: data.remaining_words, originalName: finalName }))
      } else {
        localStorage.removeItem('remainingWords')
      }
      
      setTimeout(() => navigate('/scene/view'), 1000)
    } catch (err) {
      setStatus('✗ 服务出现了问题，请稍后再试')
      setLoading(false)
    }
  }

  const handleGenerateRemaining = async () => {
    if (!remainingWords) return
    setLoading(true)
    setStatus(`正在生成剩余 ${remainingWords.words.length} 个单词的场景...`)
    
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `${remainingWords.originalName}（续）`, words: remainingWords.words })
      })
      if (!res.ok) throw new Error('生成失败')
      
      const data = await res.json()
      saveToHistory({ name: `${remainingWords.originalName}（续）`, scenes: data.scenes, createdAt: new Date().toISOString() })
      
      if (data.remaining_words?.length > 0) {
        const newRemaining = { words: data.remaining_words, originalName: remainingWords.originalName }
        localStorage.setItem('remainingWords', JSON.stringify(newRemaining))
        setRemainingWords(newRemaining)
      } else {
        localStorage.removeItem('remainingWords')
        setRemainingWords(null)
      }
      
      navigate('/scene/view')
    } catch (err) {
      setStatus('✗ 服务出现了问题，请稍后再试')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative pb-24">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-20 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-40 left-10 w-48 h-48 bg-yellow-500/5 rounded-full blur-3xl"></div>
      </div>

      <header className="sticky top-0 z-40 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          <div className="glass-card px-6 py-4 flex items-center gap-4">
            <button onClick={() => navigate('/')} className="icon-btn-back">
              <i className="fa fa-arrow-left"></i>
            </button>
            <h1 className="text-lg font-bold text-cream">创建词库</h1>
            <div className="ml-auto">
              <span className="text-2xl">🌿</span>
              <span className="text-cream font-bold ml-2">记了么</span>
            </div>
          </div>
        </div>
      </header>

      {remainingWords && (
        <div className="max-w-2xl mx-auto px-4 py-2">
          <div className="glass-card p-4 border-yellow-500/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                  <i className="fa fa-clock-o text-yellow-400"></i>
                </div>
                <div>
                  <div className="text-cream">有 {remainingWords.words.length} 个单词待生成</div>
                  <div className="text-sage/60 text-sm">来自「{remainingWords.originalName}」</div>
                </div>
              </div>
              <button onClick={handleGenerateRemaining} disabled={loading} className="btn-primary px-4 py-2 text-sm">
                继续生成
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-2xl mx-auto px-4 py-6 relative z-10">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="glass-card p-6">
            <label className="block text-sm font-medium text-cream mb-3">
              <i className="fa fa-tag mr-2 text-emerald-400"></i>词库名称
              <span className="text-sage/60 font-normal ml-2">留空自动生成</span>
            </label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} className="input-glass" placeholder="例如：GRE核心词汇" />
          </div>

          <div className="glass-card p-6">
            <label className="block text-sm font-medium text-cream mb-3">
              <i className="fa fa-cloud-upload mr-2 text-emerald-400"></i>上传文件
            </label>
            <input ref={fileInputRef} type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleFileUpload} className="hidden" />
            <div
              ref={dropZoneRef}
              onClick={() => fileInputRef.current?.click()}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className={`w-full py-8 rounded-2xl border-2 border-dashed transition-colors flex flex-col items-center gap-3 cursor-pointer
                ${isDragging ? 'border-emerald-500 bg-emerald-500/10' : 'border-white/20 hover:border-emerald-500/50'}`}
            >
              <div className={`w-14 h-14 rounded-full flex items-center justify-center transition-colors
                ${isDragging ? 'bg-emerald-500/30' : 'bg-emerald-500/20'}`}>
                <i className={`fa text-2xl text-emerald-400 ${isDragging ? 'fa-download' : 'fa-file-text-o'}`}></i>
              </div>
              {fileName ? (
                <span className="text-cream">{fileName}</span>
              ) : isDragging ? (
                <span className="text-emerald-400">松开鼠标上传文件</span>
              ) : (
                <>
                  <span className="text-cream">点击或拖拽文件到此处</span>
                  <span className="text-sage/60 text-sm">支持 PDF、Word、TXT</span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 px-4">
            <div className="flex-1 h-px bg-white/10"></div>
            <span className="text-sage/60 text-sm">或直接粘贴</span>
            <div className="flex-1 h-px bg-white/10"></div>
          </div>

          <div className="glass-card p-6">
            <label className="block text-sm font-medium text-cream mb-3">
              <i className="fa fa-pencil mr-2 text-emerald-400"></i>单词列表
              <span className="text-sage/60 font-normal ml-2">支持任意分隔符</span>
            </label>
            <textarea value={wordsText} onChange={(e) => setWordsText(e.target.value)} className="input-glass min-h-[200px] font-mono text-sm resize-none" placeholder={`直接粘贴单词，支持多种格式：\n\nflap, ranger, counsellor, ultimate\n或\nflap: v. 拍打翅膀\nranger: n. 护林员`} />
            <div className="mt-4 flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <i className="fa fa-check text-emerald-400 text-sm"></i>
              </div>
              <span className="text-sage">
                已识别 <span className="text-emerald-400 font-bold">{parsedWords.length}</span> 个单词
                {parsedWords.length > 200 && <span className="text-yellow-400 ml-2">（将分批生成，每次最多 200 词）</span>}
              </span>
            </div>
            
            {/* 显示识别的单词预览 */}
            {parsedWords.length > 0 && (
              <div className="mt-4 p-3 rounded-xl bg-black/20 max-h-32 overflow-y-auto">
                <div className="flex flex-wrap gap-2">
                  {parsedWords.slice(0, 50).map((w, i) => (
                    <span key={i} className="px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs">
                      {w.word}
                      {w.meaning && <span className="text-sage/60 ml-1">({w.meaning.slice(0, 10)})</span>}
                    </span>
                  ))}
                  {parsedWords.length > 50 && (
                    <span className="px-2 py-1 text-sage/60 text-xs">...还有 {parsedWords.length - 50} 个</span>
                  )}
                </div>
              </div>
            )}
          </div>

          {status && (
            <div className={`glass-card p-4 ${status.includes('✗') ? 'border-red-500/30' : 'border-emerald-500/30'}`}>
              <div className="flex items-center gap-3">
                {loading && <i className="fa fa-spinner fa-spin text-emerald-400"></i>}
                <span className={status.includes('✗') ? 'text-red-400' : 'text-cream'}>{status}</span>
              </div>
            </div>
          )}

          <button type="submit" disabled={loading || parsedWords.length === 0} className="btn-primary w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3">
            {loading ? <><i className="fa fa-spinner fa-spin"></i><span>生成中...</span></> : <><i className="fa fa-magic"></i><span>生成记忆宫殿</span></>}
          </button>
        </form>
      </main>
    </div>
  )
}
