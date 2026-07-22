from flask import Flask
from flask_socketio import SocketIO
import requests
from features import validate_and_normalise
  
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
  
MEMBER4_URL = 'http://localhost:8000/behaviour'
  
@socketio.on('behaviour_features')
def handle_features(data):
      '''Called every time JS sends behaviour features'''
      print(f'Received from browser: {data}')
  
      # Validate and normalise the features
      clean_data = validate_and_normalise(data)
  
      # Forward to Member 4's server
      try:
          requests.post(MEMBER4_URL, json=clean_data, timeout=2)
          print(f'Forwarded to Member 4: {clean_data}')
      except Exception as e:
          print(f'Member 4 not connected yet: {e}')
          # That is okay — just print for now
  
  
if __name__ == '__main__':
      print('Behaviour bridge running on port 5001...')
      socketio.run(app, host='0.0.0.0', port=5001)
  
