from fastapi import FastAPI
  from pydantic import BaseModel

  app = FastAPI()

  class Request(BaseModel):
      home_team: str
      away_team: str

  @app.get("/")
  async def home():
      return {"status": "ok"}

  @app.post("/analyze")
  async def analyze(req: Request):
      return {
          "success": True,
          "home": req.home_team,
          "away": req.away_team,
          "home_win": 0.45,
          "draw": 0.30,
          "away_win": 0.25
      }

  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8000)
