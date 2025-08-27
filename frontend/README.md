# RAG Chatbot Frontend

A modern, minimal UI for the RAG Chatbot built with Next.js and Tailwind CSS.

## Features

- 🎨 Clean, minimal interface with shadcn/ui design system
- 💬 Real-time chat interface with message history
- 📁 Document upload and management
- 🤖 AI model selection (Gemini 1.5 Flash/Pro)
- 📱 Responsive design
- 🔄 Health status monitoring
- ⚡ Fast and optimized

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Custom UI Components** - Based on shadcn/ui principles
- **Axios** - API communication

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   Create `.env.local` file (already created):
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Access the Application**
   Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Start the Backend**: Make sure your RAG chatbot backend is running on port 8000
2. **Upload Documents**: Use the sidebar to upload PDF, DOCX, or HTML files
3. **Chat**: Ask questions about your uploaded documents
4. **Manage**: View and delete documents as needed

## API Integration

The frontend connects to your FastAPI backend at `http://localhost:8000` with the following endpoints:

- `POST /chat` - Send chat messages
- `POST /upload-doc` - Upload documents
- `GET /list-docs` - List uploaded documents
- `POST /delete-doc` - Delete documents
- `GET /health` - Health check

## Development

- **Build for Production**: `npm run build`
- **Start Production Server**: `npm start`
- **Lint**: `npm run lint`

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Main chat interface
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── ui/              # Base UI components
│   │   ├── DocumentManager.tsx
│   │   └── SimpleMarkdown.tsx
│   └── lib/                 # Utilities
│       ├── api.ts           # API functions
│       └── utils.ts         # Helper functions
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.mjs
```

## Customization

- **Styling**: Modify `tailwind.config.ts` and `globals.css`
- **API Endpoint**: Update `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- **UI Components**: Customize components in `src/components/ui/`

## Troubleshooting

- **CORS Issues**: Ensure backend CORS settings include frontend URL
- **API Connection**: Verify backend is running and accessible
- **Build Errors**: Check TypeScript errors and dependencies
