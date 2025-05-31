import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

function Home({ user, onLogout }) {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleQuickGame = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/quick-game/');
      const roomId = response.data.room.id;
      navigate(`/room/${roomId}`);
    } catch (error) {
      console.error('Ошибка при создании быстрой игры:', error);
      alert('Ошибка при создании быстрой игры');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className="header">
        <div className="header-content">
          <h1>Крестики-нолики</h1>
          <div className="header-actions">
            <span>Привет, {user.username}!</span>
            <button onClick={onLogout} className="btn btn-secondary">
              Выйти
            </button>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="card">
          <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Главное меню</h2>
          
          <div style={{ display: 'grid', gap: '1rem', maxWidth: '400px', margin: '0 auto' }}>
            <button 
              onClick={handleQuickGame}
              className="btn btn-success"
              style={{ padding: '1rem', fontSize: '1.1rem' }}
              disabled={loading}
            >
              {loading ? 'Поиск игры...' : '🎮 Быстрая игра'}
            </button>
            
            <Link to="/rooms" className="btn btn-primary" style={{ padding: '1rem', fontSize: '1.1rem' }}>
              🏠 Список комнат
            </Link>
            
            <Link to="/stats" className="btn btn-secondary" style={{ padding: '1rem', fontSize: '1.1rem' }}>
              📊 Моя статистика
            </Link>
          </div>
          
          <div style={{ marginTop: '2rem', textAlign: 'center', color: '#7f8c8d' }}>
            <h3>Как играть:</h3>
            <ul style={{ textAlign: 'left', maxWidth: '400px', margin: '1rem auto' }}>
              <li><strong>Быстрая игра</strong> - автоматически найдет игру или создаст новую комнату</li>
              <li><strong>Список комнат</strong> - просмотр всех доступных комнат, создание новой</li>
              <li><strong>Статистика</strong> - ваши результаты игр</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;