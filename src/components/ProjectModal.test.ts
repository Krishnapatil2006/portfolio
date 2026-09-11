import { describe, it, expect } from 'vitest'
import { extractLiveDemoUrl } from './ProjectModal'

describe('extractLiveDemoUrl', () => {
  it('returns null when readme and homepage are empty or undefined', () => {
    expect(extractLiveDemoUrl(undefined, undefined)).toBeNull()
    expect(extractLiveDemoUrl('', null)).toBeNull()
  })

  it('returns null when readme only contains repo or github links', () => {
    const readme = `
      # TraffiX-AI
      Check out code at https://github.com/kriss2012/TraffiX-AI
      Badges: https://img.shields.io/badge/python-3.8-blue
    `
    expect(extractLiveDemoUrl(readme, null)).toBeNull()
    expect(extractLiveDemoUrl(readme, 'https://github.com/kriss2012/TraffiX-AI')).toBeNull()
  })

  it('detects markdown link for live demo', () => {
    const readme = `
      # Smart Project
      [Live Demo](https://smart-project.onrender.com)
    `
    expect(extractLiveDemoUrl(readme, null)).toBe('https://smart-project.onrender.com')
  })

  it('detects plain text demo URL', () => {
    const readme = `
      ### Deployment
      Live Demo: https://my-app.vercel.app
    `
    expect(extractLiveDemoUrl(readme, null)).toBe('https://my-app.vercel.app')
  })

  it('detects popular cloud hosting URLs in text', () => {
    const readme = `
      The application is hosted on https://ai-medical-consultancy-1.onrender.com for public access.
    `
    expect(extractLiveDemoUrl(readme, null)).toBe('https://ai-medical-consultancy-1.onrender.com')
  })

  it('prefers external homepage if provided', () => {
    const readme = `No demo in readme`
    const homepage = 'https://my-portfolio-tool.streamlit.app'
    expect(extractLiveDemoUrl(readme, homepage)).toBe('https://my-portfolio-tool.streamlit.app')
  })
})
