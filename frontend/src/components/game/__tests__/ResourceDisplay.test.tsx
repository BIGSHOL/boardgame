import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ResourceDisplay } from '../ResourceDisplay'
import type { Resources } from '../../../types/game'

describe('ResourceDisplay', () => {
  const defaultResources: Resources = {
    wood: 2,
    stone: 2,
    tile: 0,
    ink: 0,
  }

  it('renders all four resource types', () => {
    render(<ResourceDisplay resources={defaultResources} />)

    expect(screen.getByText('2/10')).toBeInTheDocument() // wood
    expect(screen.getByText('0/6')).toBeInTheDocument() // tile
    expect(screen.getByText('0/4')).toBeInTheDocument() // ink
  })

  it('shows correct resource values', () => {
    const resources: Resources = {
      wood: 5,
      stone: 3,
      tile: 2,
      ink: 1,
    }
    render(<ResourceDisplay resources={resources} />)

    expect(screen.getByText('5/10')).toBeInTheDocument()
    expect(screen.getByText('3/10')).toBeInTheDocument()
    expect(screen.getByText('2/6')).toBeInTheDocument()
    expect(screen.getByText('1/4')).toBeInTheDocument()
  })

  it('hides max values when showMax is false', () => {
    render(<ResourceDisplay resources={defaultResources} showMax={false} />)

    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.queryByText('/10')).not.toBeInTheDocument()
  })

  it('shows resource icons', () => {
    render(<ResourceDisplay resources={defaultResources} />)

    expect(screen.getByLabelText('목재')).toBeInTheDocument()
    expect(screen.getByLabelText('석재')).toBeInTheDocument()
    expect(screen.getByLabelText('기와')).toBeInTheDocument()
    expect(screen.getByLabelText('먹')).toBeInTheDocument()
  })
})
