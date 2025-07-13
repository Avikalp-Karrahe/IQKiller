// Feature Flags Configuration for IQKiller App
// This file manages feature flag definitions and utilities for both client and server-side tracking

export const FEATURE_FLAGS = {
  // Core Features
  PREMIUM_FEATURES_ENABLED: 'premium-features-enabled',
  AI_MODEL_VERSION: 'ai-model-version',
  QUESTION_GENERATION_V2: 'question-generation-v2',
  CUSTOM_COMPANY_RESEARCH: 'custom-company-research',
  ADVANCED_RESUME_PARSING: 'advanced-resume-parsing',
  
  // UI/UX Features
  ENHANCED_ANALYTICS: 'enhanced-analytics',
  DARK_MODE_ENABLED: 'dark-mode-enabled',
  STREAMING_ANALYSIS: 'streaming-analysis',
  
  // Experimental Features
  BETA_FEATURES: 'beta-features',
  A_B_TEST_VARIANT: 'ab-test-variant',
  NEW_ONBOARDING: 'new-onboarding'
} as const

export type FeatureFlag = typeof FEATURE_FLAGS[keyof typeof FEATURE_FLAGS]

// Default feature flag values
export const DEFAULT_FLAG_VALUES = {
  [FEATURE_FLAGS.PREMIUM_FEATURES_ENABLED]: true,
  [FEATURE_FLAGS.AI_MODEL_VERSION]: 'gpt-4',
  [FEATURE_FLAGS.QUESTION_GENERATION_V2]: true,
  [FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH]: true,
  [FEATURE_FLAGS.ADVANCED_RESUME_PARSING]: true,
  [FEATURE_FLAGS.ENHANCED_ANALYTICS]: true,
  [FEATURE_FLAGS.DARK_MODE_ENABLED]: true,
  [FEATURE_FLAGS.STREAMING_ANALYSIS]: true,
  [FEATURE_FLAGS.BETA_FEATURES]: false,
  [FEATURE_FLAGS.A_B_TEST_VARIANT]: 'control',
  [FEATURE_FLAGS.NEW_ONBOARDING]: false
}

// Client-side feature flag emission
export const emitFeatureFlagsToDOM = () => {
  if (typeof window !== 'undefined') {
    Object.entries(DEFAULT_FLAG_VALUES).forEach(([flag, value]) => {
      document.body.setAttribute(`data-flag-${flag}`, String(value))
    })
  }
}

// Server-side feature flag reporting helper
export const reportFeatureFlags = () => {
  // Note: In a real app, you would use the actual reportValue from 'flags' package
  // For now, we'll simulate the flag values
  const flags = { ...DEFAULT_FLAG_VALUES }
  
  // In a real implementation, you would call reportValue for each flag
  // Example:
  // import { reportValue } from 'flags'
  // Object.entries(flags).forEach(([flag, value]) => {
  //   reportValue(flag, value)
  // })
  
  return flags
}

// Helper to get feature flag arrays for different contexts
export const getFeatureFlagArrays = () => ({
  // Core tracking flags
  core: [
    FEATURE_FLAGS.PREMIUM_FEATURES_ENABLED,
    FEATURE_FLAGS.AI_MODEL_VERSION,
    FEATURE_FLAGS.ENHANCED_ANALYTICS
  ],
  
  // Resume processing flags
  resume: [
    FEATURE_FLAGS.ADVANCED_RESUME_PARSING,
    FEATURE_FLAGS.AI_MODEL_VERSION
  ],
  
  // Job analysis flags
  job: [
    FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH,
    FEATURE_FLAGS.AI_MODEL_VERSION
  ],
  
  // Question generation flags
  questions: [
    FEATURE_FLAGS.QUESTION_GENERATION_V2,
    FEATURE_FLAGS.AI_MODEL_VERSION
  ],
  
  // Premium features flags
  premium: [
    FEATURE_FLAGS.PREMIUM_FEATURES_ENABLED,
    FEATURE_FLAGS.QUESTION_GENERATION_V2,
    FEATURE_FLAGS.CUSTOM_COMPANY_RESEARCH,
    FEATURE_FLAGS.AI_MODEL_VERSION
  ],
  
  // UI/UX flags
  ui: [
    FEATURE_FLAGS.DARK_MODE_ENABLED,
    FEATURE_FLAGS.STREAMING_ANALYSIS,
    FEATURE_FLAGS.NEW_ONBOARDING
  ]
})

// Feature flag validation
export const validateFeatureFlag = (flag: string): flag is FeatureFlag => {
  return Object.values(FEATURE_FLAGS).includes(flag as FeatureFlag)
}

// Get current feature flag values (server-side)
export const getCurrentFeatureFlags = () => {
  return reportFeatureFlags()
}

// Feature flag utilities for analytics
export const createAnalyticsEventWithFlags = (
  eventName: string,
  eventData: Record<string, any>,
  flagContext: keyof ReturnType<typeof getFeatureFlagArrays>
) => {
  const flagArrays = getFeatureFlagArrays()
  const relevantFlags = flagArrays[flagContext] || flagArrays.core
  
  return {
    eventName,
    eventData: {
      ...eventData,
      timestamp: new Date().toISOString(),
      flagContext
    },
    flags: relevantFlags
  }
}

export default {
  FEATURE_FLAGS,
  DEFAULT_FLAG_VALUES,
  emitFeatureFlagsToDOM,
  reportFeatureFlags,
  getFeatureFlagArrays,
  validateFeatureFlag,
  getCurrentFeatureFlags,
  createAnalyticsEventWithFlags
} 