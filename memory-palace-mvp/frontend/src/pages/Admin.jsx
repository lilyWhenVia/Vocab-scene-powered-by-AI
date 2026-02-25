import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

const PROVIDERS = [
  { id: 'openai', name: 'OpenAI', desc: 'GPT-4o / GPT-4o-mini', placeholder: 'sk-...' },
  { id: 'anthropic', name: 'Claude', desc: 'Claude 3 Haiku / Sonnet', placeholder: 'sk-ant-...' },
  { id: 'zhipu', name: '智谱 GLM', desc: 'GLM-4-Flash (免费)', placeholder: '智谱 API Key' },
  { id: 'deepseek', name: 'DeepSeek', desc: 'DeepSeek Chat (便宜)', placeholder: 'sk-...' },
  { id: 'qwen', name: '通义千问', desc: 'Qwen Turbo', placeholder: 'sk-...' },
  { id: 'minimax', name: 'MiniMax', desc: 'MiniMax-Text-01 (性价比高)', placeholder: 'MiniMax API Key' },
]

export default function Admin() {
  const [searchParams] = useSearchParams()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [config, setConfig] = useState(null)
  const [apiKeys, setApiKeys] = useState({})
  const [savingKey, setSavingKey] = useState(null)
  const navigate = useNavigate()
  
  const adminKey = searchParams.get('key') || ''

  const fetchStats = () => {
    if (!adminKey) {
      setError('需要管理员密钥')
      setLoading(false)
      return
    }

    fetch(`/api/admin/stats?key=${adminKey}`)
      .then(res => {
        if (!res.ok) throw new Error('无权访问')
        return res.json()
      })
      .then(data => {
        setStats(data)
        setConfig(data.ai_config)
        // 初始化 API Key 输入框（显示遮蔽后的值）
        const keys = {}
        PROVIDERS.forEach(p => {
          keys[p.id] = data.ai_config.api_keys_masked?.[p.id] || ''
        })
        setApiKeys(keys)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchStats()
  }, [adminKey])

  const saveConfig = async () => {
    setSaving(true)
    try {
      const res = await fetch(`/api/admin/config?key=${adminKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      if (!res.ok) throw new Error('保存失败')
      const data = await res.json()
      setConfig(data.config)
      alert('配置已保存')
    } catch (err) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  const saveApiKey = async (provider) => {
    const key = apiKeys[provider]
    // 如果是遮蔽的值（包含...），不提交
    if (key.includes('...')) {
      alert('请输入新的 API Key')
      return
    }
    
    setSavingKey(provider)
    try {
      const res = await fetch(`/api/admin/api-key?key=${adminKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: key })
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || '保存失败')
      }
      const data = await res.json()
      // 更新状态
      setStats(prev => ({
        ...prev,
        available_providers: data.available_providers
      }))
      setConfig(prev => ({
        ...prev,
        api_keys_status: data.api_keys_status
      }))
      alert(`${getProviderName(provider)} API Key 已保存`)
      fetchStats() // 刷新数据
    } catch (err) {
      alert(err.message)
    } finally {
      setSavingKey(null)
    }
  }

  const deleteApiKey = async (provider) => {
    if (!confirm(`确定要删除 ${getProviderName(provider)} 的 API Key 吗？`)) return
    
    setSavingKey(provider)
    try {
      const res = await fetch(`/api/admin/api-key?key=${adminKey}&provider=${provider}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('删除失败')
      setApiKeys(prev => ({ ...prev, [provider]: '' }))
      fetchStats()
      alert('已删除')
    } catch (err) {
      alert(err.message)
    } finally {
      setSavingKey(null)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <i className="fa fa-spinner fa-spin text-3xl text-emerald-400"></i>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass-card p-8 text-center">
          <i className="fa fa-lock text-4xl text-red-400 mb-4"></i>
          <p className="text-cream">{error}</p>
          <button onClick={() => navigate('/')} className="btn-primary mt-4">
            返回首页
          </button>
        </div>
      </div>
    )
  }

  const { analytics, ai_usage, available_providers } = stats

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="glass-card p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📊</span>
              <h1 className="text-xl font-bold text-cream">开发者仪表盘</h1>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={fetchStats} className="icon-btn">
                <i className="fa fa-refresh"></i>
              </button>
              <span className="pill-tag-dark text-xs">
                <i className="fa fa-check-circle mr-1 text-emerald-400"></i>
                {available_providers.length} 个可用
              </span>
            </div>
          </div>
        </div>

        {/* API Key 配置 */}
        <div className="glass-card p-6 mb-6" style={{ borderColor: 'rgba(201, 162, 39, 0.3)' }}>
          <h2 className="text-lg font-bold text-cream mb-4 flex items-center gap-2">
            <i className="fa fa-key text-gold"></i>
            API Key 配置
            <span className="text-xs text-sage font-normal ml-2">配置后立即生效</span>
          </h2>
          
          <div className="space-y-4">
            {PROVIDERS.map(provider => {
              const isConfigured = config?.api_keys_status?.[provider.id]
              const isAvailable = available_providers.includes(provider.id)
              
              return (
                <div key={provider.id} className="glass-card-dark p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-cream font-medium">{provider.name}</span>
                        {isAvailable ? (
                          <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-500/20 text-emerald-400">
                            <i className="fa fa-check mr-1"></i>可用
                          </span>
                        ) : isConfigured ? (
                          <span className="px-2 py-0.5 text-xs rounded-full bg-yellow-500/20 text-yellow-400">
                            <i className="fa fa-exclamation mr-1"></i>连接失败
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-xs rounded-full bg-white/10 text-sage">
                            未配置
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-sage mt-1">{provider.desc}</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={apiKeys[provider.id] || ''}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, [provider.id]: e.target.value }))}
                      onFocus={(e) => {
                        // 聚焦时清空遮蔽值
                        if (e.target.value.includes('...')) {
                          setApiKeys(prev => ({ ...prev, [provider.id]: '' }))
                        }
                      }}
                      placeholder={provider.placeholder}
                      className="input-glass flex-1 text-sm font-mono"
                    />
                    <button
                      onClick={() => saveApiKey(provider.id)}
                      disabled={savingKey === provider.id}
                      className="px-4 py-2 rounded-xl bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 transition disabled:opacity-50"
                    >
                      {savingKey === provider.id ? (
                        <i className="fa fa-spinner fa-spin"></i>
                      ) : (
                        <i className="fa fa-save"></i>
                      )}
                    </button>
                    {isConfigured && (
                      <button
                        onClick={() => deleteApiKey(provider.id)}
                        disabled={savingKey === provider.id}
                        className="px-4 py-2 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition disabled:opacity-50"
                      >
                        <i className="fa fa-trash"></i>
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* AI 生成配置 */}
        <div className="glass-card p-6 mb-6" style={{ borderColor: 'rgba(16, 185, 129, 0.3)' }}>
          <h2 className="text-lg font-bold text-cream mb-4 flex items-center gap-2">
            <i className="fa fa-cog text-emerald-400"></i>
            生成配置
          </h2>
          
          {config && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 首选提供商 */}
              <div>
                <label className="block text-sm text-sage mb-2">首选 AI 提供商</label>
                <select
                  value={config.preferred_provider}
                  onChange={(e) => setConfig({ ...config, preferred_provider: e.target.value })}
                  className="input-glass"
                >
                  <option value="auto">自动选择（优先国产）</option>
                  {available_providers.map(p => (
                    <option key={p} value={p}>{getProviderName(p)}</option>
                  ))}
                </select>
              </div>

              {/* Temperature */}
              <div>
                <label className="block text-sm text-sage mb-2">
                  创意度: {config.temperature}
                </label>
                <input
                  type="range"
                  value={config.temperature}
                  onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                  min={0}
                  max={1}
                  step={0.1}
                  className="w-full accent-emerald-500"
                />
              </div>

              {/* 保存按钮 */}
              <div className="md:col-span-2">
                <button
                  onClick={saveConfig}
                  disabled={saving}
                  className="btn-primary w-full disabled:opacity-50"
                >
                  {saving ? <i className="fa fa-spinner fa-spin mr-2"></i> : <i className="fa fa-save mr-2"></i>}
                  保存配置
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 概览卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard icon="fa-bolt" label="总事件" value={analytics.total_events} color="emerald" />
          <StatCard icon="fa-users" label="独立用户" value={analytics.unique_users} color="blue" />
          <StatCard icon="fa-user-o" label="游客操作" value={analytics.guest_actions} color="yellow" />
          <StatCard icon="fa-dollar" label="AI成本" value={`$${ai_usage.total_cost_usd}`} color="red" />
        </div>

        {/* AI 使用统计 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-cream mb-4">
              <i className="fa fa-microchip mr-2 text-emerald-400"></i>Token 使用
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-sage">输入 Tokens</span>
                <span className="text-cream font-mono">{ai_usage.total_input_tokens.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-sage">输出 Tokens</span>
                <span className="text-cream font-mono">{ai_usage.total_output_tokens.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-sage">调用次数</span>
                <span className="text-cream font-mono">{ai_usage.total_calls}</span>
              </div>
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-cream mb-4">
              <i className="fa fa-pie-chart mr-2 text-emerald-400"></i>按提供商
            </h2>
            <div className="space-y-3">
              {Object.entries(ai_usage.by_provider || {}).map(([provider, data]) => (
                <div key={provider} className="flex items-center justify-between text-sm">
                  <span className="text-cream">{getProviderName(provider)}</span>
                  <div className="text-right">
                    <span className="text-sage mr-3">{data.calls}次</span>
                    <span className="text-emerald-400">${data.cost.toFixed(4)}</span>
                  </div>
                </div>
              ))}
              {Object.keys(ai_usage.by_provider || {}).length === 0 && (
                <p className="text-sage/60 text-sm">暂无数据</p>
              )}
            </div>
          </div>
        </div>

        {/* 最近调用 */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-bold text-cream mb-4">
            <i className="fa fa-history mr-2 text-emerald-400"></i>最近 AI 调用
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-sage border-b border-white/10">
                  <th className="text-left py-2">提供商</th>
                  <th className="text-left py-2">模型</th>
                  <th className="text-right py-2">输入</th>
                  <th className="text-right py-2">输出</th>
                  <th className="text-right py-2">成本</th>
                </tr>
              </thead>
              <tbody>
                {(ai_usage.recent || []).slice(-10).reverse().map((r, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-2 text-cream">{getProviderName(r.provider)}</td>
                    <td className="py-2 text-sage font-mono text-xs">{r.model}</td>
                    <td className="py-2 text-right text-cream">{r.input}</td>
                    <td className="py-2 text-right text-cream">{r.output}</td>
                    <td className="py-2 text-right text-emerald-400">${r.cost.toFixed(6)}</td>
                  </tr>
                ))}
                {(ai_usage.recent || []).length === 0 && (
                  <tr><td colSpan={5} className="py-4 text-center text-sage/60">暂无数据</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

function getProviderName(provider) {
  const names = {
    openai: 'OpenAI',
    anthropic: 'Claude',
    zhipu: '智谱 GLM',
    deepseek: 'DeepSeek',
    qwen: '通义千问',
    minimax: 'MiniMax',
    auto: '自动选择'
  }
  return names[provider] || provider
}

function StatCard({ icon, label, value, color }) {
  const colors = {
    emerald: 'from-emerald-500/20 to-emerald-600/20 text-emerald-400',
    blue: 'from-blue-500/20 to-blue-600/20 text-blue-400',
    yellow: 'from-yellow-500/20 to-yellow-600/20 text-yellow-400',
    red: 'from-red-500/20 to-red-600/20 text-red-400',
  }
  
  return (
    <div className="glass-card p-4">
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${colors[color]} flex items-center justify-center mb-3`}>
        <i className={`fa ${icon}`}></i>
      </div>
      <p className="text-2xl font-bold text-cream">{value}</p>
      <p className="text-sm text-sage">{label}</p>
    </div>
  )
}
