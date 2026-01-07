import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { LayoutDashboard, FileEdit, FileText, Mail } from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Optimize Resume', href: '/optimize', icon: FileEdit },
  { name: 'Master CVs', href: '/master-cv', icon: FileText },
  { name: 'Cover Letters', href: '/cover-letter', icon: Mail },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r bg-white">
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
