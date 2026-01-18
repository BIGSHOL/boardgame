import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface Player {
  id: number;
  user_id: number;
  username: string;
  color: string;
  turn_order: number;
  is_host: boolean;
  is_ready: boolean;
}

interface Lobby {
  id: number;
  name: string;
  host_id: number;
  invite_code: string;
  status: string;
  max_players: number;
  game_id: number | null;
  players: Player[];
  created_at: string;
}

const colorStyles: Record<string, string> = {
  blue: 'bg-hanyang-navy text-white',
  red: 'bg-red-600 text-white',
  green: 'bg-green-600 text-white',
  yellow: 'bg-yellow-500 text-black',
};

export default function LobbyRoom() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, tokens, isAuthenticated } = useAuthStore();
  const [lobby, setLobby] = useState<Lobby | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchLobby = useCallback(async () => {
    if (!id) return;

    try {
      const response = await fetch(`/api/v1/lobbies/${id}`);
      if (!response.ok) {
        if (response.status === 404) {
          setError('로비를 찾을 수 없습니다.');
        } else {
          setError('로비 정보를 불러오는데 실패했습니다.');
        }
        return;
      }
      const data = await response.json();
      setLobby(data);

      // If game started, redirect to game
      if (data.status === 'started' && data.game_id) {
        navigate(`/game/${data.game_id}`);
      }
    } catch (err) {
      setError('로비 정보를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    fetchLobby();

    // Poll for updates every 2 seconds
    const interval = setInterval(fetchLobby, 2000);
    return () => clearInterval(interval);
  }, [fetchLobby]);

  const currentPlayer = lobby?.players.find(p => p.user_id === user?.id);
  const isHost = lobby?.host_id === user?.id;

  const handleReady = async () => {
    if (!tokens?.access_token || !id || !currentPlayer) return;

    try {
      const response = await fetch(`/api/v1/lobbies/${id}/ready`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.access_token}`,
        },
        body: JSON.stringify({ is_ready: !currentPlayer.is_ready }),
      });

      if (response.ok) {
        const updatedLobby = await response.json();
        setLobby(updatedLobby);
      }
    } catch (err) {
      setError('준비 상태 변경에 실패했습니다.');
    }
  };

  const handleStart = async () => {
    if (!tokens?.access_token || !id) return;

    try {
      const response = await fetch(`/api/v1/lobbies/${id}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        navigate(`/game/${data.game_id}`);
      } else {
        const error = await response.json();
        setError(error.detail || '게임 시작에 실패했습니다.');
      }
    } catch (err) {
      setError('게임 시작에 실패했습니다.');
    }
  };

  const copyInviteCode = () => {
    if (lobby?.invite_code) {
      navigator.clipboard.writeText(lobby.invite_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <div className="card text-center">
          <h2 className="font-display text-2xl text-hanyang-navy mb-4">
            로그인이 필요합니다
          </h2>
          <Link to="/login" className="btn-primary">
            로그인하기
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <p className="text-hanyang-stone">로딩 중...</p>
      </div>
    );
  }

  if (error || !lobby) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <div className="card text-center">
          <h2 className="font-display text-2xl text-red-600 mb-4">
            {error || '로비를 찾을 수 없습니다'}
          </h2>
          <Link to="/lobbies" className="btn-primary">
            로비 목록으로
          </Link>
        </div>
      </div>
    );
  }

  const allPlayersReady = lobby.players.every(p => p.is_ready || p.is_host);
  const canStart = isHost && lobby.players.length >= 2 && allPlayersReady;

  return (
    <div className="min-h-screen bg-hanyang-cream p-4">
      <div className="max-w-2xl mx-auto">
        <header className="mb-6">
          <div className="flex justify-between items-center">
            <h1 className="font-display text-3xl text-hanyang-navy">
              {lobby.name}
            </h1>
            <Link to="/lobbies" className="text-hanyang-stone hover:text-hanyang-navy">
              나가기
            </Link>
          </div>
        </header>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
            <button onClick={() => setError(null)} className="float-right">×</button>
          </div>
        )}

        {/* Invite code */}
        <div className="card mb-6">
          <h3 className="font-display text-lg text-hanyang-navy mb-2">
            초대 코드
          </h3>
          <div className="flex items-center gap-4">
            <code className="text-3xl font-mono tracking-wider text-hanyang-gold">
              {lobby.invite_code}
            </code>
            <button
              onClick={copyInviteCode}
              className="text-hanyang-stone hover:text-hanyang-navy"
            >
              {copied ? '복사됨!' : '복사'}
            </button>
          </div>
          <p className="text-sm text-hanyang-stone mt-2">
            친구에게 이 코드를 공유하세요
          </p>
        </div>

        {/* Players */}
        <div className="card mb-6">
          <h3 className="font-display text-lg text-hanyang-navy mb-4">
            플레이어 ({lobby.players.length}/{lobby.max_players})
          </h3>

          <div className="space-y-3">
            {lobby.players.map((player) => (
              <div
                key={player.id}
                className="flex items-center justify-between p-3 border border-hanyang-stone/30 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded-full ${colorStyles[player.color] || 'bg-gray-400'}`}
                  />
                  <div>
                    <span className="font-medium text-hanyang-navy">
                      {player.username}
                    </span>
                    {player.is_host && (
                      <span className="ml-2 text-xs bg-hanyang-gold text-white px-2 py-0.5 rounded">
                        호스트
                      </span>
                    )}
                    {player.user_id === user?.id && (
                      <span className="ml-2 text-xs text-hanyang-stone">
                        (나)
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  {player.is_host ? (
                    <span className="text-hanyang-stone text-sm">-</span>
                  ) : player.is_ready ? (
                    <span className="text-green-600 font-medium">준비 완료</span>
                  ) : (
                    <span className="text-hanyang-stone">대기 중</span>
                  )}
                </div>
              </div>
            ))}

            {/* Empty slots */}
            {Array.from({ length: lobby.max_players - lobby.players.length }).map((_, i) => (
              <div
                key={`empty-${i}`}
                className="flex items-center justify-center p-3 border border-dashed border-hanyang-stone/30 rounded-lg"
              >
                <span className="text-hanyang-stone">빈 자리</span>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="card">
          {isHost ? (
            <div className="space-y-3">
              <button
                onClick={handleStart}
                disabled={!canStart}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  canStart
                    ? 'bg-hanyang-gold text-white hover:bg-hanyang-gold/90'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                게임 시작
              </button>
              {!canStart && (
                <p className="text-sm text-center text-hanyang-stone">
                  {lobby.players.length < 2
                    ? '최소 2명의 플레이어가 필요합니다'
                    : '모든 플레이어가 준비 완료해야 합니다'}
                </p>
              )}
            </div>
          ) : currentPlayer ? (
            <button
              onClick={handleReady}
              className={`w-full py-3 rounded-lg font-medium transition-colors ${
                currentPlayer.is_ready
                  ? 'bg-hanyang-stone text-white hover:bg-hanyang-stone/90'
                  : 'bg-hanyang-gold text-white hover:bg-hanyang-gold/90'
              }`}
            >
              {currentPlayer.is_ready ? '준비 취소' : '준비 완료'}
            </button>
          ) : (
            <p className="text-center text-hanyang-stone">
              로비에 참가 중입니다...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
