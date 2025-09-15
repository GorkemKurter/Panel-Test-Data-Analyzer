from io import BytesIO
from fastapi import FastAPI, Request, UploadFile, File, Form, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from services.analyzer import analyze_data
from fastapi.staticfiles import StaticFiles
import os
GRAPH_CACHE = {}
app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="C:\\Users\\gorkemk\\Desktop\\Test Qualification Improvment\\SAP_Automation\\Panel Test Data Analyzer\\templates") #Must be automated before the production

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    
    columns = [chr(i) for i in range(ord("A"), ord("Z")+1)]
    columns += [f"A{chr(i)}" for i in range(ord("A"), ord("Q"))]
    columns += "-"

    return templates.TemplateResponse("index.html", {"request": request, "columns": columns})

@app.post("/analyze")
async def analyze_excel(
    request : Request,
    file: UploadFile = File(...),
    rpm: str = Form(...),
    su_valf: str = Form(...),
    su_toplam: str = Form(...),
    sicaklik: str = Form(...),
    tahliye: str = Form(...),
    twinjet: str = Form(...),
    resistans: str = Form(...),
    zaman: str = Form(...)
):
    contents = await file.read()
    filename = file.filename.lower()
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(BytesIO(contents))
    elif filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(contents), sep=';', engine='python', on_bad_lines='skip', header=None, skiprows=1)
    elif filename.endswith(".txt"):
        df = pd.read_table(BytesIO(contents), sep=';', engine='python', on_bad_lines='skip', header=None, skiprows=1)
    else:
        return JSONResponse(content={"error": "Desteklenmeyen dosya türü."}, status_code=400)
    
    csv_columns = [chr(i) for i in range(ord("A"), ord("Z")+1)]
    csv_columns += [f"A{chr(i)}" for i in range(ord("A"), ord("Q"))]
    if len(df.columns) > len(csv_columns):
        df = df.iloc[:, :len(csv_columns)]
    df = df.map(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
    df = df.apply(pd.to_numeric, errors='coerce')
    df.columns = csv_columns[:len(df.columns)]
    #print(df.tail())
    columns = {
        "rpm": rpm if rpm != "-" else None,
        "su_valf": su_valf if su_valf != "-" else None,
        "su_toplam": su_toplam if su_toplam != "-" else None,
        "sicaklik": sicaklik if sicaklik != "-" else None,
        "tahliye": tahliye if tahliye != "-" else None,
        "twinjet": twinjet if twinjet != "-" else None,
        "resistans": resistans if resistans != "-" else None,
        "zaman": zaman if zaman != "-" else None
    }

    results = analyze_data(df, columns)
    global GRAPH_CACHE
    GRAPH_CACHE = results["graphs"]
    return templates.TemplateResponse(
        "result.html", 
        {"request": request, "result": results, "graphs": results["graphs"]})

@router.get("/graph/{graph_name}", response_class=HTMLResponse)
async def get_graph(graph_name: str):
    global GRAPH_CACHE
    if graph_name not in GRAPH_CACHE:
        return HTMLResponse(content=f"<h3>Grafik '{graph_name}' bulunamadı.</h3>", status_code=404)
    return HTMLResponse(content=GRAPH_CACHE[graph_name])

app.include_router(router)