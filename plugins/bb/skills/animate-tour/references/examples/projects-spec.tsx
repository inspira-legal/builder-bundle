import { fireEvent, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderComponent } from '@tests/utils/render'
import type { PropsWithChildren } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ProjectsTourDialog } from '@/pages/Projects/components/ProjectsTourDialog'
import { LocalStorageKeys } from '@/shared/enums'

const captureMock = vi.fn()
const onCreateProjectMock = vi.fn()

vi.mock('@/lib/events', () => ({
  events: { track: (...args: unknown[]) => captureMock(...args) },
}))

vi.mock('@/stores/useFeatureFlags', () => ({
  useFeatureFlags: () => ({ feature: vi.fn(() => true), isReady: true }),
}))

vi.mock('@/stores/useFeatureFlags/FeatureFlagInit', () => ({
  FeatureFlagsInit: () => null,
}))

vi.mock('@/hooks/usePermission', () => ({
  usePermission: () => ({ hasPermission: () => false, permissions: null }),
}))

vi.mock('@/hooks/useAuth/context', () => ({
  AuthContext: {},
  AuthProvider: ({ children }: PropsWithChildren) => children,
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ isReady: true, me: null }),
}))

const dialog = () => screen.queryByTestId('projects-tour')

describe('pages/Projects/components/ProjectsTourDialog', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
    document.getElementById('root')?.removeAttribute('inert')
  })

  it('does not render when disabled', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={false} onCreateProject={onCreateProjectMock} />,
    )
    expect(dialog()).not.toBeInTheDocument()
  })

  it('does not render when already seen (localStorage)', async () => {
    localStorage.setItem(LocalStorageKeys.projectsTourSeen, 'true')
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )
    expect(dialog()).not.toBeInTheDocument()
  })

  it('renders on step 1 and captures a view impression', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )
    expect(dialog()).toBeInTheDocument()
    expect(screen.queryByTestId('projects-tour-back')).not.toBeInTheDocument()
    expect(captureMock).toHaveBeenCalledWith('projects_tour:impression:view', {})
  })

  it('advances through the 4 steps with Próximo and back with Voltar', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )

    await userEvent.click(screen.getByTestId('projects-tour-next'))
    expect(captureMock).toHaveBeenCalledWith('projects_tour:click:next', { step: 0 })
    expect(screen.getByTestId('projects-tour-back')).toBeInTheDocument()

    await userEvent.click(screen.getByTestId('projects-tour-back'))
    expect(captureMock).toHaveBeenCalledWith('projects_tour:click:prev', { step: 1 })
    expect(screen.queryByTestId('projects-tour-back')).not.toBeInTheDocument()
  })

  it('finishes on the last step: marks seen, captures finish and opens the create dialog', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )

    for (let i = 0; i < 3; i++) {
      await userEvent.click(screen.getByTestId('projects-tour-next'))
    }

    await userEvent.click(screen.getByTestId('projects-tour-next'))

    expect(captureMock).toHaveBeenCalledWith('projects_tour:click:finish', {})
    expect(localStorage.getItem(LocalStorageKeys.projectsTourSeen)).toBe('true')
    expect(onCreateProjectMock).toHaveBeenCalledOnce()
    expect(dialog()).not.toBeInTheDocument()
  })

  it('marks seen and captures dismiss when closed via the X button', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )

    await userEvent.click(screen.getByTestId('projects-tour-close'))

    expect(dialog()).not.toBeInTheDocument()
    expect(localStorage.getItem(LocalStorageKeys.projectsTourSeen)).toBe('true')
    expect(captureMock).toHaveBeenCalledWith('projects_tour:click:dismiss', {
      reason: 'close_button',
      step: 0,
    })
  })

  it('marks seen and captures dismiss on Escape, from the current step', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )

    await userEvent.click(screen.getByTestId('projects-tour-next'))
    fireEvent.keyDown(document, { key: 'Escape' })

    await waitFor(() => expect(dialog()).not.toBeInTheDocument())
    expect(localStorage.getItem(LocalStorageKeys.projectsTourSeen)).toBe('true')
    expect(captureMock).toHaveBeenCalledWith('projects_tour:click:dismiss', {
      reason: 'escape',
      step: 1,
    })
  })

  it('marks seen and captures dismiss on click outside the card', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )

    fireEvent.mouseDown(document.body)

    await waitFor(() => expect(dialog()).not.toBeInTheDocument())
    expect(captureMock).toHaveBeenCalledWith('projects_tour:click:dismiss', {
      reason: 'outside',
      step: 0,
    })
  })

  it('focuses the close button on open and traps Tab within the dialog', async () => {
    await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )

    const close = screen.getByTestId('projects-tour-close')
    const next = screen.getByTestId('projects-tour-next')

    expect(close).toHaveFocus()

    next.focus()
    fireEvent.keyDown(document, { key: 'Tab' })
    expect(close).toHaveFocus()

    close.focus()
    fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
    expect(next).toHaveFocus()
  })

  it('marks #root inert while open and restores it on close', async () => {
    const root = document.createElement('div')
    root.id = 'root'
    document.body.appendChild(root)

    const { unmount } = await renderComponent(
      <ProjectsTourDialog enabled={true} onCreateProject={onCreateProjectMock} />,
    )
    expect(root.hasAttribute('inert')).toBe(true)

    unmount()
    expect(root.hasAttribute('inert')).toBe(false)

    root.remove()
  })
})
