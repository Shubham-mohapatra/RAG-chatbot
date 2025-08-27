import React from 'react'

interface MarkdownProps {
  children: string
}

export default function SimpleMarkdown({ children }: MarkdownProps) {
  // Enhanced markdown parsing with better structure detection
  const parseMarkdown = (text: string) => {
    const lines = text.split('\n')
    const result: React.ReactNode[] = []
    let listItems: React.ReactNode[] = []
    let inList = false
    
    const flushList = (index: number) => {
      if (listItems.length > 0) {
        result.push(
          <ul key={`list-${index}`} className="mb-4 space-y-2 ml-4">
            {listItems}
          </ul>
        )
        listItems = []
      }
      inList = false
    }
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()
      
      // Handle different markdown elements
      if (line.startsWith('# ')) {
        flushList(i)
        result.push(
          <div key={i} className="mb-6 pb-2 border-b border-blue-100">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span className="w-1 h-8 bg-gradient-to-b from-blue-500 to-blue-600 rounded-full"></span>
              {line.slice(2)}
            </h1>
          </div>
        )
      } else if (line.startsWith('## ')) {
        flushList(i)
        result.push(
          <div key={i} className="mb-4 mt-6">
            <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              {line.slice(3)}
            </h2>
          </div>
        )
      } else if (line.startsWith('### ')) {
        flushList(i)
        result.push(
          <h3 key={i} className="text-lg font-medium text-gray-700 mt-4 mb-2 flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
            {line.slice(4)}
          </h3>
        )
      } else if (line.startsWith('- ') || line.startsWith('• ')) {
        inList = true
        const content = line.slice(2)
        listItems.push(
          <li key={i} className="flex items-start gap-2 text-gray-700">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
            <span>{formatInlineText(content)}</span>
          </li>
        )
      } else if (line.match(/^\d+\./)) {
        flushList(i)
        const content = line.replace(/^\d+\./, '').trim()
        result.push(
          <div key={i} className="flex items-start gap-3 mb-2">
            <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-sm font-medium min-w-[24px] text-center">
              {line.match(/^\d+/)?.[0]}
            </span>
            <span className="text-gray-700">{formatInlineText(content)}</span>
          </div>
        )
      } else if (line.startsWith('**') && line.endsWith('**') && line.length > 4) {
        flushList(i)
        result.push(
          <div key={i} className="bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-blue-500 p-4 my-4 rounded-r-lg">
            <div className="font-semibold text-gray-800">
              {line.slice(2, -2)}
            </div>
          </div>
        )
      } else if (line.trim()) {
        if (!inList) {
          result.push(
            <p key={i} className="mb-3 text-gray-700 leading-relaxed">
              {formatInlineText(line)}
            </p>
          )
        }
      } else {
        flushList(i)
        if (result.length > 0) {
          result.push(<div key={i} className="h-2"></div>)
        }
      }
    }
    
    // Flush any remaining list items
    flushList(lines.length)
    
    return result
  }
  
  // Enhanced inline text formatting
  const formatInlineText = (text: string): React.ReactNode => {
    // Handle bold text
    const boldRegex = /\*\*(.*?)\*\*/g
    const parts = text.split(boldRegex)
    
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        return <strong key={index} className="font-semibold text-gray-900">{part}</strong>
      }
      
      // Handle inline code
      const codeRegex = /`(.*?)`/g
      const codeParts = part.split(codeRegex)
      
      return codeParts.map((codePart, codeIndex) => {
        if (codeIndex % 2 === 1) {
          return (
            <code key={`${index}-${codeIndex}`} className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800">
              {codePart}
            </code>
          )
        }
        return codePart
      })
    })
  }
  
  return (
    <div className="max-w-none">
      <div className="space-y-1">
        {parseMarkdown(children)}
      </div>
    </div>
  )
}
