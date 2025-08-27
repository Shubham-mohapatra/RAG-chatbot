# 🚀 RAG Chatbot Deployment Guide

## Backend Deployment Options

### Option 1: Railway (Recommended) 🚂
1. **Create Railway Account**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your GitHub repository
3. **Deploy Backend**:
   - Create new project from GitHub repo
   - Railway will auto-detect Python and use `Procfile`
   - Add environment variable: `GOOGLE_API_KEY=your_actual_api_key`
   - Deploy will start automatically
4. **Get Backend URL**: Copy the generated Railway URL (e.g., `https://rag-chatbot-backend-production.up.railway.app`)

### Option 2: Render 🎨
1. **Create Render Account**: Go to [render.com](https://render.com)
2. **Deploy Backend**:
   - Connect GitHub repository
   - Select "Web Service"
   - Use `render.yaml` configuration
   - Add environment variable: `GOOGLE_API_KEY=your_actual_api_key`
3. **Get Backend URL**: Copy the generated Render URL

### Option 3: Heroku 📦
1. **Create Heroku Account**: Go to [heroku.com](https://heroku.com)
2. **Install Heroku CLI**
3. **Deploy Commands**:
   ```bash
   cd rag-chatbot
   heroku create your-app-name-backend
   heroku config:set GOOGLE_API_KEY=your_actual_api_key
   git push heroku main
   ```

## Frontend Deployment Options

### Option 1: Vercel (Recommended) ⚡
1. **Create Vercel Account**: Go to [vercel.com](https://vercel.com)
2. **Connect GitHub**: Link your repository
3. **Deploy Frontend**:
   - Import your GitHub repository
   - Select `frontend` folder as root directory
   - Add environment variable: `NEXT_PUBLIC_API_BASE_URL=your_backend_url`
   - Deploy automatically
4. **Get Frontend URL**: Your app will be live at `https://your-app.vercel.app`

### Option 2: Netlify 🌐
1. **Create Netlify Account**: Go to [netlify.com](https://netlify.com)
2. **Deploy Frontend**:
   - Connect GitHub repository
   - Set build directory to `frontend`
   - Add environment variable: `NEXT_PUBLIC_API_BASE_URL=your_backend_url`
   - Deploy

## 📋 Deployment Checklist

### Backend Setup ✅
- [ ] Choose deployment platform (Railway/Render/Heroku)
- [ ] Set `GOOGLE_API_KEY` environment variable
- [ ] Verify `/health` endpoint works
- [ ] Test `/docs` API documentation
- [ ] Copy backend URL for frontend configuration

### Frontend Setup ✅
- [ ] Choose deployment platform (Vercel/Netlify)
- [ ] Set `NEXT_PUBLIC_API_BASE_URL` to backend URL
- [ ] Test deployment and functionality
- [ ] Verify CORS is working between frontend and backend

### Environment Variables 🔐
**Backend:**
- `GOOGLE_API_KEY`: Your Google AI Studio API key
- `PORT`: Auto-set by hosting platforms

**Frontend:**
- `NEXT_PUBLIC_API_BASE_URL`: Your deployed backend URL

## 🎯 Quick Deploy Commands

### Backend (Railway)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### Frontend (Vercel)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

## 🔧 Post-Deployment Steps

1. **Update CORS**: Update backend CORS origins with your frontend URL
2. **Test Integration**: Upload a document and test chat functionality
3. **Monitor Logs**: Check deployment logs for any issues
4. **Custom Domain** (Optional): Add custom domain in hosting platform settings

## 📱 Mobile Optimization
The frontend is already mobile-responsive with:
- Responsive design for all screen sizes
- Touch-friendly interface
- Mobile-optimized chat experience

## 🛡️ Security Notes
- API keys are securely stored as environment variables
- CORS is configured for your specific domains
- No sensitive data is exposed in frontend code
- All file uploads are handled securely

## 📊 Expected Deployment Times
- **Backend**: 3-5 minutes
- **Frontend**: 1-2 minutes
- **Total Setup**: ~10 minutes

Your RAG chatbot will be publicly accessible and ready to use! 🎉
