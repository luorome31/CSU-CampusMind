import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Eye, EyeOff } from 'lucide-react';
import { Card, CardBody } from '../../components/ui';
import { Button } from '../../components/ui';
import { authStore } from './authStore';
import { EMPTY_STATE_AVATAR } from '../../utils/avatar';
import './LoginPage.css';

export function LoginPage() {
  const navigate = useNavigate();
  const login = authStore((s) => s.login);
  const isLoading = authStore((s) => s.isLoading);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败，请检查学号和密码');
    }
  };

  return (
    <div className="login-page">
      {/* Decorative Leaves */}
      <div className="leaves-container">
        <div className="leaf leaf-1">🍃</div>
        <div className="leaf leaf-2">🍃</div>
        <div className="leaf leaf-3">🍂</div>
        <div className="leaf leaf-4">🍃</div>
      </div>

      <div className="compass-decoration">🧭</div>

      <Card variant="auth" padding="lg" className="login-card">
        <CardBody>
          <header className="login-header">
            <div className="login-logo">
              <img src={EMPTY_STATE_AVATAR} alt="CampusMind" />
            </div>
            <h1 className="login-title">CampusMind</h1>
            <p className="login-subtitle">
              欢迎回来<br />
              请使用中南大学统一身份认证登录
            </p>
          </header>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="input-field">
              <label htmlFor="username">学号</label>
              <div className="input-with-icon">
                <User size={18} className="input-icon" />
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="请输入学号"
                  required
                />
              </div>
            </div>

            <div className="input-field">
              <label htmlFor="password">密码</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="请输入密码"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {error && <p className="login-error">{error}</p>}

            <div className="form-actions">
              <Button type="submit" disabled={isLoading} fullWidth className="btn-login">
                {isLoading ? '登录中...' : '登录'}
              </Button>
            </div>
          </form>

          <footer className="login-footer">
            <p>© 2026 CampusMind · 中南大学智能校园助手</p>
          </footer>
        </CardBody>
      </Card>
    </div>
  );
}
