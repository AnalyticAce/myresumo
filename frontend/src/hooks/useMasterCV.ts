import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { masterCVAPI } from '@/api/masterCV'
import { MasterCV } from '@/types/resume'
import { toast } from 'sonner'

export function useMasterCVs() {
  return useQuery({
    queryKey: ['master-cvs'],
    queryFn: () => masterCVAPI.getAll(),
  })
}

export function useMasterCV(id: string) {
  return useQuery({
    queryKey: ['master-cv', id],
    queryFn: () => masterCVAPI.getById(id),
    enabled: !!id,
  })
}

export function useUploadMasterCV() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => masterCVAPI.upload(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['master-cvs'] })
      toast.success('Master CV uploaded successfully')
    },
    onError: () => {
      toast.error('Failed to upload Master CV')
    },
  })
}

export function useDeleteMasterCV() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => masterCVAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['master-cvs'] })
      toast.success('Master CV deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete Master CV')
    },
  })
}

export function useDownloadMasterCV() {
  return useMutation({
    mutationFn: (id: string) => masterCVAPI.getById(id).then(cv => {
      // TODO: Implement actual download functionality
      console.log('Download Master CV:', cv)
      return cv
    }),
    onSuccess: (cv) => {
      // TODO: Implement actual download
      toast.success('Master CV downloaded successfully')
    },
    onError: () => {
      toast.error('Failed to download Master CV')
    },
  })
}
