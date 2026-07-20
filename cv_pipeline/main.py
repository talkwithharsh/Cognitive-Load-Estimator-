import cv2
import mediapipe as mp
import json, time, threading, asyncio, websockets
from blink_detector import BlinkCounter, calculate_ear
from gaze_detector import get_gaze_direction
from expression_classifier import extract_expression_features, predict_expression, load_or_default_classifier
  
  # Landmark index groups
LEFT_EYE  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
  
  # Global variable to hold the latest features
latest_features = {}
  
def run_cv_pipeline():
      '''This runs in a background thread. Reads webcam continuously.'''
      global latest_features
  
      mp_face = mp.solutions.face_mesh
      face_mesh = mp_face.FaceMesh(
          max_num_faces=1,
          refine_landmarks=True,   # needed for iris landmarks
          min_detection_confidence=0.5
      )
  
      blink_counter = BlinkCounter()
      clf = load_or_default_classifier()
      cap = cv2.VideoCapture(0)
      start_time = time.time()
  
      print('CV Pipeline started. Reading webcam...')
  
      while True:
          ret, frame = cap.read()
          if not ret:
              print('Cannot read webcam frame. Retrying...')
              time.sleep(0.5)
              continue
  
          # Convert BGR (OpenCV format) to RGB (MediaPipe format)
          rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          results = face_mesh.process(rgb)
  
          if results.multi_face_landmarks:
              lm = results.multi_face_landmarks[0].landmark
  
              # Calculate EAR for both eyes
              left_ear  = calculate_ear(lm, LEFT_EYE)
              right_ear = calculate_ear(lm, RIGHT_EYE)
  
              # Update blink count
              elapsed = time.time() - start_time
              blink_counter.update(left_ear, right_ear)
              blink_rate = blink_counter.get_blinks_per_minute(elapsed)
  
              # Get gaze direction
              gaze, gaze_score = get_gaze_direction(lm)
  
              # Get expression
              expr_features = extract_expression_features(lm)
              expression = predict_expression(expr_features, clf)
  
              # Package into JSON
              latest_features = {
                  'timestamp': int(time.time()),
                  'blink_rate': round(blink_rate, 2),
                  'gaze': gaze,
                  'gaze_score': round(gaze_score, 3),
                  'expression': expression,
                  'left_ear': round(left_ear, 3),
                  'right_ear': round(right_ear, 3)
              }
  
          time.sleep(0.2)   # read webcam 5 times per second
  
  
async def send_features():
      '''Every 1 second, send latest features to Member 4 server.'''
      uri = 'ws://localhost:8000/ws/cv'
      async with websockets.connect(uri) as ws:
          print('Connected to Member 4 server!')
          while True:
              if latest_features:
                  await ws.send(json.dumps(latest_features))
                  print(f'Sent: {latest_features}')
              await asyncio.sleep(1)
  
  
if __name__ == '__main__':
      # Start CV pipeline in background thread
      thread = threading.Thread(target=run_cv_pipeline, daemon=True)
      thread.start()
  
      # Send features to server in async loop
      asyncio.run(send_features())
