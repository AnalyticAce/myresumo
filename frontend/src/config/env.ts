import { z } from 'zod'

// Environment variable schema for validation
const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url().default('http://localhost:8000'),
  VITE_API_TIMEOUT: z.string().transform(val => Number(val)).default('60000'),
  VITE_APP_TITLE: z.string().default('PowerCV'),
  VITE_APP_VERSION: z.string().default('1.0.0'),
  VITE_APP_DESCRIPTION: z.string().default('Professional Resume Optimization Platform'),
  VITE_ENABLE_ANALYTICS: z.string().transform(val => val === 'true').default('false'),
  VITE_ENABLE_ERROR_REPORTING: z.string().transform(val => val === 'true').default('false'),
  VITE_ENABLE_PERFORMANCE_MONITORING: z.string().transform(val => val === 'true').default('false'),
  VITE_AUTH_REQUIRED: z.string().transform(val => val === 'true').default('false'),
  VITE_AUTH_PROVIDER: z.string().optional(),
  VITE_AUTH_DOMAIN: z.string().optional(),
  VITE_MAX_FILE_SIZE: z.string().transform(val => Number(val)).default('10485760'),
  VITE_ALLOWED_FILE_TYPES: z.string().default('pdf,docx,doc,txt,md'),
  VITE_ENABLE_LAZY_LOADING: z.string().transform(val => val === 'true').default('true'),
  VITE_ENABLE_CODE_SPLITTING: z.string().transform(val => val === 'true').default('true'),
  VITE_ENABLE_COMPRESSION: z.string().transform(val => val === 'true').default('true'),
  VITE_SENTRY_DSN: z.string().optional(),
  VITE_GOOGLE_ANALYTICS_ID: z.string().optional(),
  VITE_DEV_MODE: z.string().transform(val => val === 'true').default('true'),
  VITE_DEBUG_MODE: z.string().transform(val => val === 'true').default('false'),
})

// Validate and export environment variables
export const env = envSchema.parse(import.meta.env)

// Helper functions for environment-specific logic
export const isDevelopment = env.VITE_DEV_MODE
export const isProduction = !isDevelopment
export const isStaging = import.meta.env.MODE === 'staging'

// API configuration
export const apiConfig = {
  baseURL: env.VITE_API_BASE_URL,
  timeout: Number(env.VITE_API_TIMEOUT),
}

// App configuration
export const appConfig = {
  title: env.VITE_APP_TITLE,
  version: env.VITE_APP_VERSION,
  description: env.VITE_APP_DESCRIPTION,
}

// Feature flags
export const features = {
  analytics: env.VITE_ENABLE_ANALYTICS,
  errorReporting: env.VITE_ENABLE_ERROR_REPORTING,
  performanceMonitoring: env.VITE_ENABLE_PERFORMANCE_MONITORING,
  lazyLoading: env.VITE_ENABLE_LAZY_LOADING,
  codeSplitting: env.VITE_ENABLE_CODE_SPLITTING,
  compression: env.VITE_ENABLE_COMPRESSION,
}

// Authentication configuration
export const auth = {
  required: env.VITE_AUTH_REQUIRED,
  provider: env.VITE_AUTH_PROVIDER,
  domain: env.VITE_AUTH_DOMAIN,
}

// File upload configuration
export const fileUpload = {
  maxSize: Number(env.VITE_MAX_FILE_SIZE),
  allowedTypes: env.VITE_ALLOWED_FILE_TYPES.split(','),
}

// Monitoring configuration
export const monitoring = {
  sentryDSN: env.VITE_SENTRY_DSN,
  googleAnalyticsId: env.VITE_GOOGLE_ANALYTICS_ID,
}
