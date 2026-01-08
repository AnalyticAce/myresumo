import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { OptimizePage } from '../OptimizePage'
import { useOptimizationStore } from '@/stores/optimizationStore'
import { optimizationAPI } from '@/api/optimization'
import { toast } from 'sonner'

// Mock dependencies
vi.mock('@/stores/optimizationStore')
vi.mock('@/api/optimization')
vi.mock('sonner')
vi.mock('@/components/optimization/FileUpload', () => ({
  FileUpload: vi.fn(({ onFileSelect, selectedFile }) => (
    <div data-testid="file-upload">
      <button onClick={() => onFileSelect(new File(['test'], 'resume.pdf'))}>
        Upload File
      </button>
      {selectedFile && <span data-testid="selected-file">{selectedFile.name}</span>}
    </div>
  ))
}))

vi.mock('@/components/optimization/TemplateSelector', () => ({
  TemplateSelector: vi.fn(({ selectedTemplate, onTemplateSelect }) => (
    <div data-testid="template-selector">
      <button onClick={() => onTemplateSelect('modern')}>Select Modern</button>
      {selectedTemplate && <span data-testid="selected-template">{selectedTemplate}</span>}
    </div>
  ))
}))

const MockedOptimizationStore = vi.mocked(useOptimizationStore)
const MockedOptimizationAPI = vi.mocked(optimizationAPI)
const MockedToast = vi.mocked(toast)

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('OptimizePage', () => {
  const mockSetRequest = vi.fn()
  const mockSetCurrentStep = vi.fn()
  const mockSetAnalysis = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    
    MockedOptimizationStore.mockReturnValue({
      request: {},
      setRequest: mockSetRequest,
      setCurrentStep: mockSetCurrentStep,
      setAnalysis: mockSetAnalysis,
      step: 1
    })
  })

  describe('initial render', () => {
    it('should render optimize page with correct title', () => {
      renderWithRouter(<OptimizePage />)
      
      expect(screen.getByText('Optimize Resume')).toBeInTheDocument()
      expect(screen.getByText('Create an ATS-optimized resume for your job application')).toBeInTheDocument()
    })

    it('should show step 1 content initially', () => {
      renderWithRouter(<OptimizePage />)
      
      expect(screen.getByText('Step 1: Select Source')).toBeInTheDocument()
      expect(screen.getByText('Choose resume source')).toBeInTheDocument()
    })

    it('should show back to dashboard button', () => {
      renderWithRouter(<OptimizePage />)
      
      expect(screen.getByText('Back to Dashboard')).toBeInTheDocument()
    })
  })

  describe('step navigation', () => {
    it('should go to next step when valid', () => {
      MockedOptimizationStore.mockReturnValue({
        request: { sourceType: 'upload' },
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 1
      })

      renderWithRouter(<OptimizePage />)
      
      const nextButton = screen.getByText('Next')
      fireEvent.click(nextButton)
      
      expect(mockSetCurrentStep).toHaveBeenCalledWith(2)
    })

    it('should disable next button when step is invalid', () => {
      MockedOptimizationStore.mockReturnValue({
        request: {},
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 1
      })

      renderWithRouter(<OptimizePage />)
      
      const nextButton = screen.getByText('Next')
      expect(nextButton).toBeDisabled()
    })

    it('should go to previous step', () => {
      MockedOptimizationStore.mockReturnValue({
        request: { sourceType: 'upload' },
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 2
      })

      renderWithRouter(<OptimizePage />)
      
      const previousButton = screen.getByText('Previous')
      fireEvent.click(previousButton)
      
      expect(mockSetCurrentStep).toHaveBeenCalledWith(1)
    })

    it('should disable previous button on step 1', () => {
      MockedOptimizationStore.mockReturnValue({
        request: {},
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 1
      })

      renderWithRouter(<OptimizePage />)
      
      const previousButton = screen.getByText('Previous')
      expect(previousButton).toBeDisabled()
    })
  })

  describe('form interactions', () => {
    it('should update request when source type changes', () => {
      renderWithRouter(<OptimizePage />)
      
      const select = screen.getByRole('combobox')
      fireEvent.change(select, { target: { value: 'upload' } })
      
      expect(mockSetRequest).toHaveBeenCalledWith(expect.objectContaining({
        sourceType: 'upload'
      }))
    })

    it('should update request when company changes', () => {
      MockedOptimizationStore.mockReturnValue({
        request: { sourceType: 'upload' },
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 2
      })

      renderWithRouter(<OptimizePage />)
      
      const companyInput = screen.getByPlaceholderText('e.g., Google, Microsoft, Amazon')
      fireEvent.change(companyInput, { target: { value: 'Test Company' } })
      
      expect(mockSetRequest).toHaveBeenCalledWith(expect.objectContaining({
        company: 'Test Company'
      }))
    })

    it('should update request when position changes', () => {
      MockedOptimizationStore.mockReturnValue({
        request: { sourceType: 'upload' },
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 2
      })

      renderWithRouter(<OptimizePage />)
      
      const positionInput = screen.getByPlaceholderText('e.g., Senior Software Engineer')
      fireEvent.change(positionInput, { target: { value: 'Software Engineer' } })
      
      expect(mockSetRequest).toHaveBeenCalledWith(expect.objectContaining({
        position: 'Software Engineer'
      }))
    })
  })

  describe('analysis submission', () => {
    it('should call optimization API when analyze button is clicked', async () => {
      const mockRequest = {
        sourceType: 'upload',
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description',
        template: 'modern',
        generateCoverLetter: false
      }

      const mockAnalysisResult = {
        atsScore: 85,
        matchedSkills: ['React'],
        missingSkills: [],
        recommendations: []
      }

      MockedOptimizationStore.mockReturnValue({
        request: mockRequest,
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 4
      })

      MockedOptimizationAPI.analyze.mockResolvedValue(mockAnalysisResult)

      renderWithRouter(<OptimizePage />)
      
      const analyzeButton = screen.getByText('Analyze & Optimize')
      fireEvent.click(analyzeButton)

      await waitFor(() => {
        expect(MockedOptimizationAPI.analyze).toHaveBeenCalledWith(mockRequest)
      })
    })

    it('should show success toast and navigate on successful analysis', async () => {
      const mockRequest = {
        sourceType: 'upload',
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description',
        template: 'modern',
        generateCoverLetter: false
      }

      const mockAnalysisResult = {
        atsScore: 85,
        matchedSkills: ['React'],
        missingSkills: [],
        recommendations: []
      }

      MockedOptimizationStore.mockReturnValue({
        request: mockRequest,
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 4
      })

      MockedOptimizationAPI.analyze.mockResolvedValue(mockAnalysisResult)

      renderWithRouter(<OptimizePage />)
      
      const analyzeButton = screen.getByText('Analyze & Optimize')
      fireEvent.click(analyzeButton)

      await waitFor(() => {
        expect(mockSetAnalysis).toHaveBeenCalledWith(mockAnalysisResult)
        expect(MockedToast.success).toHaveBeenCalledWith('Analysis completed successfully!')
      })
    })

    it('should show error toast on failed analysis', async () => {
      const mockRequest = {
        sourceType: 'upload',
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description',
        template: 'modern',
        generateCoverLetter: false
      }

      MockedOptimizationStore.mockReturnValue({
        request: mockRequest,
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 4
      })

      MockedOptimizationAPI.analyze.mockRejectedValue(new Error('API Error'))

      renderWithRouter(<OptimizePage />)
      
      const analyzeButton = screen.getByText('Analyze & Optimize')
      fireEvent.click(analyzeButton)

      await waitFor(() => {
        expect(MockedToast.error).toHaveBeenCalledWith('Analysis failed. Please try again.')
      })
    })

    it('should show loading state during analysis', async () => {
      const mockRequest = {
        sourceType: 'upload',
        company: 'Test Company',
        position: 'Software Engineer',
        jobDescription: 'Job description',
        template: 'modern',
        generateCoverLetter: false
      }

      MockedOptimizationStore.mockReturnValue({
        request: mockRequest,
        setRequest: mockSetRequest,
        setCurrentStep: mockSetCurrentStep,
        setAnalysis: mockSetAnalysis,
        step: 4
      })

      MockedOptimizationAPI.analyze.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

      renderWithRouter(<OptimizePage />)
      
      const analyzeButton = screen.getByText('Analyze & Optimize')
      fireEvent.click(analyzeButton)

      expect(screen.getByText('Analyzing...')).toBeInTheDocument()
    })
  })
})
