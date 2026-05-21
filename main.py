from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from pydantic import BaseModel
  from typing import Optional, List
  import os
  from datetime import datetime
  import random

  app = FastAPI(title="Sports Analyzer")

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  class AnalyzeRequest(BaseModel):
      sport: str = "football"
      home_team: str
      away_team: str
      match_date: Optional[str] = None
      competition: Optional[str] = None

  class Prediction(BaseModel):
      home_win: float
      draw: float
      away_win: float
      confidence: str

  class MatchInfo(BaseModel):
      competition: str
      home_team: str
      away_team: str
      date: str

  class AnalysisResponse(BaseModel):
      success: bool
      match_info: MatchInfo
      prediction: Prediction
      report: str
      data_sources: List[str]

  @app.get("/")
  async def home():
      return {"message": "Sports Analyzer API", "status": "ok"}

  @app.get("/health")
  async def health():
      return {"status": "ok", "timestamp": datetime.now().isoformat()}

  @app.post("/analyze", response_model=AnalysisResponse)
  async def analyze(request: AnalyzeRequest):
      home_win = 0.45 + random.uniform(-0.1, 0.1)
      draw = 0.28 + random.uniform(-0.05, 0.05)
      away_win = 1 - home_win - draw

      max_prob = max(home_win, draw, away_win)
      confidence = "高" if max_prob > 0.5 else "中" if max_prob > 0.4 else "低"

      prediction = Prediction(
          home_win=round(home_win, 3),
          draw=round(draw, 3),
          away_win=round(away_win, 3),
          confidence=confidence
      )

      report = f"{request.home_team} vs {request.away_team}"

      return AnalysisResponse(
          success=True,
          match_info=MatchInfo(
              competition=request.competition or "未知",
              home_team=request.home_team,
              away_team=request.away_team,
              date=request.match_date or datetime.now().strftime("%Y-%m-%d")
          ),
          prediction=prediction,
          report=report,
          data_sources=["智能分析"]
      )

  if __name__ == "__main__":
      import uvicorn
      port = int(os.getenv("PORT", 8000))
      uvicorn.run(app, host="0.0.0.0", port=port)
