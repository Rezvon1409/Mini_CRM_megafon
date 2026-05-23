from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth , clients
import uvicorn

app = FastAPI(
    title="Megafon Mini CRM API",
    description="Ticket and Client Automation System of Megafon Tajikistan (Backend)", # Ислоҳ шуд ба англисӣ
    version="1.0.0",
    docs_url="/docs",       
    redoc_url="/redoc"      
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(clients.router)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "online",
        "project": "Megafon Mini CRM",
        "version": "1.0.0",
        "environment": "development",
        "documentation": "/docs"
    }

if __name__ == '__main__':
    uvicorn.run('main:app' , host='127.0.0.1' , port=8000 , reload=True)