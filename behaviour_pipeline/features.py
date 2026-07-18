def validate_and_normalise(data):
      '''
      Clean and normalise raw behaviour features.
      Clamps values to sensible ranges.
      Normalises each to 0.0 - 1.0 scale.
      '''
      # Clamp to max realistic values
      wpm             = min(float(data.get('wpm', 0)), 120.0)
      backspace_rate  = min(float(data.get('backspace_rate', 0)), 1.0)
      scroll_reversals= min(int(data.get('scroll_reversals', 0)), 20)
      mouse_idle      = min(float(data.get('mouse_idle_sec', 0)), 60.0)
  
      # Normalise to 0.0 - 1.0
      return {
          'timestamp'        : int(data.get('timestamp', 0)),
          'wpm'              : round(wpm / 120.0, 3),
          'backspace_rate'   : round(backspace_rate, 3),
          'scroll_reversals' : round(scroll_reversals / 20.0, 3),
          'mouse_idle'       : round(mouse_idle / 60.0, 3)
      }
  
