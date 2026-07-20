  from fastapi import FastAPI, WebSocket, WebSocketDisconnect
  from fastapi.middleware.cors import CORSMiddleware
  import asyncio, json, time, sqlite3
  from aggregator import Aggregator
  
  app = FastAPI()
  
  # Allow React frontend to connect
  app.add_middleware(CORSMiddleware,
      allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
  
  # Shared aggregator — holds incoming signals
  aggregator = Aggregator()
  
  # List of connected dashboard clients
  dashboard_clients = []
  
  # ─── Endpoints for other members ─────────────────────
  
  @app.post('/cv')
  async def receive_cv(data: dict):
      '''Member 1 sends CV features here'''
      aggregator.add_cv(data)
      return {'status': 'ok'}
  
  @app.post('/behaviour')
  async def receive_behaviour(data: dict):
      '''Member 2 sends behaviour features here'''
      aggregator.add_behaviour(data)
      return {'status': 'ok'}
  
  @app.post('/quiz')
  async def receive_quiz(data: dict):
      '''Member 3 sends quiz features here'''
      aggregator.add_quiz(data)
      return {'status': 'ok'}
  
  @app.get('/score')
  async def get_score():
      '''React dashboard polls this for latest score'''
      return aggregator.latest_result
  
  # ─── WebSocket for live dashboard updates ────────────
  
  @app.websocket('/ws/dashboard')
  async def dashboard_ws(ws: WebSocket):
      await ws.accept()
      dashboard_clients.append(ws)
      try:
          while True:
              await ws.receive_text()   # keep alive
      except WebSocketDisconnect:
          dashboard_clients.remove(ws)
  
  # ─── Background task: classify every 5 seconds ───────
  
  @app.on_event('startup')
  async def start_classification_loop():
      asyncio.create_task(classification_loop())
  
  async def classification_loop():
      '''Runs forever. Every 5 seconds: aggregate + classify + push to dashboard.'''
      while True:
          await asyncio.sleep(5)
  
          result = aggregator.classify()
          print(f'Classification result: {result}')
  
          # Save to SQLite
          save_score(result)
  
          # Push to all connected dashboards
          for client in dashboard_clients.copy():
              try:
                  await client.send_text(json.dumps(result))
              except:
                  dashboard_clients.remove(client)
  
  def save_score(result):
      conn = sqlite3.connect('../dataset/cognitive_load.db')
      conn.execute(
          'CREATE TABLE IF NOT EXISTS scores (timestamp INT, session_id TEXT, load_class TEXT, load_score REAL)'
      )
      conn.execute('INSERT INTO scores VALUES (?,?,?,?)',
          (result['timestamp'], result.get('session_id','unknown'),
           result['load_class'], result['load_score']))
      conn.commit(); conn.close()
  
  # ─── Run with: uvicorn server:app --reload --port 8000
