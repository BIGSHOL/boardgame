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

    // Check resource icons exist by title attribute
    expect(screen.getByTitle('목재')).toBeInTheDocument()
    expect(screen.getByTitle('석재')).toBeInTheDocument()
    expect(screen.getByTitle('기와')).toBeInTheDocument()
    expect(screen.getByTitle('먹')).toBeInTheDocument()
  })

  it('shows correct resource values', () => {
    const resources: Resources = {
      wood: 5,
      stone: 3,
      tile: 2,
      ink: 1,
    }
    render(<ResourceDisplay resources={resources} />)

    // Check values are displayed (text is split across elements)
    const woodContainer = screen.getByTitle('목재')
    expect(woodContainer).toHaveTextContent('5')

    const stoneContainer = screen.getByTitle('석재')
    expect(stoneContainer).toHaveTextContent('3')

    const tileContainer = screen.getByTitle('기와')
    expect(tileContainer).toHaveTextContent('2')

    const inkContainer = screen.getByTitle('먹')
    expect(inkContainer).toHaveTextContent('1')
  })

  it('hides max values when showMax is false', () => {
    render(<ResourceDisplay resources={defaultResources} showMax={false} />)

    const woodContainer = screen.getByTitle('목재')
    expect(woodContainer).toHaveTextContent('2')
    expect(woodContainer).not.toHaveTextContent('/10')
  })

  it('shows resource icons', () => {
    render(<ResourceDisplay resources={defaultResources} />)

    expect(screen.getByLabelText('목재')).toBeInTheDocument()
    expect(screen.getByLabelText('석재')).toBeInTheDocument()
    expect(screen.getByLabelText('기와')).toBeInTheDocument()
    expect(screen.getByLabelText('먹')).toBeInTheDocument()
  })
})
