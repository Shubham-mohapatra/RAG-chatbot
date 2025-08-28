# 🚀 RAG Chatbot Deployment Guide

## Render.com Deployment (Recommended) 🎨
### Option 1: Blueprint Deployment (One-Click)
1. **Create Render Account**: Go to [render.com](https://render.com)
2. **Deploy with Blueprint**:
   - Go to Dashboard → "Blueprints"
   - Click "New Blueprint Instance"
   - Connect to your GitHub repository
   - Render will detect `render.yaml` file
   - Add environment variable: `GOOGLE_API_KEY=your_actual_api_key`
   - Click "Apply" to deploy both backend and frontend
3. **Access Your App**: Use the generated URLs for both services

### Option 2: Manual Deployment
1. **Create Render Account**: Go to [render.com](https://render.com)
2. **Deploy Backend**:
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Configure service:
     - **Name**: `rag-chatbot-backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `GOOGLE_API_KEY=your_actual_api_key`
   - Click "Create Web Service"
3. **Deploy Frontend**:
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Configure service:
     - **Name**: `rag-chatbot-frontend`
     - **Root Directory**: `frontend`
     - **Runtime**: `Node`
     - **Build Command**: `npm install && npm run build`
     - **Start Command**: `npm start`
   - Add environment variable: `NEXT_PUBLIC_API_BASE_URL=your_backend_url`
   - Click "Create Web Service"

## Optimization for Render

### Using Optimized Dependencies

Render's free tier has limited memory, so you may need to optimize:

1. **Use Optimized Requirements**:
   - Update the build command in Render dashboard:
   ```
   pip install -r requirements-optimized.txt
   ```

2. **Use Quantized Models**:
   - Smaller models use less memory
   - See `quantized_models.py` for implementation

3. **Implement Lazy Loading**:
   - Only load heavy components when needed
   - See `optimization_utils.py`

4. **Tiered Document Processing**:
   - Optimize document handling
   - See `tiered_processing.py`

## 📋 Deployment Checklist

### Backend Setup ✅
- [ ] Set `GOOGLE_API_KEY` environment variable
- [ ] Verify `/health` endpoint works
- [ ] Test `/docs` API documentation
- [ ] Copy backend URL for frontend configuration

### Frontend Setup ✅
- [ ] Set `NEXT_PUBLIC_API_BASE_URL` to backend URL
- [ ] Test deployment and functionality
- [ ] Verify CORS is working between frontend and backend

### Environment Variables 🔐
**Backend:**
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `PORT`: Auto-set by Render

**Frontend:**
- `NEXT_PUBLIC_API_BASE_URL`: Your deployed backend URL

## 🎯 Quick Deploy Using Render CLI

You can also deploy using the Render CLI:

```bash
# Install Render CLI
npm install -g @renderinc/cli

# Login
render login

# Deploy using the render.yaml file
render blueprint launch
```

## 🔧 Post-Deployment Steps

1. **Update CORS**: Verify CORS origins include your frontend URL
2. **Test Integration**: Upload a document and test chat functionality
3. **Monitor Logs**: Check Render logs for any issues
4. **Custom Domain** (Optional): Add custom domain in Render settings

## ⚠️ Render Free Tier Considerations

1. **Sleep Mode**: Free tier services sleep after 15 minutes of inactivity
   - First request after sleep will take longer to respond
   - Consider upgrading to a paid plan for production use

2. **Ephemeral Storage**: Free tier has ephemeral disk storage
   - Uploaded files and vector DB will be lost on service restart
   - Solution: Use persistent disk (paid feature) or modify app for cloud storage

3. **Memory Limits**: Free tier has 512MB RAM
   - Use optimized dependencies and models
   - Implement lazy loading of components

## 📊 Expected Deployment Times
- **Backend**: 5-7 minutes (first deploy may take longer due to dependencies)
- **Frontend**: 2-3 minutes
- **Total Setup**: ~15 minutes

Your RAG chatbot will be publicly accessible and ready to use! 🎉
