import { useEffect, useState, useRef } from 'react'
import { getReplayStatsFromBackend } from '../services/githubApi'
import { GitHubReplayStats } from '../types'
import { useLanguage } from '../contexts/LanguageContext'
import './GitHubReplay.css'

const TOTAL_SLIDES = 6

export default function GitHubReplay() {
  const { t } = useLanguage()
  const [stats, setStats] = useState<GitHubReplayStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentSlide, setCurrentSlide] = useState(0)
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [isAnimating, setIsAnimating] = useState(false)

  const currentYear = new Date().getFullYear()
  const availableYears = [currentYear, currentYear - 1, currentYear - 2]

  const loadStats = async (year: number = selectedYear) => {
    setLoading(true)
    console.log(`[CodeReplay] Request started for year ${year}`)
    try {
      const data = await getReplayStatsFromBackend(year)
      setStats(data)
      if (data) {
        console.log(`[CodeReplay] Response received: ${data.totalCommits} commits, ${data.daysCoded} days coded`)
      } else {
        console.warn('[CodeReplay] No replay stats returned')
      }
    } catch (err) {
      console.error('[CodeReplay] API failed:', err)
      setStats(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let active = true
    setLoading(true)
    console.log(`[CodeReplay] Request started for year ${selectedYear}`)

    getReplayStatsFromBackend(selectedYear)
      .then(data => {
        if (!active) return
        setStats(data)
        if (data) {
          console.log(`[CodeReplay] Response received: ${data.totalCommits} commits, ${data.daysCoded} days coded`)
        } else {
          console.warn('[CodeReplay] No replay stats returned')
        }
      })
      .catch(err => {
        if (!active) return
        console.error('[CodeReplay] API failed:', err)
        setStats(null)
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [selectedYear])

  const animateSlideChange = (update: () => void) => {
    if (isAnimating) return
    setIsAnimating(true)
    update()
    setTimeout(() => setIsAnimating(false), 150)
  }

  const nextSlide = () =>
    animateSlideChange(() =>
      setCurrentSlide(prev => (prev + 1) % TOTAL_SLIDES)
    )

  const prevSlide = () =>
    animateSlideChange(() =>
      setCurrentSlide(prev => (prev - 1 + TOTAL_SLIDES) % TOTAL_SLIDES)
    )

  const goToSlide = (index: number) =>
    animateSlideChange(() => setCurrentSlide(index))

  const formatHour = (hour: number) =>
    hour === 0 ? '12 AM' :
    hour < 12 ? `${hour} AM` :
    hour === 12 ? '12 PM' :
    `${hour - 12} PM`

  if (loading) {
    return (
      <section className="card github-replay">
        <div className="card-header">
          <div className="replay-header-content">
            <span>{t.replayTitle}</span>
            <div className="year-selector">
              <select value={selectedYear} onChange={e => setSelectedYear(+e.target.value)}>
                {availableYears.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="replay-loading">
          <div className="loading-spinner" />
          <p>{t.replayLoading}</p>
        </div>
      </section>
    )
  }

  if (!stats) {
    return (
      <section className="card github-replay">
        <div className="card-header">
          <div className="replay-header-content">
            <span>{t.replayTitle}</span>
            <div className="year-selector">
              <select value={selectedYear} onChange={e => setSelectedYear(+e.target.value)}>
                {availableYears.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
        <div className="replay-error">
          <p>GitHub activity couldn't be loaded.</p>
          <button
            type="button"
            className="btn btn-steam"
            style={{
              marginTop: '12px',
              padding: '8px 20px',
              background: 'linear-gradient(135deg, #1a9fff 0%, #0077cc 100%)',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '13px',
            }}
            onClick={loadStats}
          >
            Retry
          </button>
        </div>
      </section>
    )
  }

  /* ---------- Slides ---------- */

  const renderSlide = () => {
    switch (currentSlide) {

      case 0:
        return (
          <div className="slide slide-overview">
            <div className="slide-emoji">🎮</div>
            <h3>{t.replayOverviewTitle}</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{stats.totalCommits.toLocaleString()}</div>
                <div className="stat-label">{t.replayOverviewCommits}</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.mostActiveMonth}</div>
                <div className="stat-label">{t.replayOverviewMostActiveMonth}</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.longestStreak}</div>
                <div className="stat-label">{t.replayOverviewLongestStreak}</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.daysCoded}</div>
                <div className="stat-label">{t.replayOverviewDaysCoded}</div>
              </div>
            </div>
          </div>
        )

      case 1:
        return (
          <div className="slide slide-language">
            <div className="slide-emoji">💻</div>
            <h3>{t.replayLanguageTitle}</h3>

            <div className="language-hero">
              <div
                className="language-circle"
                style={{ borderColor: stats.topLanguage.color }}
              >
                <div className="language-percentage">{stats.topLanguage.percentage}%</div>
                <div className="language-name">{stats.topLanguage.name}</div>
              </div>

              <p className="language-subtitle">
                {t.replayLanguageSubtitle.replace('{language}', stats.topLanguage.name)}
              </p>
            </div>

            <div className="language-breakdown">
              {stats.languageBreakdown.map(lang => (
                <div key={lang.name} className="language-bar">
                  <div className="language-info">
                    <span className="language-dot" style={{ backgroundColor: lang.color }} />
                    <span className="language-text">{lang.name}</span>
                    <span className="language-percent">{lang.percentage}%</span>
                  </div>
                  <div className="language-progress">
                    <div
                      className="language-fill"
                      style={{
                        width: `${lang.percentage}%`,
                        backgroundColor: lang.color
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="slide slide-impact">
            <div className="slide-emoji">🌟</div>
            <h3>Impact & Reach</h3>

            <div className="impact-stats">
              <div className="impact-primary">
                <div className="impact-number">{stats.starsEarned}</div>
                <div className="impact-label">Total Stars Earned</div>
              </div>

              <div className="impact-grid">
                <div className="impact-item">
                  <div className="impact-icon">🍴</div>
                  <div className="impact-value">{stats.forksGained}</div>
                  <div className="impact-text">Forks Gained</div>
                </div>
                <div className="impact-item">
                  <div className="impact-icon">📦</div>
                  <div className="impact-value">{stats.reposCreated}</div>
                  <div className="impact-text">Repositories</div>
                </div>
              </div>

              <div className="top-repo">
                <p className="top-repo-label">Top Starred Project</p>
                <p className="top-repo-name">{stats.topStarredRepo.name}</p>
                <p className="top-repo-stars">⭐ {stats.topStarredRepo.stars} stars</p>
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="slide slide-productivity">
            <div className="slide-emoji">⏰</div>
            <h3>{t.replayProductivityTitle}</h3>

            <div className="productivity-stats">
              <div className="productivity-row">
                <div className="productivity-card">
                  <div className="productivity-day">{stats.mostProductiveDay}</div>
                  <div className="productivity-label">{t.replayProductivityMostProductiveDay}</div>
                </div>
                <div className="productivity-card">
                  <div className="productivity-hour">
                    {formatHour(stats.peakCodingHour)}
                  </div>
                  <div className="productivity-label">{t.replayProductivityPeakHour}</div>
                </div>
              </div>

              <div className="productivity-badges">
                <div className="badge">
                  <span className="badge-icon">🌙</span>
                  <span className="badge-text">Night Owl</span>
                  <span className="badge-count">{stats.lateNightCommits} commits</span>
                </div>
                <div className="badge">
                  <span className="badge-icon">⚡</span>
                  <span className="badge-text">Weekend Warrior</span>
                  <span className="badge-count">{stats.weekendCommits} commits</span>
                </div>
              </div>
            </div>
          </div>
        )

      case 4:
        return (
          <div className="slide slide-collab">
            <div className="slide-emoji">🤝</div>
            <h3>Community & Collaboration</h3>

            <div className="collab-stats">
              <div className="collab-row">
                <div className="collab-item">
                  <div className="collab-number">{stats.pullRequestsCreated}</div>
                  <div className="collab-label">PRs Opened</div>
                </div>
                <div className="collab-item">
                  <div className="collab-number">{stats.pullRequestsMerged}</div>
                  <div className="collab-label">PRs Merged</div>
                </div>
                <div className="collab-item">
                  <div className="collab-number">{stats.issuesClosed}</div>
                  <div className="collab-label">Issues Closed</div>
                </div>
              </div>

              <div className="collab-top-repo">
                <p className="collab-repo-label">Featured Repository</p>
                <p className="collab-repo-name">{stats.topCollaboratedRepo}</p>
              </div>
            </div>
          </div>
        )

      case 5:
        return (
          <div className="slide slide-growth">
            <div className="slide-emoji">📈</div>
            <h3>Activity & Growth</h3>

            <div className="growth-stats">
              <div className="growth-item">
                <div className="growth-icon">👥</div>
                <div className="growth-number">{stats.followerGrowth}</div>
                <div className="growth-label">Followers</div>
              </div>
              <div className="growth-item">
                <div className="growth-icon">📚</div>
                <div className="growth-number">{stats.repoGrowth}</div>
                <div className="growth-label">Public Repos</div>
              </div>
            </div>

            <div className="growth-heatmap">
              <div className="heatmap-title">Annual Activity Heatmap</div>
              <div className="heatmap-grid">
                <div className="heatmap-container">
                  {stats.contributionDays.map((week, weekIdx) => (
                    <div key={weekIdx} className="heatmap-week">
                      {week.map((count, dayIdx) => {
                        const intensity =
                          count === 0 ? 0 : count >= 13 ? 4 : count >= 8 ? 3 : count >= 4 ? 2 : 1
                        return (
                          <div
                            key={`${weekIdx}-${dayIdx}`}
                            className={`heatmap-day intensity-${intensity}`}
                            title={`${count} contribution${count !== 1 ? 's' : ''}`}
                          />
                        )
                      })}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="replay-footer">
              <p>Keep building and shipping in {selectedYear}!</p>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <section className="card github-replay">
      <div className="card-header">
        <div className="replay-header-content">
          <span>{t.replayTitle}</span>
          <div className="year-selector">
            <select value={selectedYear} onChange={e => setSelectedYear(+e.target.value)}>
              {availableYears.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="replay-carousel">
        <button className="carousel-nav prev" onClick={prevSlide} disabled={isAnimating}>◀</button>

        <div className={`carousel-content ${isAnimating ? 'animating' : ''}`}>
          {renderSlide()}
        </div>

        <button className="carousel-nav next" onClick={nextSlide} disabled={isAnimating}>▶</button>
      </div>

      <div className="carousel-dots">
        {Array.from({ length: TOTAL_SLIDES }).map((_, i) => (
          <button
            key={i}
            className={`dot ${currentSlide === i ? 'active' : ''}`}
            onClick={() => goToSlide(i)}
          />
        ))}
      </div>
    </section>
  )
}
