import { Button } from '@inspira-legal/ui/Button'
import { Icon } from '@inspira-legal/ui/Icon'
import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Trans, useTranslation } from 'react-i18next'

import { useHeadlessModal, type HeadlessModalDismissReason } from '@/hooks/useHeadlessModal'
import useLocalStorage from '@/hooks/useLocalStorage'
import { events } from '@/lib/events'
import { LocalStorageKeys } from '@/shared/enums'

import { STEP_COUNT, StepArt } from './StepArt'
import type { ProjectsTourDialogProps } from './types'

type DismissReason = 'close_button' | HeadlessModalDismissReason

const TITLE_ID = 'projects-tour-title'
const TOTAL_STEPS = STEP_COUNT
const LAST_STEP = TOTAL_STEPS - 1

// Dialog entrance + the step-art animations (same vocabulary as the Análise em
// Tabela tour — see StepArt.tsx for where each is applied). Reveals use
// `forwards` so they land on a fully-opaque resting state; only the looping
// cues (cursor, CTA glow, the card moving between phases) repeat.
// The reduced-motion guard collapses everything to its end state, which is the
// visible resting state for every reveal — including `ptd-taskMove`, whose 100%
// frame puts the card back in its source column. It zeroes `animation-delay`
// too: the staggered reveals start at opacity 0, so keeping their delays would
// leave the later rows blank for up to ~0.75s with nothing animating in.
const KEYFRAMES = `
@keyframes ptd-dlgIn{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:none}}
@keyframes ptd-stepIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes ptd-pop{0%{opacity:0;transform:translateY(6px) scale(.94)}60%{opacity:1}100%{opacity:1;transform:none}}
@keyframes ptd-cursorTap{0%,100%{transform:translate(0,0)}45%{transform:translate(-2px,-2px)}55%{transform:translate(1px,1px)}}
@keyframes ptd-glowPulse{0%,100%{box-shadow:0 0 0 0 rgba(106,151,235,.45)}50%{box-shadow:0 0 0 7px rgba(106,151,235,0)}}
@keyframes ptd-taskMove{0%,12%{opacity:1;transform:translateX(0) rotate(0)}42%,74%{opacity:1;transform:translateX(120px) rotate(1.5deg)}86%{opacity:0;transform:translateX(120px) rotate(1.5deg)}87%{opacity:0;transform:translateX(0) rotate(0)}100%{opacity:1;transform:translateX(0) rotate(0)}}
@keyframes ptd-checkPop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes ptd-barFill{from{width:0}to{width:67%}}
@keyframes ptd-sheetRise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.ptd-scope,.ptd-scope *{animation-duration:.01ms!important;animation-delay:0s!important;animation-iteration-count:1!important}}
`

// Literal tuples (not a template-string lookup) so each entry stays a key
// i18next-typescript can validate against the locale files.
const TITLE_KEYS = [
  'projects.tour.step1.title',
  'projects.tour.step2.title',
  'projects.tour.step3.title',
  'projects.tour.step4.title',
] as const
const BODY_KEYS = [
  'projects.tour.step1.body',
  'projects.tour.step2.body',
  'projects.tour.step3.body',
  'projects.tour.step4.body',
] as const

// Same fixed card width as the Análise em Tabela tour so both onboarding modals
// read as one family; a named px value because the step art is laid out against it.
const CARD_WIDTH = 452

// Hand-rolled instead of the DS `Dialog`/`TutorialGuide` for the same reason as
// TabularTourDialog: the animated illustrations need live CSS, not an image/gif
// media slot, and the tour owns its own step chrome. The modal machinery itself
// (focus trap, Escape, click-outside, `inert`, focus restore) lives in
// `useHeadlessModal`, extracted from this third copy of it.
export const ProjectsTourDialog = ({ enabled, onCreateProject }: ProjectsTourDialogProps) => {
  const { t } = useTranslation()
  const [seen, setSeen] = useLocalStorage(LocalStorageKeys.projectsTourSeen, false)
  const [step, setStep] = useState(0)

  const open = enabled && !seen
  const nextRef = useRef<HTMLButtonElement>(null)

  const markSeen = useCallback(() => {
    // useLocalStorage persists via a useEffect, which may not run before the
    // finish path unmounts this dialog through onCreateProject — write through
    // synchronously too.
    localStorage.setItem(LocalStorageKeys.projectsTourSeen, 'true')
    setSeen(true)
  }, [setSeen])

  const dismiss = useCallback(
    (reason: DismissReason) => {
      events.track('projects_tour:click:dismiss', { reason, step })
      markSeen()
    },
    [markSeen, step],
  )

  const { cardRef, closeRef, skipFocusRestore } = useHeadlessModal({ open, onDismiss: dismiss })

  const next = useCallback(() => {
    if (step < LAST_STEP) {
      events.track('projects_tour:click:next', { step })
      setStep((s) => s + 1)
      return
    }
    events.track('projects_tour:click:finish', {})
    // O CreateProjectDialog assume o foco em seguida; devolvê-lo ao gatilho
    // roubaria o foco do diálogo que acabou de abrir.
    skipFocusRestore()
    markSeen()
    onCreateProject()
  }, [step, markSeen, onCreateProject, skipFocusRestore])

  const prev = useCallback(() => {
    events.track('projects_tour:click:prev', { step })
    // The "Voltar" button only renders while step > 0, so going 1→0 unmounts the
    // very element that has focus — dropping it to <body> and breaking the trap.
    // Move focus to the always-present "Próximo" button first.
    if (step === 1) {
      nextRef.current?.focus()
    }
    setStep((s) => Math.max(0, s - 1))
  }, [step])

  useEffect(() => {
    if (open) events.track('projects_tour:impression:view', {})
  }, [open])

  if (!open) return null

  return createPortal(
    // `z-(--z-dialog)` (1310), not the `z-dialog` class the tabular dialogs use:
    // that class does not exist in the DS (the token is `--z-dialog`), so the
    // overlay ended up at `z-index: auto` and the app header (`sticky z-10`) and
    // sidebar (`z-(--z-sidebar)`, 1100) painted on top of the dim.
    <div className='fixed inset-0 z-(--z-dialog) flex items-center justify-center bg-navy-base-dark/55 backdrop-blur-[3px]'>
      <style>{KEYFRAMES}</style>
      <div
        ref={cardRef}
        role='dialog'
        aria-modal='true'
        aria-labelledby={TITLE_ID}
        data-test='projects-tour'
        style={{ width: CARD_WIDTH }}
        className='ptd-scope relative [animation:ptd-dlgIn_.28s_cubic-bezier(.25,1,.5,1)_both] overflow-hidden rounded-xl bg-neutral-1'
      >
        <Button
          type='button'
          color='transparent'
          iconOnly
          onClick={() => dismiss('close_button')}
          data-test='projects-tour-close'
          aria-label={t('common.close')}
          className='absolute top-3.5 right-3.5 z-[3]'
          ref={closeRef}
        >
          <Icon name='X' label={null} size='sm' />
        </Button>

        <div className='px-6 pt-5.5 pb-4.5'>
          <div
            aria-hidden='true'
            className='mb-4.5 h-[212px] overflow-hidden rounded-xl border border-neutral-3 bg-linear-to-b from-sky-2 to-neutral-1'
          >
            <StepArt step={step} />
          </div>

          <div className='mb-3.5 inline-flex items-center gap-1.5 rounded-full bg-sky-2 px-2.5 py-1'>
            <span className='h-1.5 w-1.5 rounded-full bg-sky-9' />
            <span className='text-caption-sm font-sans font-medium text-navy-3'>
              {t('projects.tour.badge')}
            </span>
          </div>
          {/* aria-live so screen readers announce the new title/body when the step
              changes (the DOM swaps in place without moving focus). */}
          <div aria-live='polite'>
            <h2
              id={TITLE_ID}
              className='mb-2 text-subtitle font-sans font-semibold tracking-[-0.01em] text-neutral-10'
            >
              {t(TITLE_KEYS[step] ?? TITLE_KEYS[0])}
            </h2>
            <p className='text-body-sm font-sans text-neutral-9'>
              <Trans i18nKey={BODY_KEYS[step] ?? BODY_KEYS[0]} />
            </p>
          </div>
        </div>

        <div className='flex items-center gap-2.5 px-6 pb-5.5'>
          {step > 0 && (
            <Button
              type='button'
              color='gray'
              size='lg'
              onClick={prev}
              data-test='projects-tour-back'
              className='shrink-0'
            >
              {t('common.back')}
            </Button>
          )}
          <span
            role='status'
            className='text-caption-sm flex-1 font-sans whitespace-nowrap text-neutral-6'
          >
            {t('projects.tour.progress', { current: step + 1, total: TOTAL_STEPS })}
          </span>
          <Button
            ref={nextRef}
            type='button'
            size='lg'
            onClick={next}
            data-test='projects-tour-next'
            className='shrink-0 whitespace-nowrap'
            endIcon={<Icon name='ArrowRight' label={null} size='sm' />}
          >
            {step === LAST_STEP ? t('projects.tour.finish') : t('common.tutorial.next')}
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
