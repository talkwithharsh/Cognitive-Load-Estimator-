def get_gaze_direction(landmarks):
      '''
      Returns 'CENTER', 'LEFT', or 'RIGHT'
      by comparing iris landmark to eye center landmark
      '''
      # Left iris center and left eye center
      left_iris  = landmarks[468]   # iris center
      left_eye   = landmarks[33]    # eye outer corner
      left_eye_r = landmarks[133]   # eye inner corner
  
      # Calculate eye width
      eye_width = abs(left_eye_r.x - left_eye.x)
  
      # How far is iris from eye center?
      eye_center_x = (left_eye.x + left_eye_r.x) / 2
      offset = (left_iris.x - eye_center_x) / eye_width
  
      # offset < -0.15 means looking left
      # offset > +0.15 means looking right
      # between -0.15 and +0.15 means looking center
      if offset < -0.15:
          return 'LEFT', abs(offset)
      elif offset > 0.15:
          return 'RIGHT', abs(offset)
      else:
          return 'CENTER', abs(offset)
