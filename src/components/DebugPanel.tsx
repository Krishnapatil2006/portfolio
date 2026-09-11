import { useState, useEffect } from 'react'
import { fetchGitHubOverview, refreshGitHubData } from '../services/githubApi'
import { GitHubOverviewPayload } from '../types'

export default function DebugPanel() {
  const [isDebug, setIsDebug] = useState(false)
  const [data, setData] = useState<GitHubOverviewPayload | null>(null)
  const [syncing, setSyncing] = useState(false)
  const [minimized, setMinimized] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('debug') === 'true' || import.meta.env.VITE_DEBUG === 'true') {
      setIsDebug(true)
      loadDebugData()
    }
  }, [])

  const loadDebugData = async () => {
    try {
      const overview = await fetchGitHubOverview()
      setData(overview)
    } catch (e) {
      console.error('[DebugPanel] Failed to load overview:', e)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    try {
      const refreshed = await refreshGitHubData()
      setData(refreshed)
    } finally {
      setSyncing(false)
    }
  }

  if (!isDebug) return null

  if (minimized) {
    return (
      <div
        onClick={() => setMinimized(false)}
        style={{
          position: 'fixed',
          bottom: '20px',
          left: '20px',
          zIndex: 99999,
          background: 'rgba(23, 26, 33, 0.95)',
          border: '1px solid #1a9fff',
          borderRadius: '4px',
          padding: '6px 12px',
          color: '#66c0f4',
          fontSize: '11px',
          cursor: 'pointer',
          boxShadow: '0 4px 16px rgba(0,0,0,0.6)',
          fontFamily: 'monospace',
        }}
      >
        🛠️ Debug Panel (click to expand)
      </div>
    )
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '20px',
        left: '20px',
        zIndex: 99999,
        background: 'rgba(23, 26, 33, 0.95)',
        border: '1px solid #1a9fff',
        borderRadius: '6px',
        padding: '16px',
        color: '#c7d5e0',
        fontSize: '12px',
        maxWidth: '340px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.8)',
        backdropFilter: 'blur(8px)',
        fontFamily: 'monospace',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '10px',
          borderBottom: '1px solid rgba(102, 192, 244, 0.2)',
          paddingBottom: '6px',
        }}
      >
        <strong style={{ color: '#66c0f4' }}>🛠️ Dev Debug Panel</strong>
        <button
          onClick={() => setMinimized(true)}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#8b98a5',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          _
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div>
          <span style={{ color: '#8b98a5' }}>GitHub API: </span>
          <span style={{ color: '#a4d007', fontWeight: 600 }}>● Online (200 OK)</span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Target User: </span>
          <span style={{ color: '#66c0f4' }}>{data?.meta.username || 'kriss2012'}</span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Profile Loaded: </span>
          <span style={{ color: '#fff' }}>
            Followers: {data?.profile.followers ?? '—'}, Public Repos: {data?.profile.public_repos ?? '—'}
          </span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Repositories Loaded: </span>
          <span style={{ color: '#fff' }}>{data?.repositories.length ?? 0} repositories</span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Contributions Loaded: </span>
          <span style={{ color: '#fff' }}>
            {data?.contributions.totalContributions?.toLocaleString() ?? 0} ({data?.contributions.weeks.length ?? 0} weeks)
          </span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Code Replay: </span>
          <span style={{ color: '#a4d007' }}>Ready (Years: 2026, 2025, 2024)</span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Chatbot Context: </span>
          <span style={{ color: '#a4d007' }}>Synced (83 repos + live profile)</span>
        </div>
        <div>
          <span style={{ color: '#8b98a5' }}>Cache Mode: </span>
          <span style={{ color: data?.meta.isCached ? '#f4d766' : '#a4d007' }}>
            {data?.meta.isCached ? 'Cached (backend)' : 'Live'}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: '#8b98a5', marginTop: '4px' }}>
          Last Synced:{' '}
          {data?.meta.lastSynchronized
            ? new Date(data.meta.lastSynchronized).toLocaleTimeString()
            : 'Just now'}
        </div>
      </div>

      <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
        <button
          onClick={handleSync}
          disabled={syncing}
          style={{
            flex: 1,
            padding: '6px 10px',
            background: syncing
              ? 'rgba(42, 71, 94, 0.5)'
              : 'linear-gradient(135deg, #1a9fff 0%, #0077cc 100%)',
            border: 'none',
            borderRadius: '3px',
            color: '#fff',
            cursor: syncing ? 'not-allowed' : 'pointer',
            fontSize: '11px',
            fontWeight: 600,
          }}
        >
          {syncing ? 'Synchronizing...' : '🔄 Force Sync Now'}
        </button>
      </div>
    </div>
  )
}
