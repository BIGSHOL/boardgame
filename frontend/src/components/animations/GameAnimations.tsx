/**
 * Game-specific animation components
 */
import { motion, AnimatePresence } from 'framer-motion'
import type { ReactNode } from 'react'
import { spring } from './animationConfig'

interface GameAnimationProps {
  children: ReactNode
  className?: string
}

/**
 * Animation for placing a tile on the board
 */
export function TilePlaceAnimation({
  children,
  className,
  isNew = false,
}: GameAnimationProps & { isNew?: boolean }) {
  if (!isNew) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, scale: 0.5, y: -50 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{
        ...spring.bouncy,
        opacity: { duration: 0.2 },
      }}
    >
      {children}
    </motion.div>
  )
}

/**
 * Animation for placing a worker
 */
export function WorkerPlaceAnimation({
  children,
  className,
  isNew = false,
}: GameAnimationProps & { isNew?: boolean }) {
  if (!isNew) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, scale: 0, rotate: -180 }}
      animate={{ opacity: 1, scale: 1, rotate: 0 }}
      transition={{
        ...spring.bouncy,
        rotate: { type: 'spring', stiffness: 200, damping: 15 },
      }}
    >
      {children}
    </motion.div>
  )
}

/**
 * Turn indicator animation (glowing border)
 */
export function TurnIndicator({
  children,
  className,
  isActive = false,
}: GameAnimationProps & { isActive?: boolean }) {
  return (
    <motion.div
      className={className}
      animate={
        isActive
          ? {
              boxShadow: [
                '0 0 0 0 rgba(34, 197, 94, 0)',
                '0 0 0 4px rgba(34, 197, 94, 0.4)',
                '0 0 0 0 rgba(34, 197, 94, 0)',
              ],
            }
          : { boxShadow: '0 0 0 0 rgba(34, 197, 94, 0)' }
      }
      transition={
        isActive
          ? { duration: 1.5, repeat: Infinity, ease: 'easeInOut' }
          : { duration: 0.2 }
      }
    >
      {children}
    </motion.div>
  )
}

/**
 * Score change animation
 */
export function ScoreChange({
  value,
  className,
}: {
  value: number
  className?: string
}) {
  const isPositive = value > 0
  const color = isPositive ? 'text-green-500' : 'text-red-500'

  return (
    <AnimatePresence>
      {value !== 0 && (
        <motion.span
          className={`${color} font-bold ${className}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
        >
          {isPositive ? '+' : ''}{value}
        </motion.span>
      )}
    </AnimatePresence>
  )
}

/**
 * Card flip animation
 */
export function CardFlip({
  children,
  className,
  isFlipped = false,
  backContent,
}: GameAnimationProps & { isFlipped?: boolean; backContent?: ReactNode }) {
  return (
    <div className={`relative ${className}`} style={{ perspective: 1000 }}>
      <motion.div
        className="w-full h-full"
        animate={{ rotateY: isFlipped ? 180 : 0 }}
        transition={{ duration: 0.6, type: 'spring', stiffness: 100 }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div
          className="absolute inset-0"
          style={{ backfaceVisibility: 'hidden' }}
        >
          {children}
        </div>
        <div
          className="absolute inset-0"
          style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
        >
          {backContent}
        </div>
      </motion.div>
    </div>
  )
}

/**
 * List item animation for staggered lists
 */
export function StaggerList({
  children,
  className,
}: {
  children: ReactNode[]
  className?: string
}) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.1,
          },
        },
      }}
    >
      {children.map((child, index) => (
        <motion.div
          key={index}
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 },
          }}
          transition={{ duration: 0.3 }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}
