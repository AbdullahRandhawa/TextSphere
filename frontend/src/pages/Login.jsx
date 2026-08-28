import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const { loginEmail, registerEmail, loginGoogle } = useAuth();
  const navigate = useNavigate();

  const [tab,         setTab]         = useState('login'); // 'login' | 'register'
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [displayName, setDisplayName] = useState('');
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');

  const go = () => navigate('/');

  const handleEmail = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'login') {
        await loginEmail(email, password);
      } else {
        await registerEmail(email, password, displayName);
      }
      go();
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    setError('');
    setLoading(true);
    try {
      await loginGoogle();
      go();
    } catch (err) {
      setError(err.message || 'Google sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <div className="login-card" role="main">
        {/* Logo */}
        <div className="login-logo">
          <div className="login-logo-icon">🌐</div>
          <span className="login-logo-name">TextSphere</span>
        </div>

        {/* Tab switch */}
        <div className="login-tabs" role="tablist">
          <button
            id="login-tab-btn"
            className={`login-tab${tab === 'login' ? ' active' : ''}`}
            onClick={() => setTab('login')}
            role="tab"
            aria-selected={tab === 'login'}
          >
            Sign in
          </button>
          <button
            id="register-tab-btn"
            className={`login-tab${tab === 'register' ? ' active' : ''}`}
            onClick={() => setTab('register')}
            role="tab"
            aria-selected={tab === 'register'}
          >
            Create account
          </button>
        </div>

        {/* Error */}
        {error && <div className="login-error" role="alert">{error}</div>}

        {/* Email/password form */}
        <form className="login-form" onSubmit={handleEmail}>
          {tab === 'register' && (
            <label>
              Name
              <input
                id="register-name-input"
                className="input"
                type="text"
                placeholder="Your name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                autoComplete="name"
              />
            </label>
          )}
          <label>
            Email
            <input
              id="login-email-input"
              className="input"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </label>
          <label>
            Password
            <input
              id="login-password-input"
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
            />
          </label>
          <button
            id="login-submit-btn"
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '10px' }}
            disabled={loading}
          >
            {loading ? <><span className="spinner" /> Please wait…</> : (tab === 'login' ? 'Sign in' : 'Create account')}
          </button>
        </form>

        <div className="login-divider">or</div>

        <button
          id="google-login-btn"
          className="btn btn-google"
          onClick={handleGoogle}
          disabled={loading}
          type="button"
        >
          <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
            <path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.4 29.3 35 24 35c-6.1 0-11-4.9-11-11s4.9-11 11-11c2.8 0 5.3 1 7.3 2.7l5.7-5.7C33.5 7.1 29 5 24 5 12.9 5 4 13.9 4 25s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.6-.4-3.9z"/>
            <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c2.8 0 5.3 1 7.3 2.7l5.7-5.7C33.5 7.1 29 5 24 5 16.3 5 9.7 9 6.3 14.7z"/>
            <path fill="#4CAF50" d="M24 45c4.9 0 9.3-1.8 12.7-4.8l-5.9-5c-2 1.4-4.4 2.2-6.8 2.2-5.2 0-9.6-3.5-11.2-8.3l-6.5 5C9.5 41.3 16.3 45 24 45z"/>
            <path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.1-2.2 4-4 5.4l5.9 5C37 38.4 44 33 44 25c0-1.3-.1-2.6-.4-3.9z"/>
          </svg>
          Continue with Google
        </button>
      </div>
    </main>
  );
}
