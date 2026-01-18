/**
 * Animation configuration and presets
 */
import type { Transition, Variants } from 'framer-motion'

// Spring presets
export const spring = {
  gentle: { type: 'spring', stiffness: 120, damping: 14 },
  bouncy: { type: 'spring', stiffness: 300, damping: 10 },
  stiff: { type: 'spring', stiffness: 400, damping: 20 },
  slow: { type: 'spring', stiffness: 80, damping: 20 },
} as const

// Transition presets
export const transitions: Record<string, Transition> = {
  fast: { duration: 0.15, ease: 'easeOut' },
  normal: { duration: 0.3, ease: 'easeInOut' },
  slow: { duration: 0.5, ease: 'easeInOut' },
  bounce: spring.bouncy,
  gentle: spring.gentle,
}

// Common animation variants
export const variants: Record<string, Variants> = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  },
  slideDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
  },
  slideLeft: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  },
  slideRight: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 },
  },
  popIn: {
    initial: { opacity: 0, scale: 0.5 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.5 },
  },
  pulse: {
    animate: {
      scale: [1, 1.05, 1],
      transition: { duration: 0.5, repeat: Infinity, repeatDelay: 1 },
    },
  },
  shake: {
    animate: {
      x: [0, -5, 5, -5, 5, 0],
      transition: { duration: 0.4 },
    },
  },
  glow: {
    animate: {
      boxShadow: [
        '0 0 0 0 rgba(255, 200, 100, 0)',
        '0 0 20px 10px rgba(255, 200, 100, 0.4)',
        '0 0 0 0 rgba(255, 200, 100, 0)',
      ],
      transition: { duration: 1.5, repeat: Infinity },
    },
  },
}

// Stagger children animation
export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
}

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
}
