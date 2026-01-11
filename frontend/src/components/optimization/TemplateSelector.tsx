import { TemplateType } from '@/types/enums'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface TemplateSelectorProps {
  selectedTemplate?: TemplateType
  onTemplateSelect: (template: TemplateType) => void
  className?: string
}

const templates = [
  {
    id: TemplateType.MODERN,
    name: 'Modern',
    description: 'Clean and contemporary design with a focus on readability',
    preview: '',
    color: 'bg-blue-500',
  },
  {
    id: TemplateType.CLASSIC,
    name: 'Classic',
    description: 'Traditional format suitable for conservative industries',
    preview: '',
    color: 'bg-gray-500',
  },
  {
    id: TemplateType.PROFESSIONAL,
    name: 'Professional',
    description: 'Sophisticated design for experienced professionals',
    preview: '',
    color: 'bg-slate-600',
  },
  {
    id: TemplateType.CREATIVE,
    name: 'Creative',
    description: 'Eye-catching design for creative industries',
    preview: '',
    color: 'bg-purple-500',
  },
  {
    id: TemplateType.MINIMAL,
    name: 'Minimal',
    description: 'Simple and clean design with maximum whitespace',
    preview: '',
    color: 'bg-green-500',
  },
]

export function TemplateSelector({
  selectedTemplate,
  onTemplateSelect,
  className = ''
}: TemplateSelectorProps) {
  return (
    <div className={className}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => (
          <Card
            key={template.id}
            className={cn(
              'cursor-pointer transition-all hover:shadow-md',
              selectedTemplate === template.id
                ? 'ring-2 ring-primary border-primary'
                : 'hover:border-primary/50'
            )}
            onClick={() => onTemplateSelect(template.id)}
          >
            <CardContent className="p-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className={cn(
                    'w-12 h-12 rounded-lg flex items-center justify-center text-2xl',
                    template.color
                  )}>
                    {template.preview}
                  </div>
                  {selectedTemplate === template.id && (
                    <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full" />
                    </div>
                  )}
                </div>
                
                <div>
                  <h3 className="font-semibold">{template.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {template.description}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {selectedTemplate && (
        <div className="mt-4 p-3 bg-primary/10 rounded-lg">
          <p className="text-sm text-primary">
            <strong>Selected:</strong> {templates.find(t => t.id === selectedTemplate)?.name}
          </p>
        </div>
      )}
    </div>
  )
}
