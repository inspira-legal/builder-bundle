import { Icon } from '@inspira-legal/ui/Icon'
import { cx } from 'class-variance-authority'
import { t } from 'i18next'
import type { ReactNode } from 'react'

// Faithful port of the approved "3a — Empilhado" tour prototype (Claude Design
// doc "Análise Tabular - Diálogo"). Structure + per-step animations mirror the
// mock; its palette is expressed with DS tokens, and ProjectsTourDialog/StepArt
// declares the same aliases so the two modals read as one family. Keyframes
// (ttd-*) live in index.tsx.
const BORDER = 'border-neutral-5'
const BORDER_SOFT = 'border-neutral-3'
const TEXT_DARK = 'text-neutral-10'
const TEXT_MUTED = 'text-neutral-9'
const TEXT_FAINT = 'text-neutral-8'
const BG_TABLE = 'bg-neutral-2'
const BG_LAVENDER = 'bg-sky-2'
const TEXT_INDIGO = 'text-[var(--gradient-4c-to)]'
const ACCENT_BLUE = 'text-sky-10'
const POP = '[animation:ttd-colPop_.4s_cubic-bezier(.25,1,.5,1)_forwards]'

// Cursor glyph; ttd-cursorTap easing lives in index.tsx. Position via className.
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
      'absolute [animation:ttd-cursorTap_1.6s_ease-in-out_infinite] [filter:drop-shadow(0_2px_3px_rgba(7,12,33,0.3))]',
      className,
    )}
  >
    <path d='M5 3l6.5 16 2.2-6.6L20 10.5 5 3z' />
  </svg>
)

const StepCreate = () => (
  <div className='flex h-full [animation:ttd-stepIn_.3s_cubic-bezier(.25,1,.5,1)_both] flex-col items-center justify-center gap-3.5'>
    <div
      className={cx(
        'flex w-[220px] flex-col items-center gap-2.5 rounded-xl border-[1.5px] border-dashed bg-neutral-1 px-4.5 py-4.5',
        'border-neutral-6',
      )}
    >
      <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-neutral-3'>
        <Icon name='Paper' label={null} className={cx('h-4 w-4', TEXT_FAINT)} />
      </div>
      <p className={cx('text-caption-sm', TEXT_FAINT)}>
        {t('documentVault.tabularTour.step1.title')}
      </p>
      <span className='relative inline-flex'>
        <span className='text-button inline-flex h-[38px] [animation:ttd-glowPulse_2s_ease-in-out_infinite] items-center gap-1.5 rounded-md bg-navy-3 px-4.5 font-medium whitespace-nowrap text-neutral-1'>
          <Icon name='Plus' label={null} size='sm' />
          {t('documentVault.tabularTour.step1.artCta')}
        </span>
        <Cursor className='-right-3.5 -bottom-3.5' />
      </span>
    </div>
  </div>
)

const ColHead = ({ name, delay }: { name: string; delay: string }) => (
  <div
    style={{ animationDelay: delay }}
    className={cx('border-l px-2 py-2 opacity-0', BG_TABLE, BORDER_SOFT, POP)}
  >
    <p className={cx('text-caption-sm truncate font-semibold', TEXT_DARK)}>{name}</p>
  </div>
)

const ColCell = ({ children, delay }: { children: ReactNode; delay: string }) => (
  <div
    style={{ animationDelay: delay }}
    className={cx(
      'text-caption-sm flex h-9 items-center border-t border-l px-2 opacity-0',
      BORDER_SOFT,
      TEXT_DARK,
      POP,
    )}
  >
    {children}
  </div>
)

const StepColumns = () => (
  <div className='flex h-full items-center justify-center p-1.5'>
    <div className='w-[320px]'>
      <div
        className={cx(
          'grid grid-cols-[1.2fr_1.1fr_1fr_0.9fr] overflow-hidden rounded-lg border bg-neutral-1',
          BORDER,
        )}
      >
        <div
          className={cx(
            'text-caption-sm px-2 py-2 font-semibold opacity-0',
            BG_TABLE,
            TEXT_MUTED,
            POP,
          )}
        >
          {t('documentVault.tabularReview.table.documentColumn')}
        </div>
        <ColHead name={t('documentVault.tabularTour.step2.artColTerm')} delay='.15s' />
        <ColHead name={t('documentVault.tabularTour.step2.artColValor')} delay='.3s' />
        <ColHead name={t('documentVault.tabularTour.step2.artColRisco')} delay='.45s' />
        <div
          className={cx(
            'text-caption-sm flex h-9 items-center gap-1.5 border-t px-2 opacity-0',
            BORDER_SOFT,
            TEXT_DARK,
            POP,
          )}
        >
          <Icon name='Paper' label={null} className={cx('h-3 w-3 shrink-0', TEXT_FAINT)} />
          <span className='truncate'>{t('documentVault.tabularTour.step2.artDocumentName')}</span>
        </div>
        <ColCell delay='.15s'>{t('documentVault.tabularTour.step2.artCellDate')}</ColCell>
        <ColCell delay='.3s'>{t('documentVault.tabularTour.step4.artValue1')}</ColCell>
        <ColCell delay='.45s'>
          <span className='text-caption-sm rounded-full bg-success-2 px-1.5 py-0.5 font-medium text-success-9'>
            {t('documentVault.tabularTour.step2.artCellRisk')}
          </span>
        </ColCell>
      </div>
      <div
        style={{ animationDelay: '.9s' }}
        className={cx(
          'mt-2.5 flex items-start gap-2 rounded-lg px-3 py-2.5 opacity-0',
          BG_LAVENDER,
          POP,
        )}
      >
        <Icon name='Comment' label={null} className={cx('mt-0.5 h-3 w-3 shrink-0', ACCENT_BLUE)} />
        <div className='min-w-0'>
          <p className={cx('mb-0.5 text-caption-sm font-semibold uppercase', TEXT_FAINT)}>
            {t('documentVault.tabularTour.step2.artCalloutLabel')}
          </p>
          <p className={cx('text-caption-sm italic', TEXT_DARK)}>
            “{t('documentVault.tabularTour.step2.artExampleQuestion')}”
          </p>
        </div>
      </div>
    </div>
  </div>
)

const TemplateRow = ({
  name,
  badge,
  badgeClassName,
  count,
  delay,
  selected = false,
}: {
  name: string
  badge: string
  badgeClassName: string
  count: number
  delay: string
  selected?: boolean
}) => (
  <div
    style={{ animationDelay: delay }}
    className={cx(
      'flex items-center gap-2.5 rounded-lg border px-3 py-2.5 opacity-0',
      selected
        ? 'border-sky-4 bg-sky-1 shadow-[0_0_0_3px_rgba(106,151,235,0.15)]'
        : cx(BORDER, 'bg-neutral-1'),
      POP,
    )}
  >
    <span
      className={cx(
        'flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-lg',
        selected ? 'bg-sky-2' : BG_TABLE,
      )}
    >
      <Icon name='Grid' label={null} size='sm' className={ACCENT_BLUE} />
    </span>
    <div className='min-w-0 flex-1'>
      <div className='flex items-center gap-1.5'>
        <span className={cx('text-body-sm truncate font-medium', TEXT_DARK)}>{name}</span>
        <span
          className={cx(
            'text-caption-sm shrink-0 rounded-full px-1.5 py-0.5 font-medium',
            badgeClassName,
          )}
        >
          {badge}
        </span>
      </div>
      <p className={cx('text-caption-sm', TEXT_FAINT)}>
        {t('documentVault.tabularReview.create.wizard.step2.templateColCount', { count })}
      </p>
    </div>
  </div>
)

const StepTemplate = () => (
  <div className='flex h-full items-center justify-center'>
    <div className='flex w-[296px] flex-col gap-2'>
      <p className={cx('text-caption-sm font-semibold uppercase opacity-0', TEXT_FAINT, POP)}>
        {t('documentVault.tabularTour.step3.title')}
      </p>
      <TemplateRow
        name={t('documentVault.tabularTour.step3.artTemplate1Name')}
        badge={t('documentVault.tabularReview.create.wizard.step2.badgeInspira')}
        badgeClassName={cx('bg-sky-2', TEXT_INDIGO)}
        count={12}
        delay='.15s'
        selected
      />
      <TemplateRow
        name={t('documentVault.tabularTour.step3.artTemplate2Name')}
        badge={t('documentVault.tabularReview.create.wizard.step2.badgeMine')}
        badgeClassName={cx(BG_TABLE, TEXT_MUTED)}
        count={8}
        delay='.4s'
      />
      <div
        style={{ animationDelay: '.65s' }}
        className={cx(
          'text-caption flex h-8 items-center justify-center gap-1.5 rounded-md border-[1.5px] border-dashed font-medium opacity-0',
          'border-neutral-6',
          ACCENT_BLUE,
          POP,
        )}
      >
        <Icon name='Download' label={null} size='sm' />
        {t('documentVault.tabularTour.step3.artSaveAsTemplate')}
      </div>
    </div>
  </div>
)

const CellRow = ({
  doc,
  value,
  active = false,
}: {
  doc: string
  value: string
  active?: boolean
}) => (
  <div className={cx('grid grid-cols-[1.5fr_1fr] border-b', BORDER_SOFT)}>
    <div
      className={cx('text-caption-sm flex h-[34px] min-w-0 items-center gap-1.5 px-2.5', TEXT_DARK)}
    >
      <Icon name='Paper' label={null} className='h-3 w-3 shrink-0' />
      <span className='truncate'>{doc}</span>
    </div>
    <div
      className={cx(
        'relative text-caption-sm flex h-[34px] items-center px-2.5 font-medium',
        TEXT_DARK,
        active && 'rounded-xs bg-sky-2 shadow-[inset_0_0_0_1.5px_var(--color-sky-9)]',
      )}
    >
      {value}
      {active && <Cursor className='right-1.5 -bottom-2' />}
    </div>
  </div>
)

const StepSource = () => (
  <div className='flex h-full items-center justify-center p-1.5'>
    <div className='relative w-[250px]'>
      <div className={cx('overflow-hidden rounded-lg border bg-neutral-1', BORDER)}>
        <div className={cx('grid grid-cols-[1.5fr_1fr] border-b', BG_TABLE, BORDER)}>
          <div
            className={cx(
              'text-caption-sm flex h-[30px] items-center px-2.5 font-semibold',
              TEXT_MUTED,
            )}
          >
            {t('documentVault.tabularReview.table.documentColumn')}
          </div>
          <div
            className={cx(
              'text-caption-sm flex h-[30px] items-center px-2.5 font-semibold',
              TEXT_MUTED,
            )}
          >
            {t('documentVault.tabularTour.step2.artColValor')}
          </div>
        </div>
        <CellRow
          doc={t('documentVault.tabularTour.step2.artDocumentName')}
          value={t('documentVault.tabularTour.step4.artValue1')}
          active
        />
        <CellRow
          doc={t('documentVault.tabularTour.step4.artDocument2Name')}
          value={t('documentVault.tabularTour.step4.artValue2')}
        />
      </div>
      <div className='absolute top-[54px] left-[92px] z-[2] w-[188px] origin-top-left [animation:ttd-colPop_.45s_cubic-bezier(.25,1,.5,1)_.35s_forwards] rounded-lg border border-sky-3 bg-neutral-1 px-3 py-2.5 opacity-0'>
        <div className='mb-1.5 flex items-center gap-1.5'>
          <Icon name='Comment' label={null} className={cx('h-3 w-3', ACCENT_BLUE)} />
          <span className={cx('text-caption-sm font-semibold', TEXT_INDIGO)}>
            {t('documentVault.tabularTour.step4.artCitationLabel')}
          </span>
        </div>
        <p className={cx('text-caption-sm italic', TEXT_DARK)}>
          “{t('documentVault.tabularTour.step4.artCitationQuote')}”
        </p>
      </div>
    </div>
  </div>
)

const STEPS = [StepCreate, StepColumns, StepTemplate, StepSource]

export const STEP_COUNT = STEPS.length

export const StepArt = ({ step }: { step: number }) => {
  const Step = STEPS[step] ?? StepCreate
  return <Step />
}
