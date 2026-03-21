import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody } from '../../components/ui';
import { Button } from '../../components/ui';
import { Input } from '../../components/ui';
import { authStore } from './authStore';
import './LoginPage.css';

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
    <div className="login-page">
      <Card variant="auth" padding="lg" className="login-card">
        <CardBody>
          <h1 className="login-title">Sign In</h1>
          <p className="login-subtitle">Welcome back to CampusMind</p>

          <form className="login-form" onSubmit={handleSubmit}>
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

            {error && <p className="login-error">{error}</p>}

            <Button type="submit" disabled={isLoading} fullWidth>
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
