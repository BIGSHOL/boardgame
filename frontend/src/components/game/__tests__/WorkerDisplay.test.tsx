import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { WorkerDisplay } from '../WorkerDisplay'
import type { PlayerWorkers } from '../../../types/game'

describe('WorkerDisplay', () => {
  const defaultWorkers: PlayerWorkers = {
    apprentices: { total: 3, available: 3, placed: 0 },
    officials: { total: 2, available: 2, placed: 0 },
  }

  it('renders apprentice and official sections', () => {
    render(<WorkerDisplay workers={defaultWorkers} />)

    expect(screen.getByText('견습생')).toBeInTheDocument()
    expect(screen.getByText('관리')).toBeInTheDocument()
  })

  it('shows correct available counts', () => {
    render(<WorkerDisplay workers={defaultWorkers} />)

    expect(screen.getByText('3/3')).toBeInTheDocument() // apprentices
    expect(screen.getByText('2/2')).toBeInTheDocument() // officials
  })

  it('shows placed workers correctly', () => {
    const workers: PlayerWorkers = {
      apprentices: { total: 3, available: 1, placed: 2 },
      officials: { total: 2, available: 0, placed: 2 },
    }
    render(<WorkerDisplay workers={workers} />)

    expect(screen.getByText('1/3')).toBeInTheDocument() // apprentices
    expect(screen.getByText('0/2')).toBeInTheDocument() // officials
  })

  it('calls onSelectWorker when clicking apprentice', () => {
    const onSelectWorker = vi.fn()
    render(
      <WorkerDisplay workers={defaultWorkers} onSelectWorker={onSelectWorker} />
    )

    fireEvent.click(screen.getByLabelText('견습생 선택'))
    expect(onSelectWorker).toHaveBeenCalledWith('apprentice')
  })

  it('calls onSelectWorker when clicking official', () => {
    const onSelectWorker = vi.fn()
    render(
      <WorkerDisplay workers={defaultWorkers} onSelectWorker={onSelectWorker} />
    )

    fireEvent.click(screen.getByLabelText('관리 선택'))
    expect(onSelectWorker).toHaveBeenCalledWith('official')
  })

  it('disables button when no workers available', () => {
    const workers: PlayerWorkers = {
      apprentices: { total: 3, available: 0, placed: 3 },
      officials: { total: 2, available: 2, placed: 0 },
    }
    render(<WorkerDisplay workers={workers} />)

    expect(screen.getByLabelText('견습생 선택')).toBeDisabled()
    expect(screen.getByLabelText('관리 선택')).not.toBeDisabled()
  })

  it('disables all when disabled prop is true', () => {
    render(<WorkerDisplay workers={defaultWorkers} disabled />)

    expect(screen.getByLabelText('견습생 선택')).toBeDisabled()
    expect(screen.getByLabelText('관리 선택')).toBeDisabled()
  })

  it('shows selected state for apprentice', () => {
    render(
      <WorkerDisplay workers={defaultWorkers} selectedWorker="apprentice" />
    )

    const apprenticeButton = screen.getByLabelText('견습생 선택')
    expect(apprenticeButton).toHaveAttribute('aria-pressed', 'true')
  })

  it('shows selected state for official', () => {
    render(<WorkerDisplay workers={defaultWorkers} selectedWorker="official" />)

    const officialButton = screen.getByLabelText('관리 선택')
    expect(officialButton).toHaveAttribute('aria-pressed', 'true')
  })
})
