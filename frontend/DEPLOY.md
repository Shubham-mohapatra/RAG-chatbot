# 🎨 Frontend Deployment Quick Guide

## Deploy to Vercel (Recommended - 5 minutes)

### Method 1: Vercel Dashboard (No CLI needed)

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with GitHub
3. **Click "Add New"** → "Project"
4. **Import** your `RAG-chatbot` repository
5. **Configure**:
   - Root Directory: `frontend`
   - Framework: Next.js (auto-detected)
   - Build Command: `npm run build` (auto-filled)
   - Output Directory: `.next` (auto-filled)
6. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.railway.app
   ```
   *(Replace with your actual backend URL)*
7. **Click "Deploy"**
8. **Wait 2-3 minutes** ⏳
9. **Get your URL**: `https://your-app.vercel.app` 🎉

### Method 2: Vercel CLI (For developers)

```powershell
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Follow prompts:
# - Link to existing project? No
# - Project name? rag-chatbot-frontend
# - Directory? ./
# - Override settings? No
```

---

## Deploy to Netlify (Alternative)

1. **Go to Netlify**: https://netlify.com
2. **Sign in** with GitHub
3. **Click "Add new site"** → "Import an existing project"
4. **Select** your repository
5. **Configure**:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `.next`
6. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.railway.app
   ```
7. **Deploy**

---

## Test Your Deployment

```bash
# Visit your deployed URL
https://your-app.vercel.app

# Check if it loads
# Try uploading a document
# Try chatting
```

---

## Update Backend CORS

After deploying frontend, update your backend's CORS settings:

**In Railway/Render Dashboard**:
- Add environment variable: `FRONTEND_URL=https://your-app.vercel.app`

**Or manually in `main.py`**:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add this line
]
```

---

## Environment Variables Checklist

- [ ] `NEXT_PUBLIC_API_BASE_URL` - Your backend URL (Railway/Render/Cloud Run)
- [ ] Backend CORS updated with frontend URL
- [ ] API responds to requests from frontend domain

---

## Common Issues

**Issue: "Failed to fetch" in browser console**
- Check backend CORS includes frontend URL
- Verify backend is running and accessible
- Check backend URL in environment variables

**Issue: Build fails**
- Ensure `package.json` has all dependencies
- Try local build first: `npm run build`
- Check Node.js version (need 18+)

**Issue: Environment variable not working**
- Must start with `NEXT_PUBLIC_`
- Redeploy after adding env vars
- Hard refresh browser (Ctrl+Shift+R)

---

## Next Steps

1. ✅ Update backend CORS with frontend URL
2. 🔒 Rotate Google API key (security)
3. 🎨 Add custom domain (optional)
4. 📊 Monitor with Vercel Analytics
5. 🚀 Build new features!

Congrats on deploying! 🎊
