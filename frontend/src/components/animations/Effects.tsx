/**
 * Animation effect components
 */
import { motion } from 'framer-motion'
import type { ReactNode } from 'react'
import { variants } from './animationConfig'

interface EffectProps {
  children: ReactNode
  className?: string
  active?: boolean
}

/**
 * Pulsing animation effect
 */
export function PulseEffect({ children, className, active = true }: EffectProps) {
  return (
    <motion.div
      className={className}
      animate={active ? 'animate' : undefined}
      variants={variants.pulse}
    >
      {children}
    </motion.div>
  )
}

/**
 * Shake animation effect (for errors or invalid actions)
 */
export function ShakeEffect({ children, className, active = false }: EffectProps) {
  return (
    <motion.div
      className={className}
      animate={active ? 'animate' : undefined}
      variants={variants.shake}
    >
      {children}
    </motion.div>
  )
}

/**
 * Glow animation effect (for highlighting)
 */
export function GlowEffect({ children, className, active = true }: EffectProps) {
  return (
    <motion.div
      className={className}
      animate={active ? 'animate' : undefined}
      variants={variants.glow}
    >
      {children}
    </motion.div>
  )
}

/**
 * Hover scale effect
 */
export function HoverScale({
  children,
  className,
  scale = 1.05
}: EffectProps & { scale?: number }) {
  return (
    <motion.div
      className={className}
      whileHover={{ scale }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.div>
  )
}
