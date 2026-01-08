import { describe, it, expect, vi, beforeEach } from 'vitest'
import { optimizationAPI } from '../optimization'
import { OptimizationRequest } from '@/types/optimization'
import { TemplateType } from '@/types/enums'
import { apiClient } from '../client'

// Mock API client
vi.mock('../client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

describe('Optimization API Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('analyze', () => {
    it('should analyze resume with correct endpoint and payload', async () => {
      const mockResponse = {
        atsScore: 85,
        matchedSkills: ['React', 'TypeScript'],
        missingSkills: ['Python'],
        recommendations: []
      }
      
      const mockRequest: OptimizationRequest = {
        sourceType: 'upload',
        uploadedFile: new File(['test'], 'resume.pdf'),
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description here...',
        template: TemplateType.MODERN,
        generateCoverLetter: false
      }

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await optimizationAPI.analyze(mockRequest)

      expect(apiClient.post).toHaveBeenCalledWith('/optimize', {
        cv_text: '',
        jd_text: 'Job description here...',
        generate_cover_letter: false,
        template: 'modern'
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle analysis errors', async () => {
      const mockRequest: OptimizationRequest = {
        sourceType: 'upload',
        uploadedFile: new File(['test'], 'resume.pdf'),
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description here...',
        template: TemplateType.MODERN,
        generateCoverLetter: false
      }

      vi.mocked(apiClient.post).mockRejectedValue(new Error('Network error'))

      await expect(optimizationAPI.analyze(mockRequest)).rejects.toThrow('Network error')
    })
  })

  describe('optimize', () => {
    it('should optimize resume with correct endpoint and payload', async () => {
      const mockResponse = {
        resumeId: '123',
        improvements: ['Added skills section'],
        optimizedResumeUrl: 'http://example.com/resume.pdf',
        coverLetterUrl: 'http://example.com/cover.pdf',
        analysisResult: {
          atsScore: 90,
          matchedSkills: ['React', 'TypeScript'],
          missingSkills: [],
          recommendations: []
        }
      }
      
      const mockRequest: OptimizationRequest = {
        sourceType: 'upload',
        uploadedFile: new File(['test'], 'resume.pdf'),
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description here...',
        template: TemplateType.MODERN,
        generateCoverLetter: true
      }

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await optimizationAPI.optimize(mockRequest)

      expect(apiClient.post).toHaveBeenCalledWith('/optimize', {
        cv_text: '',
        jd_text: 'Job description here...',
        generate_cover_letter: true,
        template: 'modern'
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle optimization errors', async () => {
      const mockRequest: OptimizationRequest = {
        sourceType: 'upload',
        uploadedFile: new File(['test'], 'resume.pdf'),
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description here...',
        template: TemplateType.MODERN,
        generateCoverLetter: false
      }

      vi.mocked(apiClient.post).mockRejectedValue(new Error('API error'))

      await expect(optimizationAPI.optimize(mockRequest)).rejects.toThrow('API error')
    })
  })

  describe('getComprehensiveOptimization', () => {
    it('should call comprehensive optimization endpoint', async () => {
      const mockResponse = {
        analysis: {},
        optimization: {},
        recommendations: []
      }
      
      const mockRequest: OptimizationRequest = {
        sourceType: 'upload',
        uploadedFile: new File(['test'], 'resume.pdf'),
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description here...',
        template: TemplateType.MODERN,
        generateCoverLetter: false
      }

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await optimizationAPI.getComprehensiveOptimization(mockRequest)

      expect(apiClient.post).toHaveBeenCalledWith('/api/comprehensive-optimize', {
        cv_text: '',
        jd_text: 'Job description here...',
        generate_cover_letter: false,
        template: 'modern'
      })
      expect(result).toEqual(mockResponse)
    })
  })
})
