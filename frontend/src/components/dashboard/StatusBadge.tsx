import { Badge } from '@/components/ui/badge'
import { ResumeStatus } from '@/types/enums'

interface StatusBadgeProps {
  status: ResumeStatus
}

const statusConfig = {
  [ResumeStatus.NOT_APPLIED]: {
    label: 'Not Applied',
    variant: 'secondary' as const,
    className: 'bg-gray-500 hover:bg-gray-600',
  },
  [ResumeStatus.APPLIED]: {
    label: 'Applied',
    variant: 'default' as const,
    className: 'bg-blue-500 hover:bg-blue-600',
  },
  [ResumeStatus.ANSWERED]: {
    label: 'Answered',
    variant: 'default' as const,
    className: 'bg-purple-500 hover:bg-purple-600',
  },
  [ResumeStatus.REJECTED]: {
    label: 'Rejected',
    variant: 'destructive' as const,
    className: 'bg-red-500 hover:bg-red-600',
  },
  [ResumeStatus.INTERVIEW]: {
    label: 'Interview',
    variant: 'default' as const,
    className: 'bg-green-500 hover:bg-green-600',
  },
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status]
  
  return (
    <Badge variant={config.variant} className={config.className}>
      {config.label}
    </Badge>
  )
}
