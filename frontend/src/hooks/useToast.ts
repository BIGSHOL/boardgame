/**
 * Toast notification hook
 */
import { useState, useCallback } from 'react'
import type { ToastType } from '../components/ui/Toast'

interface ToastState {
  message: string
  type: ToastType
  isVisible: boolean
}

export function useToast() {
  const [toast, setToast] = useState<ToastState>({
    message: '',
    type: 'info',
    isVisible: false,
  })

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    setToast({
      message,
      type,
      isVisible: true,
    })
  }, [])

  const hideToast = useCallback(() => {
    setToast((prev) => ({ ...prev, isVisible: false }))
  }, [])

  // Convenience methods
  const showInfo = useCallback((message: string) => showToast(message, 'info'), [showToast])
  const showSuccess = useCallback((message: string) => showToast(message, 'success'), [showToast])
  const showWarning = useCallback((message: string) => showToast(message, 'warning'), [showToast])
  const showError = useCallback((message: string) => showToast(message, 'error'), [showToast])
  const showTurnNotification = useCallback((message: string) => showToast(message, 'turn'), [showToast])

  return {
    toast,
    showToast,
    hideToast,
    showInfo,
    showSuccess,
    showWarning,
    showError,
    showTurnNotification,
  }
}

export default useToast
