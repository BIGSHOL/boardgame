/**
 * Toast notification component
 */
import { motion, AnimatePresence } from 'framer-motion'
import { useEffect } from 'react'

export type ToastType = 'info' | 'success' | 'warning' | 'error' | 'turn'

interface ToastProps {
  message: string
  type?: ToastType
  isVisible: boolean
  onClose: () => void
  duration?: number
}

const typeStyles: Record<ToastType, string> = {
  info: 'bg-blue-500 text-white',
  success: 'bg-green-500 text-white',
  warning: 'bg-yellow-500 text-yellow-900',
  error: 'bg-red-500 text-white',
  turn: 'bg-hanyang-gold text-hanyang-brown',
}

const typeIcons: Record<ToastType, string> = {
  info: 'i',
  success: '✓',
  warning: '!',
  error: '✕',
  turn: '⏱',
}

export function Toast({
  message,
  type = 'info',
  isVisible,
  onClose,
  duration = 3000,
}: ToastProps) {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(onClose, duration)
      return () => clearTimeout(timer)
    }
  }, [isVisible, duration, onClose])

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 ${typeStyles[type]}`}
          initial={{ opacity: 0, y: -50, x: 50 }}
          animate={{ opacity: 1, y: 0, x: 0 }}
          exit={{ opacity: 0, y: -20, x: 50 }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        >
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-white/20 font-bold">
            {typeIcons[type]}
          </span>
          <span className="font-medium">{message}</span>
          <button
            type="button"
            onClick={onClose}
            className="ml-2 w-6 h-6 flex items-center justify-center rounded-full hover:bg-white/20 transition-colors"
            aria-label="닫기"
          >
            ✕
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default Toast
