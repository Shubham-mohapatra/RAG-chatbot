'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Send, 
  Upload, 
  FileText, 
  Trash2, 
  MessageSquare, 
  Settings,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from '@/components/ui/icons'
import { chatAPI, type ChatMessage, type DocumentInfo, type ChatResponse } from '@/lib/api'
import DocumentManager from '@/components/DocumentManager'
import SimpleMarkdown from '@/components/SimpleMarkdown'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [selectedModel, setSelectedModel] = useState<'gemini-1.5-flash' | 'gemini-2.0-flash-exp'>('gemini-2.0-flash-exp')
  const [showDocuments, setShowDocuments] = useState(false)
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'unknown'>('unknown')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    // Generate session ID on component mount
    setSessionId(crypto.randomUUID())
    checkHealth()
    loadDocuments()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkHealth = async () => {
    try {
      const health = await chatAPI.healthCheck()
      setHealthStatus(health.status === 'healthy' ? 'healthy' : 'unhealthy')
    } catch (error) {
      setHealthStatus('unhealthy')
    }
  }

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

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      content: inputValue,
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const chatMessage: ChatMessage = {
        question: inputValue,
        session_id: sessionId,
        model: selectedModel
      }

      const response: ChatResponse = await chatAPI.sendMessage(chatMessage)

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: response.answer,
        role: 'assistant',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      console.error('Chat error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
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
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-semibold text-gray-900">RAG Chatbot</h1>
          </div>
          
          {/* Health Status */}
          <div className="flex items-center gap-2 text-sm">
            {healthStatus === 'healthy' ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : healthStatus === 'unhealthy' ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <RefreshCw className="h-4 w-4 text-gray-400 animate-spin" />
            )}
            <span className={`font-medium ${
              healthStatus === 'healthy' ? 'text-green-600' : 
              healthStatus === 'unhealthy' ? 'text-red-600' : 'text-gray-500'
            }`}>
              {healthStatus === 'healthy' ? 'Connected' : 
               healthStatus === 'unhealthy' ? 'Disconnected' : 'Checking...'}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={checkHealth}
              className="ml-auto h-6 w-6 p-0"
            >
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Model Selection */}
        <div className="p-4 border-b border-gray-200">
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            AI Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value as 'gemini-1.5-flash' | 'gemini-2.0-flash-exp')}
            className="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
            <option value="gemini-2.0-flash-exp">Gemini 2.5 Flash (Latest)</option>
          </select>
        </div>

        {/* Documents Section */}
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-gray-700">Documents</h2>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={loadDocuments}
                  disabled={isLoadingDocs}
                  className="h-6 w-6 p-0"
                >
                  <RefreshCw className={`h-3 w-3 ${isLoadingDocs ? 'animate-spin' : ''}`} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowDocuments(!showDocuments)}
                  className="h-6 w-6 p-0"
                >
                  <Settings className="h-3 w-3" />
                </Button>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              {documents.length} documents indexed
            </div>
          </div>

          {/* Document List */}
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-2">
              {documents.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500">No documents uploaded</p>
                  <p className="text-xs text-gray-400 mt-1">Upload documents to start chatting</p>
                </div>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-start gap-2">
                      <FileText className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-900 truncate">
                          {doc.filename}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500">
                            {formatFileSize(doc.file_size)}
                          </span>
                          <span className="text-xs text-gray-400">•</span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(doc.upload_timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Upload Section */}
        <div className="p-4 border-t border-gray-200">
          <DocumentManager onDocumentChange={loadDocuments} />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <MessageSquare className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-700 mb-2">
                  Welcome to RAG Chatbot
                </h2>
                <p className="text-gray-500 mb-4">
                  Upload documents and start asking questions to get AI-powered answers based on your content.
                </p>
                <div className="text-sm text-gray-400">
                  <p>• Upload PDF, DOCX, or HTML files</p>
                  <p>• Ask questions about your documents</p>
                  <p>• Get detailed, contextual responses</p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <Card
                    className={`max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white border-blue-500'
                        : 'bg-white border-gray-200'
                    }`}
                  >
                    <CardContent className="p-0">
                      {message.role === 'assistant' ? (
                        <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-lg">
                          {/* AI Response Header */}
                          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-white/50 rounded-t-lg">
                            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">AI</span>
                            </div>
                            <span className="text-sm font-medium text-gray-700">
                              {selectedModel.includes('2.0') ? 'Gemini 2.5 Flash' : 'Gemini 1.5 Flash'}
                            </span>
                            <div className="ml-auto text-xs text-gray-500">
                              {message.timestamp.toLocaleTimeString()}
                            </div>
                          </div>
                          
                          {/* AI Response Content */}
                          <div className="px-4 py-4">
                            <SimpleMarkdown>{message.content}</SimpleMarkdown>
                          </div>
                          
                          {/* AI Response Footer */}
                          <div className="px-4 py-2 bg-white/30 border-t border-gray-100 rounded-b-lg">
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <span className="flex items-center gap-1">
                                <span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
                                Response generated
                              </span>
                              <div className="flex items-center gap-3">
                                <button className="hover:text-blue-600 transition-colors flex items-center gap-1">
                                  <span>👍</span>
                                  <span>Helpful</span>
                                </button>
                                <button className="hover:text-red-600 transition-colors flex items-center gap-1">
                                  <span>👎</span>
                                  <span>Not helpful</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="p-4">
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          <div className="mt-2 text-xs opacity-70">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <Card className="bg-gradient-to-br from-gray-50 to-blue-50/30 border-gray-200 max-w-[80%]">
                  <CardContent className="p-0">
                    {/* Loading Header */}
                    <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-white/50 rounded-t-lg">
                      <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-bold">AI</span>
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {selectedModel.includes('2.0') ? 'Gemini 2.5 Flash' : 'Gemini 1.5 Flash'}
                      </span>
                      <div className="ml-auto">
                        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    </div>
                    
                    {/* Loading Content */}
                    <div className="px-4 py-6">
                      <div className="flex items-center gap-3">
                        <div className="flex space-x-1">
                          <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-bounce"></div>
                          <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-bounce delay-100"></div>
                          <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-bounce delay-200"></div>
                        </div>
                        <div className="space-y-1">
                          <div className="text-sm font-medium text-gray-700">AI is analyzing your documents...</div>
                          <div className="text-xs text-gray-500">Processing with advanced AI capabilities</div>
                        </div>
                      </div>
                      
                      {/* Loading Animation Bars */}
                      <div className="mt-4 space-y-2">
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-pulse w-3/4"></div>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-pulse w-1/2 delay-75"></div>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-pulse w-2/3 delay-150"></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask a question about your documents..."
                  className="min-h-[60px] resize-none pr-12"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="sm"
                  className="absolute bottom-2 right-2 h-8 w-8 p-0"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="mt-2 text-xs text-gray-500 text-center">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>

      {/* Document Manager Modal */}
      {showDocuments && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] m-4">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Document Management</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowDocuments(false)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <DocumentManager onDocumentChange={loadDocuments} detailed />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
