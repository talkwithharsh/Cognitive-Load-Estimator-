import time
from inference import classify_features
  
  class Aggregator:
      def __init__(self):
          # Rolling buffers — store last 5 seconds of data
          self.cv_b uffer   = []
          self.beh_buffer  = []
          self.quiz_buffer = []
          self.latest_result = {
              'timestamp': 0,
              'load_class': 'LOW',
              'load_score': 0.0,
              'session_id': 'none'
          }
  
      def add_cv(self, data):
          self.cv_buffer.append(data)
          if len(self.cv_buffer) > 10:   # keep last 10 readings
              self.cv_buffer.pop(0)
  
      def add_behaviour(self, data):
          self.beh_buffer.append(data)
          if len(self.beh_buffer) > 10:
              self.beh_buffer.pop(0)
  
      def add_quiz(self, data):
          self.quiz_buffer.append(data)
          if len(self.quiz_buffer) > 5:
              self.quiz_buffer.pop(0)
  
      def _average(self, buffer, keys):
          '''Average a list of numeric keys from a buffer of dicts.'''
          if not buffer:
              return {k: 0.0 for k in keys}
          return {k: sum(d.get(k, 0) for d in buffer) / len(buffer) for k in keys}
  
      def classify(self):
          '''Merge all 3 buffers into one vector and classify.'''
  
          # Average each signal group
          cv  = self._average(self.cv_buffer,
              ['blink_rate', 'gaze_score', 'expression_num'])
          beh = self._average(self.beh_buffer,
              ['wpm', 'backspace_rate', 'scroll_reversals', 'mouse_idle'])
          quiz = self._average(self.quiz_buffer,
              ['response_time', 'confidence'])
  
          # Combine into one flat feature vector (11 values)
          feature_vector = [
              cv['blink_rate'], cv['gaze_score'], cv['expression_num'],
              beh['wpm'], beh['backspace_rate'], beh['scroll_reversals'], beh['mouse_idle'],
              quiz['response_time'], quiz['confidence'],
              0.0, 0.0   # 2 padding features to make it 11
          ]
  
          # Classify
          load_class, load_score = classify_features(feature_vector)
  
          self.latest_result = {
              'timestamp': int(time.time()),
              'load_class': load_class,
              'load_score': load_score,
              'cv': cv, 'behaviour': beh, 'quiz': quiz
          }
          return self.latest_result