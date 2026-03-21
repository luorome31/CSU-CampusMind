import React from 'react'
import ReactDOM from 'react-dom/client'
import { Playground } from './Playground'
import '../styles/tokens/colors.css'
import '../styles/tokens/spacing.css'
import '../styles/tokens/typography.css'
import '../styles/tokens/elevation.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Playground />
  </React.StrictMode>,
)
