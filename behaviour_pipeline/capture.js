// ─── State ───────────────────────────────────────────
  let eventBuffer = [];
  let lastMouseMoveTime = Date.now();
  let lastScrollY = window.scrollY;
  let socket = null;
  
  // ─── Event Listeners ─────────────────────────────────
  
  // Listen for every key press
  document.addEventListener('keydown', function(e) {
      eventBuffer.push({
          type: 'key',
          key_type: e.key === 'Backspace' ? 'backspace'
                  : e.key === ' ' ? 'space'
                  : e.key.length === 1 ? 'letter' : 'other',
          time: Date.now()
      });
  });
  
  // Listen for mouse movement
  document.addEventListener('mousemove', function(e) {
      lastMouseMoveTime = Date.now();
  });
  
  // Listen for scroll
  window.addEventListener('scroll', function() {
      const currentY = window.scrollY;
      eventBuffer.push({
          type: 'scroll',
          direction: currentY > lastScrollY ? 'down' : 'up',
          time: Date.now()
      });
      lastScrollY = currentY;
  });
  
  // ─── Feature Computation (runs every 1 second) ───────
  
  function computeFeatures() {
      const now = Date.now();
      const keys   = eventBuffer.filter(e => e.type === 'key');
      const scrolls = eventBuffer.filter(e => e.type === 'scroll');
  
      // Words per minute (assume 5 chars = 1 word)
      const letters = keys.filter(k => k.key_type === 'letter').length;
      const wpm = (letters / 5) * 60;
  
      // Backspace rate
      const backspaces = keys.filter(k => k.key_type === 'backspace').length;
      const backspace_rate = keys.length > 0 ? backspaces / keys.length : 0;
  
      // Scroll reversals — count direction changes
      let reversals = 0;
      for (let i = 1; i < scrolls.length; i++) {
          if (scrolls[i].direction !== scrolls[i-1].direction) {
              reversals++;
          }
      }
  
      // Mouse idle in seconds
      const mouse_idle = (now - lastMouseMoveTime) / 1000;
  
      // Clear buffer for next second
      eventBuffer = [];
  
      return {
          timestamp: Math.floor(now / 1000),
          wpm: Math.round(wpm * 10) / 10,
          backspace_rate: Math.round(backspace_rate * 100) / 100,
          scroll_reversals: reversals,
          mouse_idle_sec: Math.round(mouse_idle * 10) / 10
      };
  }
  
  // ─── Send to Python server every 1 second ────────────
  
  function initCapture() {
      // Connect to Python bridge server
      socket = io('http://localhost:5001');
  
      socket.on('connect', function() {
          console.log('Behaviour capture connected!');
      });
  
      // Every 1000ms = 1 second, compute and send features
      setInterval(function() {
          const features = computeFeatures();
          socket.emit('behaviour_features', features);
          console.log('Behaviour sent:', features);
      }, 1000);
  }
  
  // Auto-start when page loads
  window.onload = initCapture;
  
