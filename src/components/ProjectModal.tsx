import { useState, useEffect, useMemo } from 'react'
import './ProjectModal.css'
import { ProjectDetailData } from '../types'
import { fetchRepoReadme } from '../services/githubApi'

interface ProjectModalProps {
  isOpen: boolean
  project: ProjectDetailData | null
  onClose: () => void
}

type ModalTab = 'mission' | 'readme'

/**
 * Extracts a live demo / deployment link from README markdown or repository homepage.
 * Returns null if no live link is specified in the README (excluding repo/github links).
 */
export function extractLiveDemoUrl(readmeText?: string, homepage?: string | null): string | null {
  // 1. If homepage is configured and is NOT a github repo link
  if (homepage && typeof homepage === 'string' && homepage.startsWith('http')) {
    const clean = homepage.trim()
    if (!clean.includes('github.com') && !clean.includes('shields.io') && !clean.includes('capsule-render')) {
      return clean
    }
  }

  if (!readmeText || typeof readmeText !== 'string') return null

  // 2. Check explicit markdown link patterns: [Live Demo](https://...), [Demo](https://...), [Live Site](https://...), etc.
  const mdLinkRegex = /\[(?:Live\s*Demo|Demo|Live\s*Site|Live\s*App|View\s*Live|Live|Website|Deployment|Try\s*Demo|App)\]\((https?:\/\/[^\s\)]+)\)/i
  const mdMatch = readmeText.match(mdLinkRegex)
  if (mdMatch && mdMatch[1]) {
    const url = mdMatch[1].trim().replace(/[.,)>"']+$/, '')
    if (!url.includes('github.com') && !url.includes('shields.io') && !url.includes('capsule-render')) {
      return url
    }
  }

  // 3. Check plain text labeled links: "Live Demo: https://...", "Demo: https://...", "Deployed at: https://..."
  const textLabelRegex = /(?:Live\s*Demo|Demo\s*URL|Live\s*Site|Demo|Deployment|Website|Deployed\s*(?:at|on))\s*[:\-]\s*(https?:\/\/[^\s\)<>"]+)/i
  const textMatch = readmeText.match(textLabelRegex)
  if (textMatch && textMatch[1]) {
    const url = textMatch[1].trim().replace(/[.,)>"']+$/, '')
    if (!url.includes('github.com') && !url.includes('shields.io') && !url.includes('capsule-render')) {
      return url
    }
  }

  // 4. Check popular web app deployment platform URLs in the README:
  // Vercel, Netlify, Streamlit, Render, Heroku, GitHub Pages
  const deployPlatformRegex = /(https?:\/\/[a-zA-Z0-9_\-]+\.(?:vercel\.app|netlify\.app|streamlit\.app|onrender\.com|render\.com|herokuapp\.com|github\.io\/[a-zA-Z0-9_\-]+))/i
  const platformMatch = readmeText.match(deployPlatformRegex)
  if (platformMatch && platformMatch[1]) {
    const url = platformMatch[1].trim().replace(/[.,)>"']+$/, '')
    if (!url.includes('shields.io') && !url.includes('capsule-render')) {
      return url
    }
  }

  return null
}

export default function ProjectModal({ isOpen, project, onClose }: ProjectModalProps) {
  const [activeTab, setActiveTab] = useState<ModalTab>('mission')
  const [readmeContent, setReadmeContent] = useState<string>('')
  const [loadingReadme, setLoadingReadme] = useState<boolean>(false)
  const [copiedRepo, setCopiedRepo] = useState<boolean>(false)

  // Fetch README whenever modal opens or project changes
  useEffect(() => {
    if (!isOpen || !project) {
      setReadmeContent('')
      setActiveTab('mission')
      setCopiedRepo(false)
      return
    }

    let isMounted = true

    const loadReadme = async () => {
      setLoadingReadme(true)
      try {
        const res = await fetchRepoReadme(project.repo)
        if (isMounted) {
          setReadmeContent(res.content || 'No README details available for this repository.')
        }
      } catch {
        if (isMounted) {
          setReadmeContent('Could not load README from GitHub repository.')
        }
      } finally {
        if (isMounted) {
          setLoadingReadme(false)
        }
      }
    }

    loadReadme()

    return () => {
      isMounted = false
    }
  }, [isOpen, project])

  // Detect live demo link from the README or project demo
  const liveDemoUrl = useMemo(() => {
    if (!project) return null
    return extractLiveDemoUrl(readmeContent, project.demo)
  }, [project, readmeContent])

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  const handleCopyRepo = () => {
    if (!project) return
    const text = `kriss2012/${project.repo}`
    navigator.clipboard.writeText(text).then(() => {
      setCopiedRepo(true)
      setTimeout(() => setCopiedRepo(false), 2000)
    }).catch(() => {})
  }

  if (!isOpen || !project) return null

  return (
    <div className="project-modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="project-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="project-modal-header">
          <div className="project-header-left">
            <div className="project-category-badge">
              {project.category || 'Featured Mission'}
            </div>
            <h2 className="project-modal-title">{project.title}</h2>
          </div>
          <button
            className="project-modal-close"
            onClick={onClose}
            aria-label="Close modal"
            title="Close (Esc)"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="project-modal-tabs">
          <button
            className={`project-tab-btn ${activeTab === 'mission' ? 'active' : ''}`}
            onClick={() => setActiveTab('mission')}
          >
            <span className="tab-icon">🎮</span> Mission Briefing
          </button>
          <button
            className={`project-tab-btn ${activeTab === 'readme' ? 'active' : ''}`}
            onClick={() => setActiveTab('readme')}
          >
            <span className="tab-icon">📜</span> GitHub README
          </button>
        </div>

        {/* Modal Body */}
        <div className="project-modal-body">
          {activeTab === 'mission' ? (
            <div className="project-briefing-content">
              {/* Sleek Steam Hero Banner */}
              <div className="project-hero-card">
                <div className="hero-card-ambient"></div>
                <div className="hero-card-content">
                  <div className="hero-repo-badge">
                    <span className="hero-octocat">🐙</span>
                    <span className="hero-repo-name">kriss2012 / {project.repo}</span>
                  </div>

                  <p className="hero-mission-desc">
                    {project.description || 'AI/ML & scalable software engineering solution built by Krishna Patil.'}
                  </p>

                  <div className="hero-stats-row">
                    <div className="hero-pill star-pill">
                      <span className="pill-icon">⭐</span>
                      <span className="pill-val">{project.stars} Stars</span>
                    </div>
                    <div className="hero-pill fork-pill">
                      <span className="pill-icon">🍴</span>
                      <span className="pill-val">{project.forks} Forks</span>
                    </div>
                    {project.status && (
                      <div className="hero-pill status-pill">
                        <span className="pill-pulse-dot"></span>
                        <span className="pill-val">{project.status}</span>
                      </div>
                    )}
                    {liveDemoUrl && (
                      <div className="hero-pill live-pill">
                        <span className="pill-pulse-dot live"></span>
                        <span className="pill-val">Live Deployed</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Problem Section */}
              {project.problem && (
                <div className="briefing-card problem-card">
                  <div className="briefing-card-title">
                    <span className="section-icon">🎯</span> Problem & Challenge
                  </div>
                  <p className="briefing-card-text">{project.problem}</p>
                </div>
              )}

              {/* Solution Section */}
              {project.solution && (
                <div className="briefing-card solution-card">
                  <div className="briefing-card-title">
                    <span className="section-icon">💡</span> What Krishna Built
                  </div>
                  <p className="briefing-card-text">{project.solution}</p>
                </div>
              )}

              {/* Features List */}
              {project.features && project.features.length > 0 && (
                <div className="briefing-card features-card">
                  <div className="briefing-card-title">
                    <span className="section-icon">⚡</span> Key Features & Architecture
                  </div>
                  <ul className="briefing-features-list">
                    {project.features.map((feature, idx) => (
                      <li key={idx} className="feature-item">
                        <span className="feature-bullet">▸</span>
                        <span className="feature-text">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Tech Stack */}
              <div className="briefing-card tech-card">
                <div className="briefing-card-title">
                  <span className="section-icon">🛠️</span> Technologies Used
                </div>
                <div className="project-modal-tech-tags">
                  {project.tech.map((tech) => (
                    <span key={tech} className="tech-badge">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              {/* Impact / Result */}
              {project.impact && (
                <div className="briefing-card impact-card">
                  <div className="briefing-card-title">
                    <span className="section-icon">🏆</span> Project Impact
                  </div>
                  <p className="briefing-card-text">{project.impact}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="project-readme-content">
              {loadingReadme ? (
                <div className="readme-loading">
                  <div className="loading-spinner"></div>
                  <p>Fetching live README from GitHub...</p>
                </div>
              ) : (
                <div className="readme-container">
                  <div className="readme-toolbar">
                    <span className="readme-file-badge">📄 README.md</span>
                    <a
                      href={`${project.github}#readme`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="readme-external-link"
                    >
                      View on GitHub ↗
                    </a>
                  </div>
                  <pre className="readme-text-viewer">
                    {readmeContent}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer Actions */}
        <div className="project-modal-footer">
          <div className="footer-left">
            <span className="repo-label">Repo:</span>
            <code className="repo-tag" onClick={handleCopyRepo} title="Click to copy repository name">
              {project.repo}
            </code>
            <button
              className="repo-copy-btn"
              onClick={handleCopyRepo}
              title={copiedRepo ? 'Copied!' : 'Copy repo name'}
            >
              {copiedRepo ? '✓ Copied' : '📋'}
            </button>
          </div>

          <div className="footer-actions">
            <a
              href={project.github}
              target="_blank"
              rel="noopener noreferrer"
              className="modal-action-btn github-btn"
            >
              <span>🐙</span> View on GitHub
            </a>
            {/* Show live link ONLY if given in readme or repo */}
            {liveDemoUrl && (
              <a
                href={liveDemoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="modal-action-btn demo-btn"
              >
                <span>🚀</span> Live Demo ↗
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
