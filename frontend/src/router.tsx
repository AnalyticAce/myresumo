import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { OptimizePage } from '@/pages/OptimizePage'
import { AnalysisPage } from '@/pages/AnalysisPage'
import { ResultsPage } from '@/pages/ResultsPage'
import { MasterCVPage } from '@/pages/MasterCVPage'
import { CoverLetterPage } from '@/pages/CoverLetterPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <div>Welcome to PowerCV</div>,
  },
  {
    path: '/app',
    element: <AppLayout />,
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
    ],
  },
])
