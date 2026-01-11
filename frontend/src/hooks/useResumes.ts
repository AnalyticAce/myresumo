import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { resumesAPI } from '@/api/resumes'
import { DashboardFilters } from '@/types/resume'
import { toast } from 'sonner'

export function useResumes(filters: DashboardFilters, search?: string) {
  return useQuery({
    queryKey: ['resumes', filters, search],
    queryFn: () => resumesAPI.getResumes({ ...filters, search }),
  })
}

export function useResume(id: string) {
  return useQuery({
    queryKey: ['resume', id],
    queryFn: () => resumesAPI.getResume(id),
    enabled: !!id,
  })
}

export function useUpdateResumeStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      resumesAPI.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume status updated')
    },
    onError: () => {
      toast.error('Failed to update resume status')
    },
  })
}

export function useDeleteResume() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => resumesAPI.deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete resume')
    },
  })
}

export function useDownloadResume() {
  return useMutation({
    mutationFn: (id: string) => resumesAPI.downloadResume(id),
    onSuccess: (blob, id) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `resume_optimized_${id}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Optimized resume downloaded successfully')
    },
    onError: () => {
      toast.error('Failed to download optimized resume')
    },
  })
}

export function useDownloadOriginalResume() {
  return useMutation({
    mutationFn: (id: string) => resumesAPI.downloadOriginalResume(id),
    onSuccess: (blob, id) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `resume_original_${id}`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Original resume downloaded successfully')
    },
    onError: () => {
      toast.error('Failed to download original resume')
    },
  })
}

export function useDownloadCoverLetter() {
  return useMutation({
    mutationFn: (id: string) => resumesAPI.downloadCoverLetter(id),
    onSuccess: (blob, id) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `cover_letter_${id}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Cover letter downloaded successfully')
    },
    onError: () => {
      toast.error('Failed to download cover letter')
    },
  })
}
