import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authStore } from './authStore';
import { Button } from '../../components/ui';
import { Input } from '../../components/ui';

export function LoginPage() {
  const navigate = useNavigate();
  const login = authStore((s) => s.login);
  const isLoading = authStore((s) => s.isLoading);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--color-bg-base)',
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: 'var(--color-bg-surface)',
          padding: 'var(--spacing-xl, 2rem)',
          borderRadius: '12px',
          boxShadow: 'var(--shadow-card)',
          width: '100%',
          maxWidth: '360px',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-md, 1rem)',
        }}
      >
        <h1
          style={{
            fontSize: 'var(--font-size-xl, 1.5rem)',
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--spacing-sm, 0.5rem)',
          }}
        >
          Sign In
        </h1>

        <Input
          label="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter username"
          required
        />

        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
          required
        />

        {error && (
          <p style={{ color: '#dc2626', fontSize: 'var(--font-size-sm, 0.875rem)' }}>
            {error}
          </p>
        )}

        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>
    </div>
  );
}
