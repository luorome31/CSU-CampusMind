import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>CampusMind Business App</h1>
      <p>Your actual application code goes here.</p>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <p><strong>Design System:</strong> Run <code>npm run playground</code> to preview the design system.</p>
      </div>
    </div>
  )
}

export default App
