import { apiClient } from './client'
import { MasterCV } from '@/types/resume'
import { ApiResponse } from '@/types/api'

export const masterCVAPI = {
  getAll: async () => {
    const { data } = await apiClient.get<ApiResponse<MasterCV[]>>('/master-cvs')
    return data.data!
  },

  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await apiClient.post<ApiResponse<MasterCV>>(
      '/master-cvs/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return data.data!
  },

  delete: async (id: string) => {
    await apiClient.delete(`/master-cvs/${id}`)
  },

  getById: async (id: string) => {
    const { data } = await apiClient.get<ApiResponse<MasterCV>>(`/master-cvs/${id}`)
    return data.data!
  },
}
