import { useEffect, useState, useCallback } from 'react'
import './Showcases.css'
import { portfolioConfig } from '../config/portfolio.config'
import { CURATED_PROJECTS } from '../config/projectsData'
import { fetchGitHubOverview } from '../services/githubApi'
import { ProcessedProject, ProjectDetailData } from '../types'
import { trackSectionVisit, trackProjectView } from '../services/achievementService'
import { useLanguage } from '../contexts/LanguageContext'
import ProjectModal from './ProjectModal'

function FeaturedProjects() {
  const [featuredProjects, setFeaturedProjects] = useState<ProcessedProject[]>([])
  const [selectedProject, setSelectedProject] = useState<ProjectDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  const { t } = useLanguage()

  const loadFeaturedProjects = useCallback(async () => {
    setLoading(true)

    try {
      // 1. Fetch live repository overview through the centralized backend service
      const overview = await fetchGitHubOverview()
      const liveRepos = overview.repositories || []

      // 2. Build map of live repos for O(1) lookup
      const liveRepoMap = new Map<string, typeof liveRepos[0]>()
      liveRepos.forEach((r) => {
        liveRepoMap.set(r.name.toLowerCase(), r)
      })

      // 3. Map configured featured projects, enriching with live GitHub stats + curated briefing
      const projects: ProcessedProject[] = portfolioConfig.featuredProjects
        .filter((fp) => fp.featured)
        .map((fp, index) => {
          const repoKey = fp.repo.toLowerCase()
          const liveRepo = liveRepoMap.get(repoKey)
          const curated = CURATED_PROJECTS[fp.repo] || CURATED_PROJECTS[liveRepo?.name || '']

          const techStack = liveRepo?.topics?.length
            ? liveRepo.topics
            : curated?.defaultTech || [liveRepo?.language || 'Python']

          return {
            id: liveRepo?.id || 1000 + index,
            repoName: fp.repo,
            title: fp.customTitle || curated?.title || liveRepo?.title || fp.repo.replace(/-/g, ' '),
            description: fp.customDescription || curated?.problem || liveRepo?.description || 'Scalable software engineering project built by Krishna Patil.',
            image: liveRepo?.image || `https://opengraph.githubassets.com/1/${portfolioConfig.social.github}/${fp.repo}`,
            tech: techStack,
            stars: liveRepo?.stars ?? (curated ? 12 : 5),
            forks: liveRepo?.forks ?? 4,
            language: liveRepo?.language || 'Python',
            github: liveRepo?.htmlUrl || `https://github.com/${portfolioConfig.social.github}/${fp.repo}`,
            demo: fp.demoUrl || (liveRepo?.homepage && !liveRepo.homepage.includes('github.com') ? liveRepo.homepage : undefined),
            isFeatured: true,
            lastUpdated: liveRepo?.updatedAtRelative || 'recently',
            problem: curated?.problem,
            solution: curated?.solution,
            features: curated?.features,
            impact: curated?.impact,
            status: curated?.status || 'Active',
          }
        })

      setFeaturedProjects(projects)
    } catch (error) {
      console.error('Featured projects load failed:', error)
      // Safe fallback using curated project config so portfolio never looks broken
      const fallbackProjects: ProcessedProject[] = portfolioConfig.featuredProjects
        .filter((fp) => fp.featured)
        .map((fp, index) => {
          const curated = CURATED_PROJECTS[fp.repo]
          return {
            id: 1000 + index,
            repoName: fp.repo,
            title: fp.customTitle || curated?.title || fp.repo.replace(/-/g, ' '),
            description: fp.customDescription || curated?.problem || 'Software engineering project built by Krishna Patil.',
            image: `https://opengraph.githubassets.com/1/${portfolioConfig.social.github}/${fp.repo}`,
            tech: curated?.defaultTech || ['Python', 'AI/ML'],
            stars: 12,
            forks: 4,
            language: 'Python',
            github: `https://github.com/${portfolioConfig.social.github}/${fp.repo}`,
            demo: fp.demoUrl,
            isFeatured: true,
            lastUpdated: 'recently',
            problem: curated?.problem,
            solution: curated?.solution,
            features: curated?.features,
            impact: curated?.impact,
            status: curated?.status || 'Active',
          }
        })
      setFeaturedProjects(fallbackProjects)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadFeaturedProjects()
  }, [loadFeaturedProjects])

  // Track section visit
  useEffect(() => {
    const section = document.getElementById('projects')
    if (!section) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          trackSectionVisit('projects')
        }
      },
      { threshold: 0.1 }
    )

    observer.observe(section)
    return () => observer.disconnect()
  }, [])

  const handleOpenDetails = (project: ProcessedProject) => {
    trackProjectView(project.id.toString())
    const curated = CURATED_PROJECTS[project.repoName || '']
    setSelectedProject({
      id: project.id,
      repo: project.repoName || project.title,
      title: project.title,
      category: curated?.category || 'AI/ML & Software Engineering',
      description: project.description,
      problem: project.problem || curated?.problem,
      solution: project.solution || curated?.solution,
      features: project.features || curated?.features,
      tech: project.tech,
      stars: project.stars,
      forks: project.forks,
      github: project.github,
      demo: project.demo,
      impact: project.impact || curated?.impact,
      status: project.status || curated?.status,
      image: project.image,
    })
  }

  return (
    <section id="projects" className="showcase-card card featured-projects-section">
      <div className="card-header-wrapper">
        <div className="card-header">{t.featuredProjects}</div>
        <span className="featured-count-badge">Curated Repositories ({featuredProjects.length})</span>
      </div>

      {loading ? (
        <div className="featured-projects-grid loading">
          <p className="loading-text">{t.loading}</p>
        </div>
      ) : featuredProjects.length > 0 ? (
        <div className="featured-projects-grid">
          {featuredProjects.map((project) => (
            <div
              key={project.id}
              className="featured-project-card"
              onClick={() => handleOpenDetails(project)}
            >
              {/* Project Image & Live Stats Badge Overlay */}
              <div className="project-image">
                <img
                  src={project.image || '/project-fallback.png'}
                  alt={project.title}
                  loading="lazy"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/project-fallback.png'
                  }}
                />
                <div className="project-overlay">
                  <div className="project-stats">
                    <span className="stat">
                      <span className="stat-icon">⭐</span>
                      <span>{project.stars}</span>
                    </span>
                    <span className="stat">
                      <span className="stat-icon">🍴</span>
                      <span>{project.forks}</span>
                    </span>
                  </div>
                  <span className="featured-badge">Featured Mission</span>
                </div>
              </div>

              {/* Project Info */}
              <div className="project-info">
                <div className="project-title-row">
                  <h3 className="project-title">{project.title}</h3>
                </div>

                <p className="project-description">{project.description}</p>

                {/* Tech Badges */}
                <div className="project-tech">
                  {project.tech.slice(0, 4).map((tech) => (
                    <span key={tech} className="tech-tag">
                      {tech}
                    </span>
                  ))}
                  {project.tech.length > 4 && (
                    <span className="tech-tag more-tag">+{project.tech.length - 4}</span>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="project-actions" onClick={(e) => e.stopPropagation()}>
                  <button
                    type="button"
                    className="project-link details-btn"
                    onClick={() => handleOpenDetails(project)}
                  >
                    <span>🔍</span> Details
                  </button>

                  <a
                    href={project.github}
                    className="project-link"
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => trackProjectView(project.id.toString())}
                  >
                    Code
                  </a>

                  {project.demo && (
                    <a
                      href={project.demo}
                      className="project-link primary"
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={() => trackProjectView(project.id.toString())}
                    >
                      Demo
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="error-text">No featured projects available right now.</p>
      )}

      {/* Steam-Styled Project Details Modal */}
      <ProjectModal
        isOpen={!!selectedProject}
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
      />
    </section>
  )
}

export default FeaturedProjects
