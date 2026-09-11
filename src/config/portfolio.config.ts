import { PortfolioConfig } from '../types'

/**
 * Portfolio Configuration for Krishna Patil
 * Data-Driven & Configurable Layer
 */
export const portfolioConfig: PortfolioConfig = {
  // Personal Information
  personal: {
    name: 'Krishna Patil',
    title: 'Software Developer | AI/ML Enthusiast | Full Stack Developer',
    location: 'Pachora, Maharashtra, India',
    bio: 'BCA student (3rd Year) specializing in Computational Science at G. H. Raisoni Institute of Engineering, Jalgaon. Passionate about building scalable applications, AI/ML models, and real-world software solutions with 99+ repositories and 21,000+ commits.',
    email: '202krishnapatil@gmail.com',
    phone: '+91 9850159631',
    birthday: '2006-02-20',
    banner: '/profile-background.jpg',
    resumeUrl: '/resume.pdf',
    avatar: '/Profile-Image.jpeg',
  },

  // Social Media & Professional Links
  social: {
    github: 'kriss2012',
    linkedin: 'https://www.linkedin.com/in/krishna-patil-33969536b/',
    website: 'https://tgkrish-portfolio.netlify.app/',
    youtube: 'https://www.youtube.com/@IQOOTGKRISH-13',
    instagram: 'https://www.instagram.com/mr_krishna_yt____',
  },

  // Current Work Status
  workStatus: {
    status: 'available',
    message: 'Open to Software Engineering & AI/ML Roles & Internships',
  },

  // Featured Repositories (Metadata enriched automatically via live GitHub API)
  featuredProjects: [
    {
      repo: 'TraffiX-AI',
      customTitle: 'TraffiX AI — Intelligent Traffic Analysis',
      customDescription: 'AI-powered real-time traffic detection, vehicle tracking, and density management pipeline using Computer Vision and deep learning.',
      featured: true,
      demoUrl: undefined,
    },
    {
      repo: 'Plagiarism-Checker',
      customTitle: 'Plagiarism Checker AI',
      customDescription: 'High-accuracy code and text plagiarism detection engine using NLP similarity scoring and tokenized AST comparison.',
      featured: true,
      demoUrl: undefined,
    },
    {
      repo: 'BashaConverter-Krishna',
      customTitle: 'BashaConverter — Multilingual NLP System',
      customDescription: 'Multilingual neural translation platform improving cross-lingual communication efficiency by 40% with fast inference.',
      featured: true,
      demoUrl: undefined,
    },
    {
      repo: 'fake-review-id-system',
      customTitle: 'Fake Reviews Identification System',
      customDescription: 'Machine learning fraud detection classifier achieving 95% accuracy on 100,000+ consumer reviews using NLP & ensemble models.',
      featured: true,
      demoUrl: undefined,
    },
    {
      repo: 'AI-Medical-Consultancy',
      customTitle: 'AI Medical Consultancy System (MediAI Pro)',
      customDescription: 'Diagnostic health assistant providing symptom assessment, triage recommendations, and real-time medical insights in <2s.',
      featured: true,
      demoUrl: 'https://ai-medical-consultancy-1.onrender.com',
    },
    {
      repo: 'kirito1.0',
      customTitle: 'KIRITO 1.0 — Voice Desktop Assistant',
      customDescription: 'Voice-controlled desktop automation assistant combining speech recognition, system APIs, and an interactive UI.',
      featured: true,
      demoUrl: undefined,
    },
  ],

  // Achievements & Awards
  achievements: [
    {
      id: 1,
      title: 'Shark Tank Winner — 1st Prize',
      description: 'Awarded 1st place in university-wide entrepreneurial innovation challenge for technical product prototype.',
      icon: '🏆',
      year: 2025,
      unlocked: true,
      rarity: 'legendary',
      badge: '1st Prize Winner',
    },
    {
      id: 2,
      title: 'Shark Tank Runner-Up — 2nd Prize',
      description: 'Secured 2nd position among 50+ teams for startup pitch and technical demonstration.',
      icon: '🥈',
      year: 2024,
      unlocked: true,
      rarity: 'epic',
      badge: 'Runner Up',
    },
    {
      id: 3,
      title: 'AI & Machine Learning Internship',
      description: 'Completed 150-hour hands-on industrial internship at iBase Electrosoft LLP building ML pipelines and predictive models.',
      icon: '🤖',
      year: 2025,
      unlocked: true,
      rarity: 'epic',
      badge: 'iBase Electrosoft',
    },
    {
      id: 4,
      title: '95% ML Model Accuracy Milestone',
      description: 'Trained and validated fraud detection model on 100,000+ customer reviews with 95% classification accuracy.',
      icon: '📊',
      year: 2025,
      unlocked: true,
      rarity: 'rare',
      badge: '95% Accuracy',
    },
    {
      id: 5,
      title: 'Vice President, Coders Club',
      description: 'Elected Vice President of the student Coders Club, mentoring 100+ students in Python, algorithms, and hackathon prep.',
      icon: '⚡',
      year: 2025,
      unlocked: true,
      rarity: 'epic',
      badge: 'VP Leadership',
    },
    {
      id: 6,
      title: 'Head of Gaming, Pinnacle IT Fest',
      description: 'Spearheaded organization and tournament infrastructure for national-level technical symposium "Pinnacle".',
      icon: '🎮',
      year: 2025,
      unlocked: true,
      rarity: 'rare',
      badge: 'National Event',
    },
  ],

  // Developer Journey Timeline (2024 - 2026)
  journey: [
    {
      year: '2024',
      title: 'The Foundation & Software Exploration',
      organization: 'BCA Computational Science',
      description: 'Started computer science degree at G.H. Raisoni Institute. Dove into foundational computer science, C++, Python, algorithms, and built first 20+ software tools.',
      highlights: [
        'Built foundational projects in Python, C++, and Web basics',
        '2nd Prize Runner-Up in Shark Tank Pitch 2024',
        'Began open-source GitHub journey and daily coding practice',
      ],
      icon: '🚀',
    },
    {
      year: '2025',
      title: 'AI/ML Breakthrough & Scalable Systems',
      organization: 'iBase Electrosoft LLP & University',
      description: 'Intensively expanded into Machine Learning, Natural Language Processing, and full-stack web applications. Built high-accuracy fraud detectors, medical assistants, and multilingual translation systems.',
      highlights: [
        '1st Prize Winner — Shark Tank Innovation Challenge 2025',
        '150-Hour Industrial ML Internship at iBase Electrosoft LLP',
        'Elected Vice President of Coders Club & Head of Gaming for Pinnacle',
        'Authored models reaching 95% classification accuracy',
      ],
      icon: '🧠',
    },
    {
      year: '2026',
      title: 'Advanced Full-Stack, Generative AI & Live Portfolio',
      organization: '3rd Year BCA / Open Source',
      description: 'Reached 99+ repositories, 21,000+ commits, and 74,000+ GitHub contributions. Built custom AI Twin Chatbot with LangChain and RAG, TraffiX AI Computer Vision pipeline, and modern live portfolio.',
      highlights: [
        'Surpassed 99 public GitHub repositories & 21k+ commits',
        'Engineered TraffiX-AI and live RAG-based AI Twin Chatbot',
        'Preparing for entry-level Software Development & AI/ML roles',
      ],
      icon: '🌟',
    },
  ],

  // Personal Interests
  hobbies: [
    {
      id: 1,
      title: 'Badminton Player',
      description: 'State-level competitive player — on the court every weekend sharpening reflexes and stamina.',
      icon: '🏸',
      status: 'Active Player',
    },
    {
      id: 2,
      title: 'Gaming Enthusiast',
      description: 'Longtime player of Red Dead Redemption, Resident Evil, and competitive titles (6+ years).',
      icon: '🎮',
      status: 'Avid Gamer',
    },
    {
      id: 3,
      title: 'AI & Open Source',
      description: 'Constantly tinkering with local LLMs, LangChain agents, computer vision, and automation tools.',
      icon: '💡',
      status: 'Continuous Builder',
    },
    {
      id: 4,
      title: 'Anime & Fiction',
      description: 'Big fan of One Piece, Naruto, Bleach, and Harry Potter series.',
      icon: '📚',
      status: 'Enthusiast',
    },
  ],

  // Verified Technical Skills
  technicalSkills: {
    'Programming Languages': ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'HTML5', 'CSS3', 'SQL'],
    'AI & Machine Learning': [
      'TensorFlow',
      'PyTorch',
      'Scikit-learn',
      'Natural Language Processing (NLP)',
      'Computer Vision (OpenCV)',
      'LangChain',
      'RAG Pipelines',
      'LLM Integration (Groq, Gemini)',
    ],
    'Web & Full Stack': [
      'React',
      'Node.js',
      'FastAPI',
      'Flask',
      'Django',
      'REST APIs',
      'Vite',
      'Responsive Web Design',
    ],
    'Databases & Storage': ['PostgreSQL', 'MySQL', 'MongoDB', 'ChromaDB (Vector DB)', 'SQLite'],
    'DevOps & Tools': [
      'Git & GitHub',
      'GitHub Actions (CI/CD)',
      'Docker',
      'Linux',
      'Postman',
      'VS Code',
      'Vercel / Netlify / Render',
    ],
    'Core Concepts': [
      'Data Structures & Algorithms',
      'Object-Oriented Programming (OOP)',
      'Model Deployment & MLOps',
      'System Design Basics',
      'Agile / Scrum',
    ],
  },

  showTestimonials: false,
  showAllRepos: true,

  staticStats: {
    totalRepos: 99,
    totalStars: 18,
    totalForks: 8,
    followers: 9,
    totalCommits: 21385,
  },
}

// Helper function to calculate years of experience
export const getYearsOfExperience = (): number => {
  const startYear = 2024
  const currentYear = new Date().getFullYear()
  return Math.max(1, currentYear - startYear)
}

// Helper function to get work status config
export const getWorkStatusConfig = (status: string) => {
  const statusConfig = {
    available: {
      badge: 'online',
      text: 'Open to Work',
      color: '#a4d007',
    },
    employed: {
      badge: 'ingame',
      text: 'Employed',
      color: '#66c0f4',
    },
    away: {
      badge: 'away',
      text: 'Away',
      color: '#d69e2e',
    },
    busy: {
      badge: 'busy',
      text: 'Busy',
      color: '#e53e3e',
    },
  }
  return statusConfig[status as keyof typeof statusConfig] || statusConfig.available
}

// Helper function to calculate age
export const getAge = (): number => {
  const birthday = new Date(portfolioConfig.personal.birthday)
  const today = new Date()
  let age = today.getFullYear() - birthday.getFullYear()
  const monthDiff = today.getMonth() - birthday.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthday.getDate())) {
    age--
  }

  return age
}

export default portfolioConfig
