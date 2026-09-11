/**
 * Centralized API Base URL configuration for Krishna's Portfolio.
 * 
 * In development:
 *   Defaults to empty string so requests hit the Vite dev proxy (`/api -> http://localhost:8000`).
 * 
 * In production:
 *   Configured via `VITE_API_BASE_URL` or `VITE_BACKEND_URL` environment variables
 *   pointing to the Render deployment (e.g. `https://krishna-portfolio-api.onrender.com`).
 *   If served from the same origin, defaults to empty string (`/api`).
 */

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  ''
).replace(/\/$/, '')

export default API_BASE_URL
