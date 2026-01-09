import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { toast } from 'sonner'
import { Resume, TemplateType, ResumeStatus, ResumeFormat } from '@/types/resume'
import { AnalysisResult, Recommendation } from '@/types/optimization'

// Mock components
import { ResumeCard } from '@/components/dashboard/ResumeCard'
import { FileUpload } from '@/components/optimization/FileUpload'
import { TemplateSelector } from '@/components/optimization/TemplateSelector'
import { ATSScoreDisplay } from '@/components/analysis/ATSScoreDisplay'
import { SkillsMatch } from '@/components/analysis/SkillsMatch'
import { RecommendationsList } from '@/components/analysis/RecommendationsList'

// Mock data
const mockResume: Resume = {
  id: '1',
  userId: 'demo-user',
  title: 'Senior Software Engineer Resume',
  status: ResumeStatus.NOT_APPLIED,
  createdAt: '2024-01-15T10:00:00Z',
  updatedAt: '2024-01-15T10:00:00Z',
  atsScore: 85,
  downloadUrl: '/resumes/senior-software-engineer.pdf',
  company: 'TechCorp',
  position: 'Senior Software Engineer',
  format: ResumeFormat.PDF
}

const mockAnalysis: AnalysisResult = {
  atsScore: 85,
  matchedSkills: ['React', 'TypeScript', 'Node.js'],
  missingSkills: ['Python', 'Docker'],
  recommendations: [
    {
      id: '1',
      category: 'skills',
      severity: 'high',
      message: 'Add more quantifiable achievements',
      suggestion: 'Include specific metrics and results'
    } as Recommendation
  ]
}

// Mock query client
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

describe('Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('ResumeCard', () => {
    it('renders resume information correctly', () => {
      const queryClient = createTestQueryClient()
      
      render(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <ResumeCard resume={mockResume} />
          </BrowserRouter>
        </QueryClientProvider>
      )

      expect(screen.getByText('Senior Software Engineer Resume')).toBeInTheDocument()
      expect(screen.getByText('85')).toBeInTheDocument()
    })

    it('handles download click', async () => {
      const mockDownload = vi.fn()
      vi.mocked(global).URL.createObjectURL = vi.fn()
      vi.mocked(global).URL.revokeObjectURL = vi.fn()

      const queryClient = createTestQueryClient()
      
      render(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <ResumeCard resume={mockResume} />
          </BrowserRouter>
        </QueryClientProvider>
      )

      const downloadButton = screen.getByRole('button', { name: /download resume/i })
      fireEvent.click(downloadButton)

      await waitFor(() => {
        expect(mockDownload).toHaveBeenCalledWith(mockResume.downloadUrl)
      })
    })

    it('handles delete click', async () => {
      const mockDelete = vi.fn()
      window.confirm = vi.fn(() => true)

      const queryClient = createTestQueryClient()
      
      render(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <ResumeCard resume={mockResume} />
          </BrowserRouter>
        </QueryClientProvider>
      )

      const deleteButton = screen.getByRole('button', { name: /delete resume/i })
      fireEvent.click(deleteButton)

      await waitFor(() => {
        expect(window.confirm).toHaveBeenCalledWith(
          'Are you sure you want to delete this resume?'
        )
        expect(mockDelete).toHaveBeenCalledWith(mockResume.id)
      })
    })
  })

  describe('FileUpload', () => {
    it('renders file upload area', () => {
      render(<FileUpload onFileSelect={vi.fn()} />)
      
      expect(screen.getByText(/drag and drop/i)).toBeInTheDocument()
      expect(screen.getByText(/choose file/i)).toBeInTheDocument()
    })

    it('handles file selection', async () => {
      const mockFileSelect = vi.fn()
      const file = new File(['test'], 'resume.pdf', { type: 'application/pdf' })
      
      render(<FileUpload onFileSelect={mockFileSelect} />)
      
      const input = screen.getByRole('button', { name: /choose file/i })
      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockFileSelect).toHaveBeenCalledWith(file)
      })
    })

    it('validates file types', async () => {
      const mockToast = vi.spyOn(toast, 'error')
      const invalidFile = new File(['test'], 'resume.txt', { type: 'text/plain' })
      
      render(<FileUpload onFileSelect={vi.fn()} />)
      
      const input = screen.getByRole('button', { name: /choose file/i })
      fireEvent.change(input, { target: { files: [invalidFile] } })

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith('Invalid file type. Please upload PDF, DOCX, DOC, TXT, or MD files.')
      })
    })
  })

  describe('TemplateSelector', () => {
    it('renders template options', () => {
      const mockSelect = vi.fn()
      
      render(<TemplateSelector selectedTemplate={TemplateType.MODERN} onTemplateSelect={mockSelect} />)
      
      expect(screen.getByText('Modern')).toBeInTheDocument()
      expect(screen.getByText('Professional')).toBeInTheDocument()
      expect(screen.getByText('Creative')).toBeInTheDocument()
    })

    it('handles template selection', async () => {
      const mockSelect = vi.fn()
      
      render(<TemplateSelector selectedTemplate={TemplateType.MODERN} onTemplateSelect={mockSelect} />)
      
      const professionalTemplate = screen.getByText('Professional')
      fireEvent.click(professionalTemplate)

      await waitFor(() => {
        expect(mockSelect).toHaveBeenCalledWith('professional')
      })
    })
  })

  describe('Analysis Components', () => {
    it('renders ATS score display', () => {
      render(<ATSScoreDisplay score={mockAnalysis.atsScore} />)
      
      expect(screen.getByText('85')).toBeInTheDocument()
      expect(screen.getByText('Good')).toBeInTheDocument()
    })

    it('renders skills match', () => {
      render(<SkillsMatch matchedSkills={mockAnalysis.matchedSkills} missingSkills={mockAnalysis.missingSkills} />)
      
      expect(screen.getByText('React')).toBeInTheDocument()
      expect(screen.getByText('TypeScript')).toBeInTheDocument()
      expect(screen.getByText('Python')).toBeInTheDocument()
    })

    it('renders recommendations', () => {
      render(<RecommendationsList recommendations={mockAnalysis.recommendations} />)
      
      expect(screen.getByText(/Add more quantifiable achievements/)).toBeInTheDocument()
    })
  })
})
