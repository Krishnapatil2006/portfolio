// Portfolio Configuration Types
export interface PersonalInfo {
  name: string
  title: string
  location: string
  bio: string
  email: string
  phone?: string
  birthday?: string
  avatar?: string
  banner?: string
  resumeUrl?: string
}

export interface SocialLinks {
  github: string
  linkedin?: string
  twitter?: string
  website?: string
  youtube?: string
  instagram?: string
}

export interface FeaturedProject {
  repo: string
  demoUrl?: string
  featured?: boolean
  customTitle?: string
  customDescription?: string
}

export interface Achievement {
  id: number
  title: string
  description: string
  icon: string
  logo?: string
  year?: number
  unlocked: boolean
  rarity?: 'common' | 'rare' | 'epic' | 'legendary'
  badge?: string
}

export interface Hobby {
  id: number
  title: string
  description: string
  icon: string
  status?: string
}

export interface VisitorAchievement {
  id: string
  title: string
  description: string
  icon: string
  unlocked: boolean
  unlockedAt?: number
  trigger: 'auto' | 'scroll' | 'click' | 'time' | 'easter-egg'
  triggerCondition?: string
  rarity?: 'common' | 'rare' | 'epic' | 'legendary'
  xp?: number
}

export interface WorkStatus {
  status: 'available' | 'employed' | 'away' | 'busy'
  message: string
}

export interface CareerMilestone {
  year: string
  title: string
  role?: string
  organization?: string
  description: string
  highlights: string[]
  icon: string
}

export interface PortfolioConfig {
  personal: PersonalInfo
  social: SocialLinks
  workStatus: WorkStatus
  featuredProjects: FeaturedProject[]
  achievements: Achievement[]
  journey: CareerMilestone[]
  hobbies: Hobby[]
  technicalSkills: { [category: string]: string[] }
  showTestimonials: boolean
  showAllRepos: boolean
  staticStats?: {
    totalRepos: number
    totalStars: number
    totalForks: number
    followers: number
    totalCommits: number
  }
}

// GitHub API Models
export interface GitHubUser {
  login: string
  avatar_url: string
  name: string
  bio: string
  location: string
  email: string | null
  public_repos: number
  followers: number
  following: number
  created_at: string
  updated_at: string
  html_url: string
  blog?: string
  company?: string | null
  account_age_years?: number
  isCached?: boolean
  lastUpdated?: string
}

export interface GitHubRepo {
  id: number
  name: string
  full_name: string
  description: string | null
  html_url: string
  homepage: string | null
  stargazers_count: number
  watchers_count: number
  forks_count: number
  fork: boolean
  language: string | null
  languages_url: string
  created_at: string
  updated_at: string
  pushed_at: string
  topics: string[]
}

// Live Processed Types for UI
export interface LiveProject {
  id: number
  name: string
  title: string
  description: string
  language: string
  languageColor: string
  topics: string[]
  stars: number
  forks: number
  openIssues: number
  size: number
  isFork: boolean
  htmlUrl: string
  homepage: string | null
  updatedAt: string
  updatedAtRelative: string
  createdAt: string
  category: string
  image: string
  isFeatured?: boolean
}

export interface ContributionDay {
  contributionCount: number
  date: string
  weekday: number
  color: string
}

export interface ContributionWeek {
  contributionDays: ContributionDay[]
}

export interface ContributionData {
  year: number
  totalContributions: number
  totalCommits: number
  totalPullRequests: number
  totalIssues: number
  totalRepositories: number
  totalReviews: number
  activeDays: number
  longestStreak: number
  currentStreak: number
  weeks: ContributionWeek[]
  availableYears: number[]
  isCached?: boolean
  lastUpdated?: string
}

export interface LanguageDistribution {
  name: string
  bytes: number
  percentage: number
  reposCount: number
  color: string
}

export interface LanguageAnalytics {
  languages: LanguageDistribution[]
  totalLanguagesCount: number
  totalReposAnalyzed: number
  lastUpdated?: string
}

export interface CommitItem {
  sha: string
  fullSha: string
  message: string
  repository: string
  repositoryUrl: string
  date: string
  dateRelative: string
  commitUrl: string
  author: string
}

export interface ActivityItem {
  id: string
  type: string
  badge: string
  icon: string
  repo: string
  repoUrl: string
  description: string
  createdAt: string
  timeAgo: string
  commits?: Array<{ sha: string; message: string }>
}

export interface GitHubStatsSummary {
  totalRepos: number
  totalStars: number
  totalForks: number
  totalCommits: number
  totalContributions: number
  totalPullRequests: number
  totalIssues: number
  totalReviews: number
  followers: number
  following: number
  activeDays: number
  longestStreak: number
  currentStreak: number
}

export interface GitHubOverviewPayload {
  profile: GitHubUser
  statistics: GitHubStatsSummary
  contributions: ContributionData
  languages: LanguageAnalytics
  repositories: LiveProject[]
  commits: CommitItem[]
  activity: ActivityItem[]
  meta: {
    username: string
    isCached: boolean
    lastSynchronized: string
    serverTime: string
  }
}

// Backwards compatibility types
export interface ProcessedProject {
  id: number
  title: string
  description: string
  image?: string
  tech: string[]
  stars: number
  forks: number
  language: string
  github: string
  demo: string | null
  isFeatured: boolean
  lastUpdated: string
  repoName?: string
  problem?: string
  solution?: string
  features?: string[]
  impact?: string
  status?: string
}

export interface ProjectDetailData {
  id: string | number
  repo: string
  title: string
  category?: string
  description: string
  problem?: string
  solution?: string
  features?: string[]
  tech: string[]
  stars: number
  forks: number
  github: string
  demo?: string | null
  impact?: string
  status?: string
  readme?: string
  image?: string
}

export interface ProcessedStats {
  totalProjects: number
  totalStars: number
  totalForks: number
  totalCommits: number
  languages: Array<{
    name: string
    percentage: number
    color: string
  }>
  completionRate: number
}

export interface ProcessedActivity {
  id: string
  type: 'commit' | 'release' | 'star' | 'pr' | 'issue' | 'fork'
  action: string
  target: string
  time: string
  icon: string
}

export interface GitHubReplayStats {
  year: number
  totalCommits: number
  mostActiveMonth: string
  longestStreak: number
  daysCoded: number
  topLanguage: {
    name: string
    percentage: number
    color: string
  }
  languageBreakdown: Array<{
    name: string
    percentage: number
    color: string
  }>
  starsEarned: number
  forksGained: number
  topStarredRepo: {
    name: string
    stars: number
  }
  reposCreated: number
  mostProductiveDay: string
  peakCodingHour: number
  lateNightCommits: number
  weekendCommits: number
  pullRequestsCreated: number
  pullRequestsMerged: number
  issuesClosed: number
  topCollaboratedRepo: string
  followerGrowth: number
  repoGrowth: number
  contributionDays: number[][]
}
