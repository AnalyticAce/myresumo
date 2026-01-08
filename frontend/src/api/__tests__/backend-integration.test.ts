import { describe, it, expect, vi, beforeEach } from 'vitest'
import { apiClient } from '../client'
import { resumesAPI } from '../resumes'
import { DashboardFilters } from '@/types/resume'

// Mock the API client
vi.mock('../client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('Backend Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Resumes API', () => {
    it('should get resumes with correct endpoint', async () => {
      const mockData = { data: [], total: 0, page: 1, pageSize: 20 }
      const mockFilters: DashboardFilters = {
        sortBy: 'createdAt',
        sortOrder: 'desc',
        search: '',
        status: undefined
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockData })

      const result = await resumesAPI.getResumes(mockFilters, 1, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/resume/user/demo-user', {
        params: { page: 1, pageSize: 20 },
      })
      expect(result).toEqual(mockData)
    })

    it('should get resume by ID with correct endpoint', async () => {
      const mockResume = { id: '123', title: 'Test Resume' }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResume })

      const result = await resumesAPI.getResume('123')

      expect(apiClient.get).toHaveBeenCalledWith('/resume/123')
      expect(result).toEqual(mockResume)
    })

    it('should update resume status with correct endpoint', async () => {
      const mockResponse = { success: true }
      vi.mocked(apiClient.put).mockResolvedValue({ data: mockResponse })

      const result = await resumesAPI.updateStatus('123', 'applied')

      expect(apiClient.put).toHaveBeenCalledWith('/resume/123/status/applied')
      expect(result).toEqual(mockResponse)
    })

    it('should delete resume with correct endpoint', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({})

      await resumesAPI.deleteResume('123')

      expect(apiClient.delete).toHaveBeenCalledWith('/resume/123')
    })

    it('should download resume with correct endpoint', async () => {
      const mockBlob = new Blob()
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockBlob })

      const result = await resumesAPI.downloadResume('123')

      expect(apiClient.get).toHaveBeenCalledWith('/resume/123/download', {
        responseType: 'blob',
      })
      expect(result).toEqual(mockBlob)
    })

    it('should create resume with correct endpoint', async () => {
      const mockResponse = { id: '123', message: 'Resume created' }
      const formData = new FormData()
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await resumesAPI.createResume(formData)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/resume',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      expect(result).toEqual(mockResponse)
    })

    it('should optimize resume with correct endpoint', async () => {
      const mockResponse = { optimized_resume: '...', score: 85 }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await resumesAPI.optimizeResume(
        '123',
        'Job description',
        'Company',
        'Role'
      )

      expect(apiClient.post).toHaveBeenCalledWith('/resume/123/optimize', {
        job_description: 'Job description',
        target_company: 'Company',
        target_role: 'Role',
      })
      expect(result).toEqual(mockResponse)
    })

    it('should score resume with correct endpoint', async () => {
      const mockResponse = { score: 85, analysis: '...' }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await resumesAPI.scoreResume('123', 'Job description')

      expect(apiClient.post).toHaveBeenCalledWith('/resume/123/score', {
        job_description: 'Job description',
      })
      expect(result).toEqual(mockResponse)
    })

    it('should get templates with correct endpoint', async () => {
      const mockTemplates = [{ name: 'Modern', file: 'modern.typ' }]
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockTemplates })

      const result = await resumesAPI.getTemplates()

      expect(apiClient.get).toHaveBeenCalledWith('/resume/templates')
      expect(result).toEqual(mockTemplates)
    })
  })
})
