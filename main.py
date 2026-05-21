 from fastapi import FastAPI, HTTPException
  from fastapi.middleware.cors import CORSMiddleware
  from fastapi.responses import HTMLResponse
  from pydantic import BaseModel
  from typing import Optional, List
  import os
  from datetime import datetime
  import random

  app = FastAPI(title="体育赛事分析API", version="1.0.0")

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

  @app.get("/", response_class=HTMLResponse)
  async def home():
      return """
      <!DOCTYPE html>
      <html lang="zh-CN">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">      
          <title>体育赛事分析</title>
          <style>
              body { font-family: Arial; background: linear-gradient(135deg, #667eea  
  0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center;
  justify-content: center; padding: 20px; }
              .container { background: white; border-radius: 20px; padding: 40px;     
  max-width: 600px; width: 100%; }
              h1 { text-align: center; color: #333; }
              .form-group { margin-bottom: 20px; }
              label { display: block; margin-bottom: 8px; color: #555; }
              input, select { width: 100%; padding: 12px; border: 2px solid #e0e0e0;  
  border-radius: 10px; font-size: 16px; }
              button { width: 100%; padding: 15px; background: #667eea; color: white; 
  border: none; border-radius: 10px; font-size: 18px; cursor: pointer; }
              .result { margin-top: 30px; padding: 20px; background: #f8f9fa;
  border-radius: 10px; display: none; }
              .result.show { display: block; }
              .prediction { display: flex; justify-content: space-around; margin: 20px   0; }
              .pred-item { text-align: center; }
              .pred-value { font-size: 32px; font-weight: bold; color: #667eea; }     
              .pred-label { font-size: 14px; color: #666; margin-top: 5px; }
          </style>
      </head>
      <body>
          <div class="container">
              <h1>⚽  体育赛事分析</h1>
              <div class="form-group">
                  <label>运动类型</label>
                  <select id="sport"><option value="football">足球</option><option    
  value="basketball">篮球</option></select>
              </div>
              <div class="form-group">
                  <label>主队</label>
                  <input type="text" id="homeTeam" placeholder="例如：曼城">
              </div>
              <div class="form-group">
                  <label>客队</label>
                  <input type="text" id="awayTeam" placeholder="例如：利物浦">        
              </div>
              <button onclick="analyze()">开始分析</button>
              <div class="result" id="result">
                  <h3 id="matchTitle"></h3>
                  <div class="prediction">
                      <div class="pred-item"><div class="pred-value"
  id="homeWin">--</div><div class="pred-label">主胜</div></div>
                      <div class="pred-item"><div class="pred-value"
  id="draw">--</div><div class="pred-label">平局</div></div>
                      <div class="pred-item"><div class="pred-value"
  id="awayWin">--</div><div class="pred-label">客胜</div></div>
                  </div>
              </div>
          </div>
          <script>
              async function analyze() {
                  const homeTeam = document.getElementById('homeTeam').value.trim();  
                  const awayTeam = document.getElementById('awayTeam').value.trim();  
                  const sport = document.getElementById('sport').value;
                  if (!homeTeam || !awayTeam) { alert('请输入球队名称'); return; }    
                  try {
                      const response = await fetch('/analyze', {
                          method: 'POST',
                          headers: {'Content-Type': 'application/json'},
                          body: JSON.stringify({ sport: sport, home_team: homeTeam,   
  away_team: awayTeam })
                      });
                      const data = await response.json();
                      if (data.success) {
                          document.getElementById('matchTitle').textContent =
  data.match_info.home_team + ' vs ' + data.match_info.away_team;
                          document.getElementById('homeWin').textContent =
  (data.prediction.home_win * 100).toFixed(1) + '%';
                          document.getElementById('draw').textContent =
  (data.prediction.draw * 100).toFixed(1) + '%';
                          document.getElementById('awayWin').textContent =
  (data.prediction.away_win * 100).toFixed(1) + '%';
                          document.getElementById('result').classList.add('show');    
                      }
                  } catch (error) { alert('分析失败'); }
              }
          </script>
      </body>
      </html>
      """

  @app.get("/health")
  async def health():
      return {"status": "ok", "timestamp": datetime.now().isoformat()}

  @app.post("/analyze", response_model=AnalysisResponse)
  async def analyze(request: AnalyzeRequest):
      try:
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

          report = f"""# {request.home_team} vs {request.away_team} 分析报告

  ## 预测结果
  - 主胜：{prediction.home_win:.1%}
  - 平局：{prediction.draw:.1%}
  - 客胜：{prediction.away_win:.1%}
  - 置信度：{prediction.confidence}

  ## 分析建议
  {"主队略占优势" if home_win > 0.4 else "双方实力接近"}

  ---
  Powered by Render.com"""

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
              data_sources=["智能分析引擎"]
          )
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))

  if __name__ == "__main__":
      import uvicorn
      port = int(os.getenv("PORT", 8000))
      uvicorn.run(app, host="0.0.0.0", port=port)
