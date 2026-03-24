// frontend/src/App.tsx
import { useEffect, useState } from 'react';
import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import { authStore } from './features/auth/authStore';

export function App() {
  const initAuth = authStore((s) => s.initAuth);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    initAuth().then(() => setReady(true));
  }, [initAuth]);

  if (!ready) {
    return null;
  }

  return <RouterProvider router={router} />;
}

export default App;
