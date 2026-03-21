import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import './styles/tokens/colors.css'
import './styles/tokens/spacing.css'
import './styles/tokens/typography.css'
import './styles/tokens/elevation.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
