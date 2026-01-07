import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, FileText, X } from 'lucide-react'
import { formatFileSize } from '@/utils/formatters'
import { FILE_TYPES, MAX_FILE_SIZE } from '@/utils/constants'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  selectedFile?: File | null
  accept?: string[]
  maxSize?: number
  className?: string
}

export function FileUpload({
  onFileSelect,
  selectedFile,
  accept = [FILE_TYPES.PDF, FILE_TYPES.DOCX],
  maxSize = MAX_FILE_SIZE,
  className = ''
}: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0])
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: accept.reduce((acc, type) => {
      acc[type] = [type]
      return acc
    }, {} as Record<string, string[]>),
    maxSize,
    multiple: false,
  })

  const handleRemoveFile = () => {
    onFileSelect(null as any)
  }

  const getErrorMessage = (error: string) => {
    if (error.includes('too large')) return 'File size must be less than 10MB'
    if (error.includes('file type')) return 'Only PDF and DOCX files are allowed'
    return error
  }

  return (
    <div className={className}>
      {!selectedFile ? (
        <Card>
          <CardContent className="p-6">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary hover:bg-muted/50'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Drag and drop your file here, or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  PDF or DOCX files, up to 10MB
                </p>
              </div>
              <Button type="button" variant="outline" className="mt-4">
                <Upload className="mr-2 h-4 w-4" />
                Choose File
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleRemoveFile}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {fileRejections.length > 0 && (
        <div className="mt-2">
          {fileRejections.map(({ file, errors }) => (
            <div key={file.name} className="text-sm text-destructive">
              {errors.map(error => (
                <p key={error.code}>{getErrorMessage(error.message)}</p>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
