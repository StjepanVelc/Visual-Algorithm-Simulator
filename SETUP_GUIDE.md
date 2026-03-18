# Setup & Running Guide

## Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- npm or yarn

---

## 🚀 Quick Start

### Option 1: Desktop App (Tkinter)
```bash
python app.py
# Select "Desktop (Tkinter)" from menu
```

### Option 2: Web App (React + FastAPI)

#### Step 1: Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Step 3: Start Backend Server
```bash
cd backend
python main.py
```
Backend will run on `http://localhost:8000`

#### Step 4: Start Frontend Dev Server (in another terminal)
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:3000`

#### Step 5: Run app.py and select Web option
```bash
python app.py
# Select "Web (React + FastAPI)" from menu
# Browser will open automatically to http://localhost:3000
```

---

## 📝 Endpoints Reference

### Health Check
- **GET** `/api/health` - Check if backend is running

### BST Operations
- **GET** `/api/bst/state/{db_id}` - Get current BST state
- **POST** `/api/bst/insert/{db_id}?value={value}` - Insert node
- **POST** `/api/bst/delete/{db_id}?value={value}` - Delete node
- **GET** `/api/bst/traverse/{db_id}/{method}` - Traverse (bfs, dfs, inorder, etc.)

### Hash Table Operations
- **GET** `/api/hash/state/{db_id}` - Get hash table state
- **POST** `/api/hash/insert/{db_id}?key={key}&value={value}` - Insert item
- **POST** `/api/hash/delete/{db_id}?key={key}` - Delete item

### Tree Operations
- **GET** `/api/tree/state/{db_id}` - Get tree state
- **POST** `/api/tree/insert/{db_id}/{parent_id}?value={value}` - Insert node
- **GET** `/api/tree/traverse/{db_id}/{method}` - Traverse tree

### Recursion Operations
- **GET** `/api/recursion/state/{db_id}` - Get recursion tree state
- **POST** `/api/recursion/insert/{db_id}` - Insert node

### General Operations
- **GET** `/api/list-databases` - List all databases
- **POST** `/api/create-database/{adt_type}?db_name={name}` - Create new DB
- **DELETE** `/api/clear-database/{db_id}` - Clear database

---

## 📚 API Documentation

When backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 🛠️ Troubleshooting

### Backend fails to start
- Ensure FastAPI is installed: `pip install -r requirements.txt`
- Check if port 8000 is in use: `netstat -ano | findstr :8000`

### Frontend won't build
- Clear node_modules: `rm -rf frontend/node_modules && cd frontend && npm install`
- Clear npm cache: `npm cache clean --force`

### Backend connection error
- Confirm backend is running on http://localhost:8000
- Check CORS settings in `backend/main.py` if needed

### Port conflicts
- Change port in `frontend/vite.config.js` (server.port)
- Change port in `backend/main.py` (uvicorn.run port)

---

## 📦 Build for Production

### Frontend
```bash
cd frontend
npm run build
```
Output: `frontend/dist/`

### Backend
Recommended: Deploy with docker or cloud platform (Vercel, Heroku, AWS)

---

## 🔧 Development Workflow

1. Make changes to backend → API automatically reloads
2. Make changes to frontend → Vite HMR automatically updates
3. Test in browser with React DevTools & Konva debugging

---

## 🎨 Next Steps

- [ ] Implement BST Canvas visualization with Konva
- [ ] Implement Hash Table visualization
- [ ] Implement Tree visualization
- [ ] Implement Recursion stack animation
- [ ] Add frame capture/export functionality
- [ ] Add user authentication
- [ ] Deploy to production
