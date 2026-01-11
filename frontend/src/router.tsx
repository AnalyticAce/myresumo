import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { OptimizePage } from '@/pages/OptimizePage'
import { AnalysisPage } from '@/pages/AnalysisPage'
import { ResultsPage } from '@/pages/ResultsPage'
import { MasterCVPage } from '@/pages/MasterCVPage'
import { CoverLetterPage } from '@/pages/CoverLetterPage'
import { ResumePreviewPage } from '@/pages/ResumePreviewPage'
import { ErrorBoundary } from '@/components/ErrorBoundary'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'optimize',
        element: <OptimizePage />,
      },
      {
        path: 'analysis',
        element: <AnalysisPage />,
      },
      {
        path: 'results',
        element: <ResultsPage />,
      },
      {
        path: 'master-cv',
        element: <MasterCVPage />,
      },
      {
        path: 'cover-letter',
        element: <CoverLetterPage />,
      },
      {
        path: 'resume/:id',
        element: <ResumePreviewPage />,
      },
    ],
  },
])
