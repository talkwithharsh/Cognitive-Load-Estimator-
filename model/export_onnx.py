  import torch
  from fusion_model import FusionModel
  
  model = FusionModel()
  model.load_state_dict(torch.load('fusion_model.pth'))
  model.eval()
  
  dummy = torch.zeros(1, 11)   # dummy input with 11 features
  torch.onnx.export(model, dummy, 'fusion_model.onnx',
      input_names=['features'], output_names=['logits'],
      dynamic_axes={'features': {0: 'batch'}})
  
  print('ONNX model saved to fusion_model.onnx')
