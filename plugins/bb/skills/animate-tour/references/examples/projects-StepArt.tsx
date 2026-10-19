import { Icon } from '@inspira-legal/ui/Icon'
import { cx } from 'class-variance-authority'
import { t } from 'i18next'
import type { ReactNode } from 'react'

// Animated illustrations for the Gestão de Projetos tour, built to match the
// Análise em Tabela tour (TabularTourDialog/StepArt.tsx): same illustration
// palette, same reveal vocabulary, same "one idea per step" framing. The palette
// is the DS token scale, and the two files declare the same aliases so the
// modals stay one family. Keyframes (ptd-*) live in index.tsx.
const BORDER = 'border-neutral-5'
const BORDER_SOFT = 'border-neutral-3'
const BORDER_DASHED = 'border-neutral-6'
const TEXT_DARK = 'text-neutral-10'
const TEXT_MUTED = 'text-neutral-9'
const TEXT_FAINT = 'text-neutral-8'
const BG_TABLE = 'bg-neutral-2'
const ACCENT_BLUE = 'text-sky-10'
const POP = '[animation:ptd-pop_.4s_cubic-bezier(.25,1,.5,1)_forwards]'
const STEP_IN = '[animation:ptd-stepIn_.3s_cubic-bezier(.25,1,.5,1)_both]'

// The traveling card in step 2 moves exactly one column + one gap to the right
// (ptd-taskMove translates 120px), so these two must stay in sync.
const PHASE_COL_WIDTH = 112
const PHASE_CARD_HEIGHT = 52

// Cursor glyph; ptd-cursorTap easing lives in index.tsx. Position via className.
const Cursor = ({ className }: { className?: string }) => (
  <svg
    width='20'
    height='20'
    viewBox='0 0 24 24'
    fill='var(--color-navy-base-dark)'
    stroke='var(--color-neutral-1)'
    strokeWidth='1.2'
    aria-hidden='true'
    className={cx(
      'absolute [animation:ptd-cursorTap_1.6s_ease-in-out_infinite] [filter:drop-shadow(0_2px_3px_rgba(7,12,33,0.3))]',
      className,
    )}
  >
    <path d='M5 3l6.5 16 2.2-6.6L20 10.5 5 3z' />
  </svg>
)

const StepCreate = () => (
  <div className={cx('flex h-full flex-col items-center justify-center gap-3.5', STEP_IN)}>
    <div
      className={cx(
        'flex w-[220px] flex-col items-center gap-2.5 rounded-xl border-[1.5px] border-dashed bg-neutral-1 px-4.5 py-4.5',
        BORDER_DASHED,
      )}
    >
      <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-neutral-3'>
        <Icon name='FolderKanban' label={null} size='sm' className={TEXT_FAINT} />
      </div>
      <p className={cx('text-caption-sm', TEXT_FAINT)}>{t('projects.tour.step1.title')}</p>
      <span className='relative inline-flex'>
        <span className='text-button inline-flex h-[38px] [animation:ptd-glowPulse_2s_ease-in-out_infinite] items-center gap-1.5 rounded-md bg-navy-3 px-4.5 font-medium whitespace-nowrap text-neutral-1'>
          <Icon name='Plus' label={null} size='sm' />
          {t('projects.tour.step1.artCta')}
        </span>
        <Cursor className='-right-3.5 -bottom-3.5' />
      </span>
    </div>
  </div>
)

const PhaseColumn = ({
  name,
  accentClassName,
  delay,
  className,
  children,
}: {
  name: string
  accentClassName: string
  delay: string
  className?: string
  children: ReactNode
}) => (
  <div
    style={{ animationDelay: delay, width: PHASE_COL_WIDTH }}
    className={cx(
      'flex flex-col rounded-md border border-t-4 bg-neutral-1 opacity-0',
      BORDER,
      accentClassName,
      POP,
      className,
    )}
  >
    <p className={cx('text-caption-sm truncate px-1.5 py-1.5 font-semibold', TEXT_MUTED)}>{name}</p>
    <div className='flex flex-col gap-1.5 px-1.5 pb-1.5'>{children}</div>
  </div>
)

const MiniTask = ({
  title,
  dotClassName,
  className,
  withCursor = false,
}: {
  title: string
  dotClassName: string
  className?: string
  withCursor?: boolean
}) => (
  <div
    style={{ height: PHASE_CARD_HEIGHT }}
    className={cx(
      'relative flex flex-col rounded-sm border bg-neutral-1 px-1.5 py-1.5',
      BORDER,
      className,
    )}
  >
    <span className={cx('mb-1 h-1.5 w-1.5 shrink-0 rounded-full', dotClassName)} />
    <p className={cx('text-caption-sm line-clamp-2 leading-tight', TEXT_DARK)}>{title}</p>
    {withCursor && <Cursor className='-right-2 -bottom-2' />}
  </div>
)

const StepPhases = () => (
  <div className='flex h-full items-center justify-center'>
    <div className='flex gap-2'>
      {/* z-[3]: each column's opacity reveal makes it a stacking context, so the
          card below — which slides out of this column and over the next one —
          would otherwise be painted over by the later siblings' backgrounds.
          Raising the whole source column keeps the moving card on top; the
          columns' boxes never overlap, so nothing else changes visually. */}
      <PhaseColumn
        name={t('projects.phases.triage')}
        accentClassName='border-t-warning-6'
        delay='0s'
        className='relative z-[3]'
      >
        {/* In flow, so its space stays reserved while it slides away and the
            columns keep the same height across the loop. */}
        <MiniTask
          title={t('projects.tour.step2.artTask1')}
          dotClassName='bg-critical-7'
          className='[animation:ptd-taskMove_3.6s_cubic-bezier(.4,0,.2,1)_infinite]'
          withCursor
        />
      </PhaseColumn>
      <PhaseColumn
        name={t('projects.phases.strategy')}
        accentClassName='border-t-sky-6'
        delay='.15s'
      >
        <div
          style={{ height: PHASE_CARD_HEIGHT }}
          className='rounded-sm border-[1.5px] border-dashed border-sky-5 bg-sky-1'
        />
      </PhaseColumn>
      <PhaseColumn
        name={t('projects.phases.execution')}
        accentClassName='border-t-blue-6'
        delay='.3s'
      >
        <MiniTask title={t('projects.tour.step2.artTask2')} dotClassName='bg-warning-7' />
      </PhaseColumn>
    </div>
  </div>
)

const ChecklistItem = ({
  label,
  delay,
  done = false,
}: {
  label: string
  delay?: string
  done?: boolean
}) => (
  <div className='flex items-center gap-1.5'>
    {done ? (
      <span
        style={{ animationDelay: delay }}
        className='flex h-3.5 w-3.5 shrink-0 [animation:ptd-checkPop_.28s_cubic-bezier(.25,1,.5,1)_forwards] items-center justify-center rounded-xs bg-success-6 opacity-0'
      >
        {/* `size`, not an `h-*`/`w-*` className: `Icon` composes its classes with
            cva (no tailwind-merge), so a size class only joins the variant's
            instead of replacing it and Tailwind's own order wins — an `h-2` here
            still rendered the 20px `md` default, overflowing this box by 4px on
            every side. `strokeWidth` thickens the 1px stroke, which all but
            disappears once the 24px glyph is scaled down to 12. */}
        <Icon name='Check' label={null} size='xs' strokeWidth={3} className='text-neutral-1' />
      </span>
    ) : (
      <span className={cx('h-3.5 w-3.5 shrink-0 rounded-xs border', BORDER_DASHED)} />
    )}
    <span
      className={cx('text-caption-sm truncate', done ? cx(TEXT_FAINT, 'line-through') : TEXT_DARK)}
    >
      {label}
    </span>
  </div>
)

const getInitials = (name: string) =>
  name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')

const StepTask = () => {
  const assignee = t('projects.tour.step3.artAssignee')

  return (
    <div className='flex h-full items-center justify-center'>
      <div className={cx('w-[288px] rounded-lg border bg-neutral-1 px-3 py-2.5', BORDER, STEP_IN)}>
        <div className='mb-1.5 flex items-center justify-between'>
          <span
            className={cx(
              'text-caption-sm inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 font-medium',
              BORDER_SOFT,
              TEXT_DARK,
            )}
          >
            <span className='h-1.5 w-1.5 rounded-full bg-warning-7' />
            {t('projects.taskCard.priority.high')}
          </span>
          <span className={cx('text-caption-sm inline-flex items-center gap-1', TEXT_MUTED)}>
            <Icon name='Calendar' label={null} size='xs' />
            {t('projects.tour.step3.artDueDate')}
          </span>
        </div>
        <p className={cx('text-body-sm leading-tight font-medium', TEXT_DARK)}>
          {t('projects.tour.step3.artTaskTitle')}
        </p>
        <div className='mt-1.5 flex items-center gap-1.5'>
          <span className='text-caption-sm flex h-5 w-5 items-center justify-center rounded-full bg-sky-3 font-medium text-[var(--gradient-4c-to)]'>
            {getInitials(assignee)}
          </span>
          <span className={cx('text-caption-sm', TEXT_MUTED)}>{assignee}</span>
        </div>
        <div className={cx('mt-2 border-t pt-1.5', BORDER_SOFT)}>
          <div className={cx('mb-0.5 flex items-center gap-1.5', TEXT_MUTED)}>
            <Icon name='Check' label={null} size='xs' />
            <span className='text-caption-sm font-medium'>
              {t('projects.taskDetail.checklist')}
            </span>
            <span className='text-caption-sm'>
              {t('projects.taskCard.checklist', { completed: 2, total: 3 })}
            </span>
          </div>
          <div className='flex flex-col gap-0.5'>
            <ChecklistItem label={t('projects.tour.step3.artChecklist1')} delay='.3s' done />
            <ChecklistItem label={t('projects.tour.step3.artChecklist2')} delay='.6s' done />
            <ChecklistItem label={t('projects.tour.step3.artChecklist3')} />
          </div>
        </div>
      </div>
    </div>
  )
}

const SummaryTile = ({ label, value, delay }: { label: string; value: string; delay: string }) => (
  <div
    style={{ animationDelay: delay }}
    className={cx('rounded-sm px-1.5 py-1 opacity-0', BG_TABLE, POP)}
  >
    <p className={cx('text-caption leading-tight font-semibold', TEXT_DARK)}>{value}</p>
    <p className={cx('text-caption-sm truncate leading-tight', TEXT_FAINT)}>{label}</p>
  </div>
)

const ReportRow = ({
  phase,
  status,
  statusClassName,
  delay,
}: {
  phase: string
  status: string
  statusClassName: string
  delay: string
}) => (
  <div
    style={{ animationDelay: delay }}
    className={cx(
      'flex items-center justify-between border-t px-0.5 py-0.5 opacity-0',
      BORDER_SOFT,
      POP,
    )}
  >
    <span className={cx('text-caption-sm truncate', TEXT_DARK)}>{phase}</span>
    <span
      className={cx(
        'text-caption-sm shrink-0 rounded-full px-1.5 py-0.5 font-medium',
        statusClassName,
      )}
    >
      {status}
    </span>
  </div>
)

const StepReport = () => (
  <div className='flex h-full flex-col items-center justify-center gap-1.5'>
    <div
      className={cx(
        'w-[248px] rounded-lg border bg-neutral-1 px-2.5 py-2',
        BORDER,
        '[animation:ptd-sheetRise_.4s_cubic-bezier(.25,1,.5,1)_both]',
      )}
    >
      <div className={cx('mb-1.5 flex items-center gap-1.5 border-b pb-1.5', BORDER_SOFT)}>
        <span className='flex h-5 w-5 items-center justify-center rounded-sm bg-neutral-3'>
          <Icon name='PaperPdf' label={null} size='xs' className={TEXT_FAINT} />
        </span>
        <p
          className={cx('text-caption-sm min-w-0 truncate leading-tight font-semibold', TEXT_DARK)}
        >
          {t('projects.pdf.title')}
        </p>
      </div>
      <div className='mb-1.5 grid grid-cols-3 gap-1.5'>
        <SummaryTile
          label={t('projects.table.tasks')}
          value={t('projects.tour.step4.artTotalValue')}
          delay='.15s'
        />
        <SummaryTile
          label={t('projects.pdf.summary.completed')}
          value={t('projects.tour.step4.artCompletedValue')}
          delay='.3s'
        />
        <SummaryTile
          label={t('projects.pdf.summary.progress')}
          value={t('projects.tour.step4.artProgressValue')}
          delay='.45s'
        />
      </div>
      {/* ptd-barFill ends at 67% — same number as step4.artProgressValue above. */}
      <div className='mb-1 h-1 overflow-hidden rounded-full bg-neutral-3'>
        <div className='h-full [animation:ptd-barFill_.9s_cubic-bezier(.25,1,.5,1)_.5s_both] rounded-full bg-sky-6' />
      </div>
      <ReportRow
        phase={t('projects.phases.execution')}
        status={t('projects.pdf.status.onTrack')}
        statusClassName='bg-success-2 text-success-8'
        delay='.6s'
      />
      <ReportRow
        phase={t('projects.phases.validation')}
        status={t('projects.pdf.status.attention')}
        statusClassName='bg-warning-2 text-warning-8'
        delay='.75s'
      />
    </div>
    <span className='relative inline-flex'>
      <span
        className={cx(
          'text-caption inline-flex h-8 [animation:ptd-glowPulse_2s_ease-in-out_infinite] items-center gap-1.5 rounded-md border bg-neutral-1 px-3 font-medium whitespace-nowrap',
          BORDER,
          ACCENT_BLUE,
        )}
      >
        <Icon name='Download' label={null} size='sm' />
        {t('projects.pdf.download')}
      </span>
      <Cursor className='-right-3 -bottom-3' />
    </span>
  </div>
)

const STEPS = [StepCreate, StepPhases, StepTask, StepReport]

export const STEP_COUNT = STEPS.length

export const StepArt = ({ step }: { step: number }) => {
  const Step = STEPS[step] ?? StepCreate
  return <Step />
}
