from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sales.routes import router as sales_router
from fraud.routes import router as fraud_router
from core import config, database
import uvicorn
import os

app = FastAPI(
    title="Ekinox Insurance Platform - Multi-Country SanlamAllianz POC",
    description="POC interactif multi-pays - Côte d'Ivoire, Maroc, Sénégal",
    version="2.0.0"
)

# Disable Browser Caching Middleware for Live Local Development & Render
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

app.include_router(sales_router)
app.include_router(fraud_router)

# Country Switch Endpoints
@app.get("/api/country/active")
def get_active_country():
    """Get active country configuration."""
    code = database.ACTIVE_COUNTRY
    return database.COUNTRY_CONFIGS.get(code, database.COUNTRY_CONFIGS["CI"])

@app.post("/api/country/switch")
def switch_country(country_code: str = Form(...)):
    """Switch active country context (CI, MA, SN)."""
    if country_code not in database.COUNTRY_CONFIGS:
        raise HTTPException(status_code=400, detail="Invalid country code. Choose CI, MA, or SN.")
    cfg = database.set_active_country(country_code)
    return {"status": "success", "active_country": cfg}

# Page Views
@app.get("/")
def home(request: Request):
    """Render central platform cockpit with country context."""
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
