import { ResumeStatus, ResumeFormat, TemplateType } from './enums'

export interface Resume {
  id: string
  userId: string
  company: string
  position: string
  status: ResumeStatus
  atsScore: number
  format: ResumeFormat
  sourceType: 'master_cv' | 'upload'
  sourceId?: string
  sourceName: string
  template: TemplateType
  hasCoverLetter: boolean
  createdAt: string
  updatedAt: string
  downloadUrl?: string
  coverLetterUrl?: string
}

export interface MasterCV {
  id: string
  userId: string
  filename: string
  originalFilename: string
  fileUrl: string
  uploadedAt: string
  usageCount: number
  lastUsed?: string
}

export interface DashboardFilters {
  status?: ResumeStatus
  sortBy: 'company' | 'position' | 'status' | 'atsScore' | 'createdAt'
  sortOrder: 'asc' | 'desc'
  search?: string
}
