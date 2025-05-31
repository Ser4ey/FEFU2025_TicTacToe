import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

function RoomList({ user, onLogout }) {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRooms();
    const interval = setInterval(fetchRooms, 3000); // Обновляем каждые 3 секунды
    return () => clearInterval(interval);
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await axios.get('/api/rooms/');
      setRooms(response.data);
    } catch (error) {
      console.error('Ошибка загрузки данных комнаты:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    if (!newRoomName.trim()) return;
    
    setCreating(true);
    try {
      const response = await axios.post('/api/rooms/create/', {
        name: newRoomName
      });
      const roomId = response.data.id;
      navigate(`/room/${roomId}`);
    } catch (error) {
      console.error('Ошибка при создании комнаты:', error);
      alert('Ошибка при создании комнаты');
    } finally {
      setCreating(false);
    }
  };

  const handleJoinRoom = async (roomId) => {
    try {
      await axios.post(`/api/rooms/${roomId}/join/`);
      navigate(`/room/${roomId}`);
    } catch (error) {
      console.error('Ошибка при присоединении к комнате:', error);
      alert(error.response?.data?.error || 'Ошибка при присоединении к комнате');
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'waiting': return 'Ожидание игроков';
      case 'playing': return 'Игра идет';
      case 'finished': return 'Завершена';
      default: return status;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'waiting': return '#f39c12';
      case 'playing': return '#27ae60';
      case 'finished': return '#95a5a6';
      default: return '#95a5a6';
    }
  };

  return (
    <div>
      <header className="header">
        <div className="header-content">
          <h1>Список комнат</h1>
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
        <div className="navigation">
          <button 
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn btn-primary"
          >
            {showCreateForm ? 'Отмена' : '+ Создать комнату'}
          </button>
          <button onClick={fetchRooms} className="btn btn-secondary">
            🔄 Обновить
          </button>
        </div>

        {showCreateForm && (
          <div className="card">
            <h3>Создать новую комнату</h3>
            <form onSubmit={handleCreateRoom}>
              <div className="form-group">
                <label>Название комнаты:</label>
                <input
                  type="text"
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                  placeholder="Введите название комнаты"
                  required
                />
              </div>
              <button 
                type="submit" 
                className="btn btn-success"
                disabled={creating}
              >
                {creating ? 'Создание...' : 'Создать'}
              </button>
            </form>
          </div>
        )}

        {loading ? (
          <div className="loading">Загрузка комнат...</div>
        ) : (
          <div className="room-list">
            {rooms.length === 0 ? (
              <div className="card" style={{ textAlign: 'center' }}>
                <h3>Нет доступных комнат</h3>
                <p>Создайте новую комнату, чтобы начать игру!</p>
              </div>
            ) : (
              rooms.map(room => (
                <div key={room.id} className="room-item">
                  <div className="room-info">
                    <h3>{room.name}</h3>
                    <div className="room-meta">
                      <div>Код: <strong>{room.code}</strong></div>
                      <div>Создатель: {room.creator.username}</div>
                      <div>Игроки: {room.player_count}/2</div>
                      <div style={{ color: getStatusColor(room.status) }}>
                        Статус: {getStatusText(room.status)}
                      </div>
                    </div>
                  </div>
                  <div>
                    {room.status === 'waiting' && room.player_count < 2 ? (
                      <button 
                        onClick={() => handleJoinRoom(room.id)}
                        className="btn btn-success"
                      >
                        Присоединиться
                      </button>
                    ) : room.status === 'playing' && room.players.some(p => p.id === user.id) ? (
                      <Link to={`/room/${room.id}`} className="btn btn-primary">
                        Войти в игру
                      </Link>
                    ) : (
                      <button className="btn btn-secondary" disabled>
                        {room.status === 'playing' ? 'Игра идет' : 'Недоступно'}
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RoomList;