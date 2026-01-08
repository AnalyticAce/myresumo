import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useOptimizationStore } from '../optimizationStore'
import { act } from 'react'

// Mock react-dom for act
vi.mock('react-dom', async () => {
  const actual = await vi.importActual('react-dom')
  return {
    ...actual,
    act: vi.fn((callback) => callback()),
  }
})

describe('Optimization Store', () => {
  beforeEach(() => {
    // Reset store before each test
    const { reset } = useOptimizationStore.getState()
    act(() => {
      reset()
    })
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = useOptimizationStore.getState()
      
      expect(state.step).toBe(1)
      expect(state.request).toEqual({})
      expect(state.isProcessing).toBe(false)
      expect(state.analysis).toBeUndefined()
      expect(state.result).toBeUndefined()
      expect(state.error).toBeUndefined()
    })
  })

  describe('setCurrentStep', () => {
    it('should update current step', () => {
      const { setCurrentStep } = useOptimizationStore.getState()
      
      act(() => {
        setCurrentStep(2)
      })
      
      const state = useOptimizationStore.getState()
      expect(state.step).toBe(2)
    })

    it('should handle valid steps only', () => {
      const { setCurrentStep } = useOptimizationStore.getState()
      
      act(() => {
        setCurrentStep(3)
      })
      
      const state = useOptimizationStore.getState()
      expect(state.step).toBe(3)
    })
  })

  describe('setRequest', () => {
    it('should update request with partial data', () => {
      const { setRequest } = useOptimizationStore.getState()
      
      act(() => {
        setRequest({ sourceType: 'upload' })
      })
      
      let state = useOptimizationStore.getState()
      expect(state.request).toEqual({ sourceType: 'upload' })

      act(() => {
        setRequest({ company: 'Test Company' })
      })
      
      state = useOptimizationStore.getState()
      expect(state.request).toEqual({ 
        sourceType: 'upload', 
        company: 'Test Company' 
      })
    })

    it('should merge with existing request data', () => {
      const { setRequest } = useOptimizationStore.getState()
      
      act(() => {
        setRequest({ sourceType: 'upload', company: 'Test Company' })
        setRequest({ position: 'Software Engineer' })
      })
      
      const state = useOptimizationStore.getState()
      expect(state.request).toEqual({
        sourceType: 'upload',
        company: 'Test Company',
        position: 'Software Engineer'
      })
    })
  })

  describe('setAnalysis', () => {
    it('should set analysis result', () => {
      const { setAnalysis } = useOptimizationStore.getState()
      const mockAnalysis = {
        atsScore: 85,
        matchedSkills: ['React', 'TypeScript'],
        missingSkills: ['Python'],
        recommendations: []
      }
      
      act(() => {
        setAnalysis(mockAnalysis)
      })
      
      const state = useOptimizationStore.getState()
      expect(state.analysis).toEqual(mockAnalysis)
    })

    it('should clear analysis when undefined', () => {
      const { setAnalysis } = useOptimizationStore.getState()
      const mockAnalysis = {
        atsScore: 85,
        matchedSkills: ['React'],
        missingSkills: [],
        recommendations: []
      }
      
      act(() => {
        setAnalysis(mockAnalysis)
      })
      
      let state = useOptimizationStore.getState()
      expect(state.analysis).toEqual(mockAnalysis)

      act(() => {
        setAnalysis(undefined)
      })
      
      state = useOptimizationStore.getState()
      expect(state.analysis).toBeUndefined()
    })
  })

  describe('setResult', () => {
    it('should set optimization result', () => {
      const { setResult } = useOptimizationStore.getState()
      const mockResult = {
        resumeId: '123',
        improvements: ['Added skills section'],
        optimizedResumeUrl: 'http://example.com/resume.pdf',
        analysisResult: {
          atsScore: 90,
          matchedSkills: ['React'],
          missingSkills: [],
          recommendations: []
        }
      }
      
      act(() => {
        setResult(mockResult)
      })
      
      const state = useOptimizationStore.getState()
      expect(state.result).toEqual(mockResult)
    })
  })

  describe('setProcessing', () => {
    it('should set processing state', () => {
      const { setProcessing } = useOptimizationStore.getState()
      
      act(() => {
        setProcessing(true)
      })
      
      let state = useOptimizationStore.getState()
      expect(state.isProcessing).toBe(true)

      act(() => {
        setProcessing(false)
      })
      
      state = useOptimizationStore.getState()
      expect(state.isProcessing).toBe(false)
    })
  })

  describe('setError', () => {
    it('should set error message', () => {
      const { setError } = useOptimizationStore.getState()
      
      act(() => {
        setError('Something went wrong')
      })
      
      let state = useOptimizationStore.getState()
      expect(state.error).toBe('Something went wrong')

      act(() => {
        setError(undefined)
      })
      
      state = useOptimizationStore.getState()
      expect(state.error).toBeUndefined()
    })
  })

  describe('reset', () => {
    it('should reset store to initial state', () => {
      const { setRequest, setAnalysis, setResult, setProcessing, setError, reset } = useOptimizationStore.getState()
      
      act(() => {
        setRequest({ sourceType: 'upload' })
        setAnalysis({ atsScore: 85, matchedSkills: [], missingSkills: [], recommendations: [] })
        setResult({ resumeId: '123', improvements: [], optimizedResumeUrl: '', analysisResult: { atsScore: 85, matchedSkills: [], missingSkills: [], recommendations: [] } })
        setProcessing(true)
        setError('Error')
      })
      
      let state = useOptimizationStore.getState()
      expect(state.request).toEqual({ sourceType: 'upload' })
      expect(state.analysis).toBeDefined()
      expect(state.result).toBeDefined()
      expect(state.isProcessing).toBe(true)
      expect(state.error).toBe('Error')

      act(() => {
        reset()
      })
      
      state = useOptimizationStore.getState()
      expect(state.step).toBe(1)
      expect(state.request).toEqual({})
      expect(state.isProcessing).toBe(false)
      expect(state.analysis).toBeUndefined()
      expect(state.result).toBeUndefined()
      expect(state.error).toBeUndefined()
    })
  })
})
