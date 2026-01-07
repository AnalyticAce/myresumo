import { z } from 'zod'

export const optimizationRequestSchema = z.object({
  sourceType: z.enum(['master_cv', 'upload']),
  sourceId: z.string().optional(),
  company: z.string().min(1, 'Company name is required'),
  position: z.string().min(1, 'Position is required'),
  jobDescription: z.string().min(50, 'Job description must be at least 50 characters'),
  template: z.enum(['modern', 'classic', 'professional', 'creative', 'minimal']),
  generateCoverLetter: z.boolean().default(false),
}).refine(
  (data) => {
    if (data.sourceType === 'upload') {
      return true // Will be validated separately for file presence
    }
    return !!data.sourceId
  },
  {
    message: 'Master CV selection is required when using master_cv source',
    path: ['sourceId'],
  }
)

export const masterCVUploadSchema = z.object({
  file: z.instanceof(File).refine(
    (file) => file.size <= 10 * 1024 * 1024, // 10MB
    'File size must be less than 10MB'
  ).refine(
    (file) => ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type),
    'Only PDF and DOCX files are allowed'
  ),
})

export const resumeFiltersSchema = z.object({
  status: z.enum(['not_applied', 'applied', 'answered', 'rejected', 'interview']).optional(),
  sortBy: z.enum(['company', 'position', 'status', 'atsScore', 'createdAt']),
  sortOrder: z.enum(['asc', 'desc']),
  search: z.string().optional(),
})

export type OptimizationRequestInput = z.infer<typeof optimizationRequestSchema>
export type MasterCVUploadInput = z.infer<typeof masterCVUploadSchema>
export type ResumeFiltersInput = z.infer<typeof resumeFiltersSchema>
