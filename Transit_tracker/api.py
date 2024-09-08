from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name="static")

client = MongoClient('localhost', 27017)
db = client['TT']
location_collection = db['bus_locations']
eta_collection = db['eta_pred']


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.get("/bus/{bus_id}")
async def get_bus_location(bus_id: str):
    location = location_collection.find_one(
        {'busId': bus_id},
        sort=[
            ('timestamp', -1)
        ]
    )

    if location:
        location['_id'] = str(location['_id'])
        return location
    return {"error": "Bus not found"}


@app.get("/eta/{stop_id}")
async def get_stop_eta(stop_id: int):
    eta = eta_collection.find_one(
        {"stopId": stop_id},
        sort=[
            ("calculatedAt", -1)
        ]
    )
    if eta:
        eta['_id'] = str(eta['_id'])
        return eta
    return {"error": "ETA not found"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
