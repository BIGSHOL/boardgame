/**
 * Basic transition animation components
 */
import { motion, AnimatePresence } from 'framer-motion'
import type { ReactNode } from 'react'
import { variants, transitions } from './animationConfig'

interface TransitionProps {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
  show?: boolean
}

/**
 * Fade in animation wrapper
 */
export function FadeIn({ children, className, delay = 0, duration = 0.3, show = true }: TransitionProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className={className}
          initial="initial"
          animate="animate"
          exit="exit"
          variants={variants.fadeIn}
          transition={{ ...transitions.normal, delay, duration }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * Slide in animation wrapper (from bottom by default)
 */
export function SlideIn({
  children,
  className,
  delay = 0,
  duration = 0.3,
  show = true,
  direction = 'up',
}: TransitionProps & { direction?: 'up' | 'down' | 'left' | 'right' }) {
  const variantKey = `slide${direction.charAt(0).toUpperCase() + direction.slice(1)}` as keyof typeof variants

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className={className}
          initial="initial"
          animate="animate"
          exit="exit"
          variants={variants[variantKey]}
          transition={{ ...transitions.normal, delay, duration }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * Scale in animation wrapper
 */
export function ScaleIn({ children, className, delay = 0, duration = 0.3, show = true }: TransitionProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className={className}
          initial="initial"
          animate="animate"
          exit="exit"
          variants={variants.scaleIn}
          transition={{ ...transitions.bounce, delay }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * Pop in animation wrapper (more dramatic scale)
 */
export function PopIn({ children, className, delay = 0, show = true }: TransitionProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className={className}
          initial="initial"
          animate="animate"
          exit="exit"
          variants={variants.popIn}
          transition={{ ...transitions.bounce, delay }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
