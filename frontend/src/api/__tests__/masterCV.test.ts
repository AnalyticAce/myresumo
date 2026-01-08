import { describe, it, expect, vi, beforeEach } from 'vitest'
import { masterCVAPI } from '../masterCV'
import { apiClient } from '../client'

// Mock API client
vi.mock('../client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('Master CV API Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAll', () => {
    it('should get all master CVs with correct endpoint', async () => {
      const mockResponse = [
        { id: '1', name: 'My Master CV 2024', createdAt: '2024-01-01' },
        { id: '2', name: 'Technical Resume', createdAt: '2024-01-02' }
      ]
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await masterCVAPI.getAll()

      expect(apiClient.get).toHaveBeenCalledWith('/master-cv')
      expect(result).toEqual(mockResponse)
    })

    it('should handle getAll errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'))

      await expect(masterCVAPI.getAll()).rejects.toThrow('Network error')
    })
  })

  describe('upload', () => {
    it('should upload master CV with correct endpoint', async () => {
      const mockResponse = { id: '123', message: 'Master CV uploaded successfully' }
      const testFile = new File(['test'], 'master-cv.pdf')
      
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await masterCVAPI.upload(testFile)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/resume/master-cv',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle upload errors', async () => {
      const testFile = new File(['test'], 'master-cv.pdf')
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Upload failed'))

      await expect(masterCVAPI.upload(testFile)).rejects.toThrow('Upload failed')
    })
  })

  describe('delete', () => {
    it('should delete master CV with correct endpoint', async () => {
      const mockResponse = { success: true }
      vi.mocked(apiClient.delete).mockResolvedValue({ data: mockResponse })

      const result = await masterCVAPI.delete('123')

      expect(apiClient.delete).toHaveBeenCalledWith('/master-cv/123')
      expect(result).toEqual(mockResponse)
    })

    it('should handle delete errors', async () => {
      vi.mocked(apiClient.delete).mockRejectedValue(new Error('Delete failed'))

      await expect(masterCVAPI.delete('123')).rejects.toThrow('Delete failed')
    })
  })

  describe('getById', () => {
    it('should get master CV by ID with correct endpoint', async () => {
      const mockResponse = { 
        id: '123', 
        name: 'My Master CV', 
        content: 'Resume content here...' 
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await masterCVAPI.getById('123')

      expect(apiClient.get).toHaveBeenCalledWith('/master-cv/123')
      expect(result).toEqual(mockResponse)
    })

    it('should handle getById errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Not found'))

      await expect(masterCVAPI.getById('123')).rejects.toThrow('Not found')
    })
  })

  describe('download', () => {
    it('should download master CV with correct endpoint', async () => {
      const mockBlob = new Blob(['test content'], { type: 'application/pdf' })
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockBlob })

      const result = await masterCVAPI.download('123')

      expect(apiClient.get).toHaveBeenCalledWith('/master-cv/123/download', {
        responseType: 'blob',
      })
      expect(result).toEqual(mockBlob)
    })

    it('should handle download errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Download failed'))

      await expect(masterCVAPI.download('123')).rejects.toThrow('Download failed')
    })
  })
})
