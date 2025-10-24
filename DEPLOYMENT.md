# 🚀 RAG Chatbot Deployment Guide

Complete guide to deploy your RAG Chatbot to production.

---

## 📋 Pre-Deployment Checklist

- [ ] **Rotate API Key**: Get a new Google API key (old one was exposed)
  - Go to: https://makersuite.google.com/app/apikey
  - Create new key or rotate existing
- [ ] **Test locally**: Ensure backend runs on port 8080, frontend on 3000
- [ ] **Update CORS**: Add your production frontend URL to backend CORS settings
- [ ] **Environment variables**: Copy `.env.example` to `.env` and fill values

---

## 🎯 Deployment Options

### **Option A: Quick Deploy (Recommended for Beginners)**
- **Backend**: Railway or Render (Free tier available)
- **Frontend**: Vercel (Free tier, best for Next.js)
- **Time**: ~15 minutes
- **Cost**: Free tier available

### **Option B: Docker Deploy (For Advanced Users)**
- **Platform**: Any VPS (DigitalOcean, AWS EC2, Azure)
- **Method**: Docker + Docker Compose
- **Time**: ~30 minutes
- **Cost**: ~$5-10/month

### **Option C: Full Cloud Deploy**
- **Backend**: Google Cloud Run or AWS ECS
- **Frontend**: Vercel or AWS Amplify
- **Time**: ~45 minutes
- **Cost**: Pay-as-you-go

---

## 🚂 Option A: Railway Deployment (Easiest)

### **Backend on Railway**

1. **Create Railway Account**
   ```bash
   # Visit https://railway.app and sign up with GitHub
   ```

2. **Install Railway CLI** (Optional)
   ```powershell
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy Backend**
   - Go to https://railway.app/new
   - Click "Deploy from GitHub repo"
   - Select your `rag-chatbot` repository
   - Railway will auto-detect Python and use Dockerfile

4. **Set Environment Variables in Railway**
   - In Railway dashboard → Your Project → Variables tab
   - Add:
     ```
     GOOGLE_API_KEY=your_new_api_key_here
     PORT=8080
     ```

5. **Generate Domain**
   - In Railway dashboard → Settings → Generate Domain
   - Copy the URL (e.g., `https://rag-chatbot-production.up.railway.app`)

6. **Update Backend CORS** (in `main.py`)
   ```python
   # Add your Railway domain to CORS origins
   origins = [
       "http://localhost:3000",
       "https://your-frontend.vercel.app",  # Add after frontend deploy
   ]
   ```

### **Frontend on Vercel**

1. **Create Vercel Account**
   - Go to https://vercel.com and sign up with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Vercel auto-detects Next.js

3. **Configure Build Settings**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Set Environment Variables**
   - In Vercel → Project Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_BASE_URL=https://your-railway-backend-url.up.railway.app
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait ~2 minutes for build
   - Get your URL: `https://your-app.vercel.app`

6. **Update Backend CORS**
   - Go back to Railway → Environment Variables
   - Update to include Vercel URL

---

## 🐳 Option B: Docker Deployment

### **1. Build and Test Locally**

```powershell
# Navigate to project root
cd c:\Users\KIIT\Desktop\Projects\rag-chatbot

# Build Docker image
docker build -t rag-chatbot-backend .

# Test run (make sure .env exists with GOOGLE_API_KEY)
docker run -p 8080:8080 --env-file .env rag-chatbot-backend

# Or use docker-compose
docker-compose up -d
```

### **2. Deploy to DigitalOcean/AWS/Azure**

**DigitalOcean App Platform** (Easiest Docker Deploy):
1. Create account at https://www.digitalocean.com
2. Go to "App Platform" → "Create App"
3. Connect GitHub repository
4. Select "Dockerfile" as build method
5. Set environment variables:
   ```
   GOOGLE_API_KEY=your_key
   PORT=8080
   ```
6. Deploy and get URL

**AWS EC2 Manual Deploy**:
```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/Shubham-mohapatra/RAG-chatbot.git
cd RAG-chatbot

# Create .env file
nano .env
# Add: GOOGLE_API_KEY=your_key

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## ☁️ Option C: Google Cloud Run (Serverless)

### **Backend on Cloud Run**

1. **Install Google Cloud CLI**
   ```powershell
   # Download from: https://cloud.google.com/sdk/docs/install
   gcloud init
   ```

2. **Build and Push Image**
   ```bash
   # Set your project ID
   gcloud config set project YOUR_PROJECT_ID

   # Build and push to Google Container Registry
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-chatbot

   # Deploy to Cloud Run
   gcloud run deploy rag-chatbot \
     --image gcr.io/YOUR_PROJECT_ID/rag-chatbot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GOOGLE_API_KEY=your_key \
     --port 8080
   ```

3. **Get Service URL**
   ```bash
   gcloud run services describe rag-chatbot --region us-central1
   # Copy the URL
   ```

---

## 🧪 Post-Deployment Testing

### **Test Backend**

```bash
# Health check
curl https://your-backend-url/health

# List documents
curl https://your-backend-url/list-docs

# Test chat (replace with your backend URL)
curl -X POST https://your-backend-url/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test123"}'
```

### **Test Frontend**

1. Visit your Vercel URL
2. Try uploading a document
3. Ask a question in chat
4. Check browser console for errors

---

## 🔒 Security Checklist

- [ ] **API Key Rotated**: New key in production, old key deleted
- [ ] **CORS Configured**: Only allow your frontend domain
- [ ] **HTTPS Enabled**: Vercel/Railway/Cloud Run provide this automatically
- [ ] **Environment Variables**: Never commit .env to Git
- [ ] **File Size Limits**: Backend validates max 10MB uploads
- [ ] **Rate Limiting**: Consider adding (see backend improvements doc)

---

## 📊 Monitoring & Logs

### **Railway**
- Dashboard → Your Project → Deployments → Logs

### **Vercel**
- Dashboard → Your Project → Deployments → Functions tab

### **Docker (Local/VPS)**
```bash
# View logs
docker-compose logs -f

# Check container status
docker-compose ps

# Restart services
docker-compose restart
```

---

## 💰 Cost Estimates

| Platform | Backend | Frontend | Total/Month |
|----------|---------|----------|-------------|
| **Railway + Vercel** | $5 (or free 500hrs) | Free | $0-5 |
| **Render + Vercel** | Free (sleeps after 15min) | Free | $0 |
| **DigitalOcean** | $5-10 | Free (Vercel) | $5-10 |
| **Google Cloud Run** | Pay-per-use (~$2-5) | Free (Vercel) | $2-5 |
| **AWS EC2** | $5-20 | Free (Vercel) | $5-20 |

---

## 🐛 Common Issues

### **Issue: Backend CORS Error**
**Solution**: Add frontend URL to `main.py` origins list

### **Issue: Frontend Can't Connect to Backend**
**Solution**: Check `NEXT_PUBLIC_API_BASE_URL` in Vercel env vars

### **Issue: Upload Fails**
**Solution**: 
- Check file size < 10MB
- Verify backend has write permissions for `uploads/` directory
- Check backend logs for errors

### **Issue: Docker Build Fails**
**Solution**:
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### **Issue: Out of Memory on Free Tier**
**Solution**: 
- Reduce `k` in retriever (default 8 → 4)
- Use smaller chunk sizes
- Upgrade to paid tier

---

## 🚀 Quick Start Commands

**Deploy Backend (Railway CLI)**:
```bash
cd c:\Users\KIIT\Desktop\Projects\rag-chatbot
railway login
railway init
railway up
railway domain
```

**Deploy Frontend (Vercel CLI)**:
```bash
cd c:\Users\KIIT\Desktop\Projects\rag-chatbot\frontend
npm install -g vercel
vercel login
vercel --prod
```

**Deploy with Docker**:
```bash
cd c:\Users\KIIT\Desktop\Projects\rag-chatbot
docker-compose up -d
```

---

## 📝 Next Steps After Deployment

1. ✅ Test all functionality (upload, chat, delete)
2. 📈 Set up monitoring (Railway/Vercel dashboards)
3. 🔐 Add authentication (optional, see backend improvements)
4. 🎨 Add custom domain (optional, ~$10-15/year)
5. 🚀 Implement new features (summarization, citations, etc.)

---

## 🆘 Need Help?

- **Railway**: https://docs.railway.app
- **Vercel**: https://vercel.com/docs
- **Docker**: https://docs.docker.com
- **Google Cloud**: https://cloud.google.com/run/docs

Good luck with deployment! 🎉
