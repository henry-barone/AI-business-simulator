# AI Business Simulation - Development Setup

This guide will help you set up and run the AI Business Simulation application locally for development and testing.

## 🚀 Quick Start

### Option 1: Python Development Server (Recommended)
```bash
python dev-server.py
```

### Option 2: Shell Script
```bash
./start-dev.sh
```

### Option 3: NPM Scripts
```bash
npm run dev
# or
npm start
```

### Option 4: Manual Start (Individual Servers)
```bash
# Terminal 1 - Backend
npm run backend

# Terminal 2 - Frontend  
npm run frontend
```

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for version control)

## 🛠 First Time Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd ai_business_sim
   ```

2. **Install all dependencies**:
   ```bash
   npm run install:all
   ```

3. **Set up environment variables**:
   - Backend `.env` file is already created
   - Frontend `.env` file is already created
   - Update with your actual API keys if needed

4. **Initialize the database**:
   ```bash
   cd backend
   python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
   cd ..
   ```

## 🌐 Local Development URLs

Once the servers are running:

- **Frontend Application**: http://localhost:8080
- **Backend API**: http://localhost:5001
- **API Health Check**: http://localhost:5001/health

## 🧪 Testing the Setup

### Test Backend API
```bash
npm run test:backend
```

### Test Frontend
```bash
npm run test:frontend
```

### Test API Endpoints
```bash
npm run test:api
```

### Manual API Testing
```bash
# Health check
curl http://localhost:5001/health

# Create a company
curl -X POST http://localhost:5001/api/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Company","industry":"Manufacturing"}'

# Get dynamic questionnaire
curl -X POST http://localhost:5001/api/questionnaire/next \
  -H "Content-Type: application/json" \
  -d '{"companyId":"1","previousAnswers":{}}'
```

## 📁 Project Structure

```
ai_business_sim/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── models/             # Database models
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic services
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── .env              # Frontend environment variables
├── dev-server.py          # Python development server script
├── start-dev.sh          # Shell script to start both servers
├── package.json          # Development scripts
└── DEV-SETUP.md          # This file
```

## 🔧 Development Features

### Hot Reload
- Both frontend and backend support hot reload
- Changes to code will automatically restart the servers
- No need to manually restart during development

### CORS Configuration
- CORS is properly configured for local development
- Frontend (localhost:8080) can communicate with backend (localhost:5001)

### Database
- Uses SQLite for local development (no PostgreSQL setup required)
- Database file: `backend/ai_business_sim.db`
- Automatically created on first run

### Environment Variables
- Backend: `backend/.env`
- Frontend: `frontend/.env`
- Pre-configured for local development

## 🐛 Troubleshooting

### Port Already in Use
If you get port conflicts:

```bash
# Check what's using port 5001
lsof -i :5001

# Check what's using port 8080
lsof -i :8080

# Kill processes if needed
kill -9 <PID>
```

### Backend Issues
```bash
# Check Python dependencies
cd backend
pip install -r requirements.txt

# Verify Flask app can start
python -c "from app import create_app; print('✅ Backend imports work')"
```

### Frontend Issues
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check if Vite works
npm run dev
```

### Database Issues
```bash
# Reset database
cd backend
rm -f ai_business_sim.db
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### CORS Issues
If frontend can't connect to backend:
1. Check that CORS_ORIGINS includes `http://localhost:8080` in `backend/.env`
2. Restart the backend server
3. Check browser console for CORS errors

## 📝 Development Workflow

1. **Start the development servers**:
   ```bash
   python dev-server.py
   ```

2. **Open the application**:
   - Go to http://localhost:8080 in your browser

3. **Make changes**:
   - Edit frontend code in `frontend/src/`
   - Edit backend code in `backend/`
   - Both servers will auto-reload

4. **Test your changes**:
   - Use the web interface
   - Test API endpoints with curl or Postman
   - Check browser console for errors
   - Check terminal for server logs

5. **Stop the servers**:
   - Press `Ctrl+C` in the terminal running the dev server

## 🚀 Production Notes

This setup is for **development only**. For production:

- Use a proper WSGI server (gunicorn) for Flask
- Use a production build of the React app
- Use PostgreSQL instead of SQLite
- Set up proper environment variables
- Configure proper CORS origins
- Add authentication and security measures

## 🆘 Need Help?

If you encounter issues:

1. Check this troubleshooting guide
2. Look at the terminal output for error messages
3. Check browser console for frontend errors
4. Verify all dependencies are installed
5. Make sure ports 5001 and 8080 are available

## 📊 API Documentation

The backend provides these main endpoints:

- `POST /api/companies` - Create a new company
- `POST /api/companies/{id}/upload-pl` - Upload P&L file
- `POST /api/questionnaire/next` - Get next questionnaire question
- `POST /api/companies/{id}/questionnaire` - Submit questionnaire answer
- `GET /api/companies/{id}/simulation` - Get simulation results
- `POST /api/simulations/{id}/adjust` - Adjust simulation parameters

For detailed API documentation, check the route files in `backend/routes/`.