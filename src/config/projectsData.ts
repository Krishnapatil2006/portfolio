/**
 * Curated project problem-solution context for Krishna Patil's featured projects.
 * Combined with real-time GitHub stats (stars, forks, live commit dates, demo URLs).
 */

export interface CuratedProjectInfo {
  repo: string
  title: string
  category: string
  problem: string
  solution: string
  features: string[]
  impact: string
  status: string
  defaultTech: string[]
}

export const CURATED_PROJECTS: Record<string, CuratedProjectInfo> = {
  'TraffiX-AI': {
    repo: 'TraffiX-AI',
    title: 'TraffiX AI — Intelligent Traffic Analysis & Optimization',
    category: 'AI/ML & Computer Vision',
    problem: 'Fixed-timer traffic lights fail to adapt to live vehicle fluctuations, causing severe congestion, unnecessary commute delays, and increased fuel emissions at busy intersections.',
    solution: 'Engineered an end-to-end computer vision pipeline using YOLO and OpenCV that monitors live traffic cameras, estimates lane queue density in real time, and dynamically controls signal phases.',
    features: [
      'Real-time vehicle detection and classification (cars, bikes, buses, trucks)',
      'Adaptive signal switching algorithm based on queue density',
      'Congestion heatmaps and rapid anomaly/incident alert generation',
      'Optimized lightweight inference designed for edge deployment',
    ],
    impact: 'Reduces junction idle times by dynamically prioritizing congested corridors and eliminates reliance on expensive physical ground sensors.',
    status: 'Active / Deployed',
    defaultTech: ['Python', 'OpenCV', 'YOLO', 'TensorFlow', 'Flask', 'NumPy'],
  },
  'Plagiarism-Checker': {
    repo: 'Plagiarism-Checker',
    title: 'Plagiarism Checker AI — Structural Code & Text Analysis',
    category: 'AI/ML & NLP',
    problem: 'Conventional plagiarism scanners only check literal string similarity, allowing copied source code to slip through if variable names are renamed or code blocks are reordered.',
    solution: 'Designed a dual-engine analysis system: AST (Abstract Syntax Tree) tokenization for deep structural code equivalence combined with TF-IDF cosine similarity for textual documents.',
    features: [
      'Structural code equivalence analysis invariant to renamed identifiers',
      'Document semantic similarity evaluation with highlighted overlaps',
      'Side-by-side comparative inspection UI for academic & review workflows',
      'Batch submission support with instant similarity scoring reports',
    ],
    impact: 'Ensures reliable, tamper-proof academic and code integrity checks with granular similarity attribution.',
    status: 'Complete & Active',
    defaultTech: ['Python', 'NLP', 'AST Parsing', 'scikit-learn', 'Flask', 'HTML5/CSS3'],
  },
  'BashaConverter-Krishna': {
    repo: 'BashaConverter-Krishna',
    title: 'BashaConverter — Multilingual Regional NLP System',
    category: 'NLP & Localization',
    problem: 'Cross-lingual digital communication often degrades domain-specific context and suffers from latency when translating vernacular idioms.',
    solution: 'Developed a neural translation platform leveraging fine-tuned transformer models specialized in regional linguistic localization and sub-second translation inference.',
    features: [
      'High-speed bidirectional regional translation',
      'Domain phrasing preservation for technical and colloquial expressions',
      'Clean web interface with real-time preview and REST API endpoints',
      'Lightweight caching for repeated query acceleration',
    ],
    impact: 'Improved cross-cultural communication efficiency by 40% during internal benchmarking.',
    status: 'Complete',
    defaultTech: ['Python', 'NLP', 'Transformers', 'FastAPI', 'JavaScript'],
  },
  'fake-review-id-system': {
    repo: 'fake-review-id-system',
    title: 'Fake Reviews Identification System',
    category: 'Machine Learning & Fraud Detection',
    problem: 'E-commerce marketplaces and review platforms are flooded with synthesized and incentivized fake reviews that manipulate consumer purchasing decisions.',
    solution: 'Trained and tuned a supervised ML ensemble classifier on 100,000+ consumer reviews using NLP text preprocessing, sentiment divergence, and behavioral metadata.',
    features: [
      '95% model classification accuracy benchmarked on 100,000+ reviews',
      'Linguistic pattern inspection detecting deceptive sentiment signals',
      'Instant single-review diagnostic score and bulk CSV dataset ingestion',
      'Visual breakdown dashboard with confidence metrics',
    ],
    impact: 'Empowers platforms and shoppers to verify authentic review signals with 95% verified accuracy.',
    status: 'Complete',
    defaultTech: ['Python', 'scikit-learn', 'NLP', 'Pandas', 'Flask'],
  },
  'AI-Medical-Consultancy': {
    repo: 'AI-Medical-Consultancy',
    title: 'AI Medical Consultancy System (MediAI Pro)',
    category: 'Healthcare AI & Full Stack',
    problem: 'Patients face long wait times for preliminary medical guidance, while clinics struggle with intake triage efficiency.',
    solution: 'A secure healthcare consultation platform matching patient-reported symptoms with disease probability vectors in <2s, integrated with role-based doctor scheduling.',
    features: [
      'NLP symptom parser providing differential diagnostic probabilities in under 2 seconds',
      'Google OAuth 2.0 authentication and role-based access for doctors and patients',
      'Razorpay payment gateway integration for appointment bookings',
      'Administrative healthcare telemetry and triage dashboard',
    ],
    impact: 'Delivers sub-2-second preliminary diagnostic triage hints to expedite clinical care.',
    status: 'Active',
    defaultTech: ['Python', 'Flask', 'PostgreSQL', 'scikit-learn', 'Tailwind CSS'],
  },
  'kirito1.0': {
    repo: 'kirito1.0',
    title: 'KIRITO 1.0 — Voice Desktop Assistant',
    category: 'Automation & Voice AI',
    problem: 'Repetitive desktop tasks and multitasking consume excessive manual time when working across complex development environments.',
    solution: 'Built a voice-operated desktop virtual assistant combining speech recognition, text-to-speech feedback, system telemetry, and a pywebview GUI.',
    features: [
      'Natural voice command recognition with auditory feedback',
      'Application launching, browser controls, and system setting automation',
      'Automated web search, weather briefings, and media controls',
      'Interactive desktop graphical dashboard',
    ],
    impact: 'Enables fully hands-free desktop task execution and rapid developer workflow shortcuts.',
    status: 'Active',
    defaultTech: ['Python', 'speech_recognition', 'pyttsx3', 'pywebview', 'JavaScript'],
  },
}
