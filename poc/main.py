import sys
import os
import io

# Force UTF-8 encoding on Windows console to prevent cp1252 crashes with Arabic script
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core import config, database
from sales import routes as sales_routes
from fraud import routes as fraud_routes

app = FastAPI(title="Ekinox Insurance Platform - SanlamAllianz Digital Acceleration", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Mount routes
app.include_router(sales_routes.router)
app.include_router(fraud_routes.router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def index_view(request: Request):
    """Render central platform cockpit & country switcher."""
    cfg = database.COUNTRY_CONFIGS[database.ACTIVE_COUNTRY]
    return templates.TemplateResponse(request, "index.html", {"country": cfg, "all_countries": database.COUNTRY_CONFIGS})

@app.get("/sales/chat")
def sales_chat_view(request: Request):
    """Render WhatsApp prospect conversation simulator with country context."""
    cfg = database.COUNTRY_CONFIGS[database.ACTIVE_COUNTRY]
    return templates.TemplateResponse(request, "sales_chat.html", {"country": cfg, "all_countries": database.COUNTRY_CONFIGS})

@app.get("/sales/workspace")
def sales_workspace_view(request: Request):
    """Render Sales Workspace & Business Cockpit with country context."""
    cfg = database.COUNTRY_CONFIGS[database.ACTIVE_COUNTRY]
    return templates.TemplateResponse(request, "sales_workspace.html", {"country": cfg, "all_countries": database.COUNTRY_CONFIGS})

@app.get("/fraud/workspace")
def fraud_workspace_view(request: Request):
    """Render Fraud Investigation Workspace with country context."""
    cfg = database.COUNTRY_CONFIGS[database.ACTIVE_COUNTRY]
    return templates.TemplateResponse(request, "fraud_workspace.html", {"country": cfg, "all_countries": database.COUNTRY_CONFIGS})

if __name__ == "__main__":
    print(f"=== Démarrage Ekinox Multi-Country Insurance Platform ===")
    print(f"Pays actif par défaut : {database.ACTIVE_COUNTRY} ({database.COUNTRY_CONFIGS[database.ACTIVE_COUNTRY]['name']})")
    print(f"URL locale : http://127.0.0.1:{config.PORT}")
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
