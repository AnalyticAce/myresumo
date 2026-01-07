import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'

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
        element: <div>Optimize Resume - Coming Soon</div>,
      },
      {
        path: 'master-cv',
        element: <div>Master CV Management - Coming Soon</div>,
      },
      {
        path: 'cover-letter',
        element: <div>Cover Letters - Coming Soon</div>,
      },
    ],
  },
])
