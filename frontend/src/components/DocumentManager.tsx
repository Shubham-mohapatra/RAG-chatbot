'use client'

import React, { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Upload, 
  FileText, 
  Trash2, 
  X,
  CheckCircle,
  AlertCircle,
  Loader2
} from '@/components/ui/icons'
import { chatAPI, type DocumentInfo } from '@/lib/api'

interface DocumentManagerProps {
  onDocumentChange: () => void
  detailed?: boolean
}

export default function DocumentManager({ onDocumentChange, detailed = false }: DocumentManagerProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string>('')
  const [dragActive, setDragActive] = useState(false)
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  React.useEffect(() => {
    if (detailed) {
      loadDocuments()
    }
  }, [detailed])

  const loadDocuments = async () => {
    setIsLoadingDocs(true)
    try {
      const docs = await chatAPI.listDocuments()
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setIsLoadingDocs(false)
    }
  }

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    const file = files[0]
    
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.html']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedTypes.includes(fileExtension)) {
      setUploadStatus(`Error: File type ${fileExtension} not supported. Allowed: ${allowedTypes.join(', ')}`)
      return
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      setUploadStatus('Error: File too large. Maximum size is 10MB.')
      return
    }

    setIsUploading(true)
    setUploadStatus('Uploading and indexing document...')

    try {
      const response = await chatAPI.uploadDocument(file)
      setUploadStatus(`✅ Successfully uploaded: ${response.filename}`)
      onDocumentChange()
      
      if (detailed) {
        loadDocuments()
      }

      // Clear success message after 3 seconds
      setTimeout(() => setUploadStatus(''), 3000)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed'
      setUploadStatus(`❌ Error: ${errorMessage}`)
      
      // Clear error message after 5 seconds
      setTimeout(() => setUploadStatus(''), 5000)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDeleteDocument = async (fileId: number, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return
    }

    try {
      await chatAPI.deleteDocument(fileId)
      setUploadStatus(`✅ Successfully deleted: ${filename}`)
      onDocumentChange()
      
      if (detailed) {
        loadDocuments()
      }

      // Clear message after 3 seconds
      setTimeout(() => setUploadStatus(''), 3000)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Delete failed'
      setUploadStatus(`❌ Error: ${errorMessage}`)
      
      // Clear error message after 5 seconds
      setTimeout(() => setUploadStatus(''), 5000)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx,.html"
          onChange={(e) => handleFileUpload(e.target.files)}
          disabled={isUploading}
        />
        
        <div className="flex flex-col items-center gap-2">
          {isUploading ? (
            <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
          ) : (
            <Upload className="h-8 w-8 text-gray-400" />
          )}
          
          <div>
            <p className="text-sm font-medium text-gray-700">
              {isUploading ? 'Processing...' : 'Upload a document'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Drag and drop or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-600 hover:text-blue-700 underline"
                disabled={isUploading}
              >
                browse files
              </button>
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Supports: PDF, DOCX, HTML (max 10MB)
            </p>
          </div>
        </div>
      </div>

      {/* Status Message */}
      {uploadStatus && (
        <div className={`p-3 rounded-lg text-sm ${
          uploadStatus.startsWith('✅') 
            ? 'bg-green-50 text-green-700 border border-green-200'
            : uploadStatus.startsWith('❌')
            ? 'bg-red-50 text-red-700 border border-red-200'
            : 'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {uploadStatus}
        </div>
      )}

      {/* Document List (detailed view only) */}
      {detailed && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">
              Uploaded Documents ({documents.length})
            </h3>
            <Button
              onClick={loadDocuments}
              disabled={isLoadingDocs}
              className="h-6 w-6 p-0"
            >
              {isLoadingDocs ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                '🔄'
              )}
            </Button>
          </div>

          <div className="max-h-60 overflow-y-auto space-y-2">
            {documents.length === 0 ? (
              <div className="text-center py-6">
                <FileText className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No documents uploaded yet</p>
              </div>
            ) : (
              documents.map((doc) => (
                <Card key={doc.id} className="border border-gray-200">
                  <CardContent className="p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-2 flex-1 min-w-0">
                        <FileText className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {doc.filename}
                          </p>
                          <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                            <span>{formatFileSize(doc.file_size)}</span>
                            <span>•</span>
                            <span>{formatTimestamp(doc.upload_timestamp)}</span>
                          </div>
                        </div>
                      </div>
                      <Button
                        onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                        className="h-6 w-6 p-0 flex-shrink-0"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
