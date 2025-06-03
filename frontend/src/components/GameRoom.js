import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function GameRoom({ user, onLogout }) {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRoomData();
    const interval = setInterval(fetchRoomData, 1000); // Обновляем каждую 1 секунду
    return () => clearInterval(interval);
  }, [roomId]);

  const fetchRoomData = async () => {
    try {
      const response = await axios.get(`/api/rooms/${roomId}/`);
      setRoom(response.data);
      setGame(response.data.game);
      setError('');
    } catch (error) {
      console.error('Ошибка загрузки данных комнаты:', error);
      setError('Ошибка загрузки данных комнаты');
    } finally {
      setLoading(false);
    }
  };

  const handleCellClick = async (row, col) => {
    if (!game || game.status !== 'ongoing') return;
    if (game.board[row][col] !== '') return;
    
    //проверяем, чей ход
    const isPlayerX = game.player_x.id === user.id;
    const isPlayerO = game.player_o.id === user.id;
    const isMyTurn = (isPlayerX && game.current_turn === 'X') || (isPlayerO && game.current_turn === 'O');
    
    if (!isMyTurn) return;

    try {
      const response = await axios.post(`/api/rooms/${roomId}/move/`, {
        row,
        col
      });
      setGame(response.data.game);
    } catch (error) {
      console.error('Ошибка при совершении хода:', error);
      alert(error.response?.data?.error || 'Ошибка при совершении хода');
    }
  };

  const handleLeaveRoom = async () => {
    if (window.confirm('Вы уверены, что хотите покинуть комнату?')) {
      try {
        await axios.post(`/api/rooms/${roomId}/leave/`);
        navigate('/');
      } catch (error) {
        console.error('Ошибка при выходе из комнаты:', error);
      }
    }
  };

  const getGameStatus = () => {
    if (!game) return 'Ожидание начала игры...';
    
    switch (game.status) {
      case 'ongoing':
        const currentPlayer = game.current_turn === 'X' ? game.player_x : game.player_o;
        return `Ход игрока: ${currentPlayer.username} (${game.current_turn})`;
      case 'x_wins':
        return `🎉 Победил ${game.player_x.username} (X)!`;
      case 'o_wins':
        return `🎉 Победил ${game.player_o.username} (O)!`;
      case 'draw':
        return '🤝 Ничья!';
      default:
        return 'Игра завершена';
    }
  };

  const isMyTurn = () => {
    if (!game || game.status !== 'ongoing') return false;
    const isPlayerX = game.player_x.id === user.id;
    const isPlayerO = game.player_o.id === user.id;
    return (isPlayerX && game.current_turn === 'X') || (isPlayerO && game.current_turn === 'O');
  };

  const getMySymbol = () => {
    if (!game) return '';
    return game.player_x.id === user.id ? 'X' : 'O';
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
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
          <h1>Комната: {room?.name}</h1>
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
          <div className="game-info">
            <h3>Код комнаты: {room?.code}</h3>
            
            {room && room.player_count < 2 ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <h3>Ожидание второго игрока...</h3>
                <p>Поделитесь кодом комнаты с другом: <strong>{room.code}</strong></p>
              </div>
            ) : (
              <>
                <div className="players-info">
                  {game && (
                    <>
                      <div className={`player ${game.current_turn === 'X' ? 'active' : ''}`}>
                        <strong>{game.player_x.username}</strong> (X)
                        {game.player_x.id === user.id && ' - Вы'}
                      </div>
                      <div className={`player ${game.current_turn === 'O' ? 'active' : ''}`}>
                        <strong>{game.player_o.username}</strong> (O)
                        {game.player_o.id === user.id && ' - Вы'}
                      </div>
                    </>
                  )}
                </div>
                
                <div className="game-status">
                  {getGameStatus()}
                  {isMyTurn() && <div style={{ color: '#27ae60' }}>Ваш ход!</div>}
                  {game && <div>Вы играете за: <strong>{getMySymbol()}</strong></div>}
                </div>
                
                {game && (
                  <div className="game-board">
                    {game.board.map((row, rowIndex) =>
                      row.map((cell, colIndex) => (
                        <button
                          key={`${rowIndex}-${colIndex}`}
                          className="game-cell"
                          onClick={() => handleCellClick(rowIndex, colIndex)}
                          disabled={!isMyTurn() || cell !== '' || game.status !== 'ongoing'}
                          style={{
                            cursor: isMyTurn() && cell === '' && game.status === 'ongoing' ? 'pointer' : 'default'
                          }}
                        >
                          {cell}
                        </button>
                      ))
                    )}
                  </div>
                )}
              </>
            )}
            
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <button onClick={handleLeaveRoom} className="btn btn-danger">
                Покинуть комнату
              </button>
              
              {game && game.status !== 'ongoing' && (
                <div style={{ marginTop: '1rem' }}>
                  <Link to="/" className="btn btn-primary" style={{ marginRight: '1rem' }}>
                    Главная
                  </Link>
                  <Link to="/rooms" className="btn btn-secondary">
                    Список комнат
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GameRoom;