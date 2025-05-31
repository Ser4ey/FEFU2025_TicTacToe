import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function Stats({ user, onLogout }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats/');
      setStats(response.data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      setError('Ошибка загрузки статистики');
    } finally {
      setLoading(false);
    }
  };

  const getWinRate = () => {
    if (!stats || stats.games_played === 0) return 0;
    return ((stats.wins / stats.games_played) * 100).toFixed(1);
  };

  const getWinRateColor = () => {
    const rate = parseFloat(getWinRate());
    if (rate >= 70) return '#27ae60';
    if (rate >= 50) return '#f39c12';
    return '#e74c3c';
  };

  if (loading) {
    return <div className="loading">Загрузка статистики...</div>;
  }

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <h2>Ошибка</h2>
          <p>{error}</p>
          <Link to="/" className="btn btn-primary">Вернуться на главную</Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <header className="header">
        <div className="header-content">
          <h1>Моя статистика</h1>
          <div className="header-actions">
            <Link to="/" className="btn btn-secondary">Главная</Link>
            <span>Привет, {user.username}!</span>
            <button onClick={onLogout} className="btn btn-secondary">
              Выйти
            </button>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="card">
          <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>
            Статистика игрока: {stats?.user?.username}
          </h2>
          
          {stats && stats.games_played === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <h3>Вы еще не сыграли ни одной игры</h3>
              <p>Начните играть, чтобы увидеть свою статистику!</p>
              <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                Начать игру
              </Link>
            </div>
          ) : (
            <>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-number">{stats?.games_played || 0}</div>
                  <div className="stat-label">Всего игр</div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-number" style={{ color: '#27ae60' }}>
                    {stats?.wins || 0}
                  </div>
                  <div className="stat-label">Победы</div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-number" style={{ color: '#e74c3c' }}>
                    {stats?.losses || 0}
                  </div>
                  <div className="stat-label">Поражения</div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-number" style={{ color: '#f39c12' }}>
                    {stats?.draws || 0}
                  </div>
                  <div className="stat-label">Ничьи</div>
                </div>
              </div>
              
              <div className="card" style={{ textAlign: 'center', marginTop: '2rem' }}>
                <h3>Процент побед</h3>
                <div 
                  style={{ 
                    fontSize: '3rem', 
                    fontWeight: 'bold', 
                    color: getWinRateColor(),
                    margin: '1rem 0'
                  }}
                >
                  {getWinRate()}%
                </div>
                <div style={{ color: '#7f8c8d' }}>
                  {stats?.wins} побед из {stats?.games_played} игр
                </div>
              </div>
              
              <div className="card" style={{ marginTop: '2rem' }}>
                <h3 style={{ textAlign: 'center', marginBottom: '1rem' }}>Детальная статистика</h3>
                <div style={{ display: 'grid', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Общее количество игр:</span>
                    <strong>{stats?.games_played || 0}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Победы:</span>
                    <strong style={{ color: '#27ae60' }}>{stats?.wins || 0}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Поражения:</span>
                    <strong style={{ color: '#e74c3c' }}>{stats?.losses || 0}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Ничьи:</span>
                    <strong style={{ color: '#f39c12' }}>{stats?.draws || 0}</strong>
                  </div>
                  <hr style={{ margin: '1rem 0' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Процент побед:</span>
                    <strong style={{ color: getWinRateColor() }}>{getWinRate()}%</strong>
                  </div>
                </div>
              </div>
            </>
          )}
          
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <Link to="/" className="btn btn-primary" style={{ marginRight: '1rem' }}>
              Главная
            </Link>
            <button onClick={fetchStats} className="btn btn-secondary">
              🔄 Обновить
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Stats;