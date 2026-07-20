  import { useState, useEffect, useRef } from 'react';
  import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
  
  const COLORS = { LOW: '#1D9E75', MEDIUM: '#BA7517', OVERLOADED: '#E24B4A' };
  
  export default function Dashboard() {
    const [loadClass, setLoadClass] = useState('LOW');
    const [loadScore, setLoadScore] = useState(0);
    const [history, setHistory]     = useState([]);
    const [showBreak, setShowBreak] = useState(false);
    const overloadCount = useRef(0);
  
    useEffect(() => {
      // Connect to FastAPI WebSocket
      const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
  
      ws.onopen  = () => console.log('Dashboard connected!');
      ws.onclose = () => console.log('Dashboard disconnected.');
  
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLoadClass(data.load_class);
        setLoadScore(data.load_score);
  
        // Add to history chart (keep last 60 points = 5 minutes)
        setHistory(prev => {
          const scoreNum = data.load_class === 'LOW' ? 0
                         : data.load_class === 'MEDIUM' ? 1 : 2;
          const newPoint = { time: new Date().toLocaleTimeString(), score: scoreNum };
          return [...prev.slice(-59), newPoint];
        });
  
        // Overload detection — 2 consecutive = trigger
        if (data.load_class === 'OVERLOADED') {
          overloadCount.current += 1;
          if (overloadCount.current >= 2) {
            setShowBreak(true);
            overloadCount.current = 0;
          }
        } else {
          overloadCount.current = 0;
        }
      };
  
      return () => ws.close();
    }, []);
  
    const color = COLORS[loadClass] || '#1D9E75';
  
    return (
      <div style={{fontFamily:'Arial', padding:'24px', maxWidth:'900px', margin:'0 auto'}}>
        <h2 style={{color:'#185FA5'}}>Cognitive Load Monitor</h2>
  
        {/* Live Score Gauge */}
        <div style={{
          background: color + '22',
          border: `2px solid ${color}`,
          borderRadius:'16px', padding:'24px', marginBottom:'24px',
          display:'flex', alignItems:'center', gap:'24px'
        }}>
          <div style={{fontSize:'64px', fontWeight:'bold', color}}>{Math.round(loadScore*100)}%</div>
          <div>
            <div style={{fontSize:'28px', fontWeight:'bold', color}}>{loadClass}</div>
            <div style={{color:'#555', fontSize:'14px'}}>Cognitive Load · Updates every 5 sec</div>
          </div>
        </div>
  
        {/* Session History Chart */}
        <h3>Session History</h3>
        <ResponsiveContainer width='100%' height={200}>
          <LineChart data={history}>
            <XAxis dataKey='time' hide />
            <YAxis domain={[0,2]} ticks={[0,1,2]}
              tickFormatter={v => ['Low','Med','High'][v]} />
            <Tooltip formatter={v => ['Low','Medium','Overloaded'][v]} />
            <Line type='monotone' dataKey='score' stroke='#185FA5' dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
  
        {/* Overload Intervention Modal */}
        {showBreak && (
          <div style={{
            position:'absolute', top:0, left:0, right:0, bottom:0,
            background:'rgba(0,0,0,0.5)',
            display:'flex', alignItems:'center', justifyContent:'center'
          }}>
            <div style={{
              background:'white', borderRadius:'16px',
              padding:'40px', textAlign:'center', maxWidth:'400px'
            }}>
              <h2 style={{color:'#E24B4A'}}>You seem overloaded!</h2>
              <p>You have been struggling for 10+ seconds.<br/>Take a 2-minute break.</p>
              <button
                onClick={() => setShowBreak(false)}
                style={{
                  background:'#185FA5', color:'white',
                  border:'none', borderRadius:'8px',
                  padding:'12px 32px', fontSize:'16px', cursor:'pointer'
                }}>
                OK, I will take a break
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }
