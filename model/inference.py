  import onnxruntime as ort
  import numpy as np
  
  CLASSES = ['LOW', 'MEDIUM', 'OVERLOADED']
  session = None
  
  def load_model():
      global session
      session = ort.InferenceSession('fusion_model.onnx')
      print('ONNX model loaded!')
  
  def classify_features(feature_vector):
      '''
      Input:  list of 11 floats
      Output: (load_class string, load_score float 0-1)
      '''
      if session is None:
          # Model not trained yet — return dummy result
          return 'LOW', 0.1
  
      x = np.array([feature_vector], dtype=np.float32)
      logits = session.run(['logits'], {'features': x})[0][0]
  
      # Convert logits to probabilities using softmax
      exp_logits = np.exp(logits - logits.max())
      probs = exp_logits / exp_logits.sum()
  
      # Get class with highest probability
      class_idx = int(np.argmax(probs))
      load_class = CLASSES[class_idx]
      load_score = float(probs[class_idx])
  
      return load_class, round(load_score, 3)
  
  # Load on import
  try:
      load_model()
  except FileNotFoundError:
      print('ONNX model not found yet. Train first with: python train.py')
  
