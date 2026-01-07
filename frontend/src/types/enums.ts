export enum ResumeStatus {
  NOT_APPLIED = 'not_applied',
  APPLIED = 'applied',
  ANSWERED = 'answered',
  REJECTED = 'rejected',
  INTERVIEW = 'interview'
}

export enum ResumeFormat {
  PDF = 'pdf',
  DOCX = 'docx',
  MARKDOWN = 'markdown'
}

export enum TemplateType {
  MODERN = 'modern',
  CLASSIC = 'classic',
  PROFESSIONAL = 'professional',
  CREATIVE = 'creative',
  MINIMAL = 'minimal'
}

export enum FileType {
  PDF = 'application/pdf',
  DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  MARKDOWN = 'text/markdown',
  TXT = 'text/plain'
}
