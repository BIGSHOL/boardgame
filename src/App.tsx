import './index.css'

function App() {
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', flexDirection: 'column' }}>
      {/* Header / StatusBar */}
      <header style={{
        padding: '1rem',
        backgroundColor: 'var(--color-navy)',
        color: 'var(--color-yellow)',
        borderBottom: '4px solid var(--color-gray)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0 }}>Hanyang: The Foundation</h1>
        <div>Turn: 1 | Season: Spring</div>
      </header>

      {/* Game Area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* Main Board (Left, Larger) */}
        <div style={{
          flex: 2,
          backgroundColor: '#e0e0e0', // Temporary Map bg
          padding: '1rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          borderRight: '2px solid var(--color-gray)'
        }}>
          <h2 style={{ color: 'var(--color-gray)' }}>Main Board (Capital Map)</h2>
          <p>Mount Bukhan (North)</p>
          <div style={{
            width: '400px',
            height: '400px',
            border: '2px dashed var(--color-gray)',
            display: 'grid',
            placeItems: 'center'
          }}>
            [Map Grid 5x5]
          </div>
          <p>Han River (South)</p>
        </div>

        {/* Personal Board (Right, Smaller) */}
        <div style={{
          flex: 1,
          backgroundColor: '#f5f5f5',
          padding: '1rem',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{ color: 'var(--color-navy)' }}>Architect's Desk</h2>

          <div style={{ marginBottom: '1rem' }}>
            <h3>Resources</h3>
            <div>Log: 0 | Stone: 0 | Tile: 0</div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <h3>Workers (Apprentices)</h3>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {[1, 2, 3].map(i => (
                <div key={i} style={{
                  width: '30px',
                  height: '30px',
                  backgroundColor: 'var(--color-navy)',
                  borderRadius: '50%',
                  color: 'white',
                  display: 'grid',
                  placeItems: 'center'
                }}>
                  {i}
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3>Blueprint Cards</h3>
            <div style={{ border: '1px solid #ccc', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              [Empty Slot]
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App
