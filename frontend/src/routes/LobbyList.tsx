import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface Lobby {
  id: number;
  name: string;
  host_id: number;
  invite_code: string;
  status: string;
  max_players: number;
  players: Array<{
    id: number;
    username: string;
    is_host: boolean;
  }>;
  created_at: string;
}

export default function LobbyList() {
  const navigate = useNavigate();
  const { isAuthenticated, tokens } = useAuthStore();
  const [lobbies, setLobbies] = useState<Lobby[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newLobbyName, setNewLobbyName] = useState('');
  const [inviteCode, setInviteCode] = useState('');

  useEffect(() => {
    fetchLobbies();
  }, []);

  const fetchLobbies = async () => {
    try {
      const response = await fetch('/api/v1/lobbies');
      const data = await response.json();
      setLobbies(data.lobbies || []);
    } catch (err) {
      setError('로비 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateLobby = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokens?.access_token) return;

    try {
      const response = await fetch('/api/v1/lobbies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.access_token}`,
        },
        body: JSON.stringify({ name: newLobbyName, max_players: 4 }),
      });

      if (response.ok) {
        const lobby = await response.json();
        navigate(`/lobby/${lobby.id}`);
      } else {
        const error = await response.json();
        setError(error.detail || '로비 생성에 실패했습니다.');
      }
    } catch (err) {
      setError('로비 생성에 실패했습니다.');
    }
  };

  const handleJoinByCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokens?.access_token || !inviteCode) return;

    try {
      // First, find lobby by invite code
      const findResponse = await fetch(`/api/v1/lobbies/join/${inviteCode}`);
      if (!findResponse.ok) {
        setError('유효하지 않은 초대 코드입니다.');
        return;
      }

      const lobby = await findResponse.json();

      // Join the lobby
      const joinResponse = await fetch(`/api/v1/lobbies/${lobby.id}/join`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });

      if (joinResponse.ok) {
        navigate(`/lobby/${lobby.id}`);
      } else {
        const error = await joinResponse.json();
        setError(error.detail || '로비 참가에 실패했습니다.');
      }
    } catch (err) {
      setError('로비 참가에 실패했습니다.');
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

  return (
    <div className="min-h-screen bg-hanyang-cream p-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <div className="flex justify-between items-center">
            <h1 className="font-display text-3xl text-hanyang-navy">
              게임 로비
            </h1>
            <div className="space-x-2">
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary"
              >
                로비 생성
              </button>
              <Link to="/" className="btn-secondary">
                홈으로
              </Link>
            </div>
          </div>
        </header>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
            <button onClick={() => setError(null)} className="float-right">×</button>
          </div>
        )}

        {/* Join by invite code */}
        <div className="card mb-6">
          <h3 className="font-display text-lg text-hanyang-navy mb-3">
            초대 코드로 참가
          </h3>
          <form onSubmit={handleJoinByCode} className="flex gap-2">
            <input
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              placeholder="초대 코드 (6자리)"
              maxLength={6}
              className="input flex-1"
            />
            <button type="submit" className="btn-primary" disabled={inviteCode.length !== 6}>
              참가
            </button>
          </form>
        </div>

        {/* Lobby list */}
        <div className="card">
          <h3 className="font-display text-lg text-hanyang-navy mb-4">
            대기 중인 로비 ({lobbies.length})
          </h3>

          {isLoading ? (
            <p className="text-hanyang-stone">로딩 중...</p>
          ) : lobbies.length === 0 ? (
            <p className="text-hanyang-stone">대기 중인 로비가 없습니다.</p>
          ) : (
            <div className="space-y-3">
              {lobbies.map((lobby) => (
                <div
                  key={lobby.id}
                  className="border border-hanyang-stone/30 rounded-lg p-4 flex justify-between items-center"
                >
                  <div>
                    <h4 className="font-medium text-hanyang-navy">{lobby.name}</h4>
                    <p className="text-sm text-hanyang-stone">
                      호스트: {lobby.players.find(p => p.is_host)?.username || '알 수 없음'}
                      {' • '}
                      {lobby.players.length}/{lobby.max_players}명
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      const response = await fetch(`/api/v1/lobbies/${lobby.id}/join`, {
                        method: 'POST',
                        headers: {
                          'Authorization': `Bearer ${tokens?.access_token}`,
                        },
                      });
                      if (response.ok) {
                        navigate(`/lobby/${lobby.id}`);
                      }
                    }}
                    className="btn-secondary"
                  >
                    참가
                  </button>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={fetchLobbies}
            className="mt-4 text-hanyang-gold hover:underline"
          >
            새로고침
          </button>
        </div>

        {/* Create lobby modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="card max-w-md w-full mx-4">
              <h3 className="font-display text-xl text-hanyang-navy mb-4">
                새 로비 생성
              </h3>
              <form onSubmit={handleCreateLobby}>
                <div className="mb-4">
                  <label htmlFor="lobbyName" className="block text-sm font-medium text-hanyang-navy mb-1">
                    로비 이름
                  </label>
                  <input
                    id="lobbyName"
                    type="text"
                    value={newLobbyName}
                    onChange={(e) => setNewLobbyName(e.target.value)}
                    required
                    maxLength={50}
                    className="input"
                    placeholder="한양 건설 제1국"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="btn-secondary"
                  >
                    취소
                  </button>
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={!newLobbyName.trim()}
                  >
                    생성
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
