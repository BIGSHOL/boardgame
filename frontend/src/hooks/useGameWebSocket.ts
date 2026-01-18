/**
 * WebSocket hook for real-time game synchronization
 */
import { useEffect, useRef, useCallback, useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useGameStore } from '../stores/gameStore'
import type { GameState } from '../types/game'

// WebSocket message types (must match backend)
export type MessageType =
  | 'game_state_update'
  | 'valid_actions_update'
  | 'your_turn'
  | 'turn_changed'
  | 'player_action'
  | 'action_result'
  | 'player_joined'
  | 'player_left'
  | 'player_reconnected'
  | 'game_started'
  | 'game_ended'
  | 'round_changed'
  | 'error'
  | 'ping'
  | 'pong'

export interface WebSocketMessage {
  type: MessageType
  data: Record<string, unknown>
  timestamp?: string
}

export interface UseGameWebSocketOptions {
  gameId: number
  onGameStateUpdate?: (gameState: GameState) => void
  onYourTurn?: () => void
  onTurnChanged?: (playerId: number, playerName: string) => void
  onPlayerJoined?: (playerId: number, username: string) => void
  onPlayerLeft?: (playerId: number, username: string) => void
  onGameEnded?: (winnerId: number, winnerName: string) => void
  onError?: (message: string) => void
}

export interface UseGameWebSocketReturn {
  isConnected: boolean
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error'
  error: string | null
  reconnect: () => void
  disconnect: () => void
}

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
const RECONNECT_DELAY = 3000
const MAX_RECONNECT_ATTEMPTS = 5
const PING_INTERVAL = 30000

export function useGameWebSocket(options: UseGameWebSocketOptions): UseGameWebSocketReturn {
  const { gameId, onGameStateUpdate, onYourTurn, onTurnChanged, onPlayerJoined, onPlayerLeft, onGameEnded, onError } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)

  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [error, setError] = useState<string | null>(null)

  const { accessToken } = useAuthStore()
  const { fetchGameState, fetchValidActions } = useGameStore()

  // Handle incoming messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)

      switch (message.type) {
        case 'game_state_update':
          if (message.data.game_state) {
            onGameStateUpdate?.(message.data.game_state as GameState)
            // Also update store directly
            useGameStore.setState({ gameState: message.data.game_state as GameState })
          }
          break

        case 'your_turn':
          onYourTurn?.()
          // Refresh valid actions when it becomes our turn
          fetchValidActions(gameId)
          break

        case 'turn_changed':
          onTurnChanged?.(
            message.data.current_player_id as number,
            message.data.current_player_name as string
          )
          break

        case 'player_joined':
          onPlayerJoined?.(
            message.data.player_id as number,
            message.data.username as string
          )
          break

        case 'player_left':
          onPlayerLeft?.(
            message.data.player_id as number,
            message.data.username as string
          )
          break

        case 'game_ended':
          onGameEnded?.(
            message.data.winner_id as number,
            message.data.winner_name as string
          )
          break

        case 'error':
          const errorMsg = message.data.message as string
          setError(errorMsg)
          onError?.(errorMsg)
          break

        case 'pong':
          // Keep-alive response received
          break

        default:
          console.log('Unhandled WebSocket message:', message.type)
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err)
    }
  }, [gameId, onGameStateUpdate, onYourTurn, onTurnChanged, onPlayerJoined, onPlayerLeft, onGameEnded, onError, fetchValidActions])

  // Start ping interval
  const startPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
    }
    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, PING_INTERVAL)
  }, [])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!accessToken || !gameId) {
      setError('Missing authentication or game ID')
      return
    }

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close()
    }

    setConnectionState('connecting')
    setError(null)

    const wsUrl = `${WS_BASE_URL}/ws/game/${gameId}?token=${accessToken}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log(`WebSocket connected to game ${gameId}`)
      setIsConnected(true)
      setConnectionState('connected')
      setError(null)
      reconnectAttemptsRef.current = 0
      startPingInterval()
    }

    ws.onmessage = handleMessage

    ws.onerror = (event) => {
      console.error('WebSocket error:', event)
      setError('WebSocket connection error')
      setConnectionState('error')
    }

    ws.onclose = (event) => {
      console.log(`WebSocket closed: ${event.code} ${event.reason}`)
      setIsConnected(false)
      setConnectionState('disconnected')

      // Clear ping interval
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
        pingIntervalRef.current = null
      }

      // Attempt reconnect if not intentionally closed
      if (event.code !== 1000 && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttemptsRef.current++
        console.log(`Reconnecting in ${RECONNECT_DELAY}ms (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`)

        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, RECONNECT_DELAY)
      }
    }

    wsRef.current = ws
  }, [accessToken, gameId, handleMessage, startPingInterval])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected')
      wsRef.current = null
    }
    setIsConnected(false)
    setConnectionState('disconnected')
    reconnectAttemptsRef.current = MAX_RECONNECT_ATTEMPTS // Prevent auto-reconnect
  }, [])

  // Reconnect manually
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0
    connect()
  }, [connect])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    if (accessToken && gameId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [accessToken, gameId]) // Intentionally not including connect/disconnect to prevent loops

  return {
    isConnected,
    connectionState,
    error,
    reconnect,
    disconnect,
  }
}

export default useGameWebSocket
