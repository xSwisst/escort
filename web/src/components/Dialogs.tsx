'use client';

import {
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type FormEvent,
} from 'react';
import gsap from 'gsap';
import { muses, site, type Overlay } from '@/lib/config';
import { Arrow, Photo } from './Primitives';
import s from './Editorial.module.css';

type Value = NonNullable<Overlay>;

export default function Dialogs({
  value,
  onClose,
  open,
}: {
  value: Value;
  onClose: () => void;
  open: (value: Overlay) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const closing = useRef(false);
  const headingId = useId();

  useLayoutEffect(() => {
    const node = dialog.current!;
    const previous = document.activeElement as HTMLElement | null;

    node.showModal();

    const context = gsap.context(() => {
      if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
        gsap.from('[data-dialog-body]', {
          y: 26,
          opacity: 0,
          duration: .65,
          ease: 'power3.out',
        });

        if (value.type === 'menu') {
          gsap.from('[data-menu-link]', {
            yPercent: 110,
            stagger: .07,
            duration: .8,
            ease: 'power4.out',
          });
        }
      }
    }, node);

    return () => {
      context.revert();
      node.close();
      previous?.focus({ preventScroll: true });
    };
  }, [value.type]);

  function close(after?: () => void) {
    if (closing.current) return;
    closing.current = true;

    const finish = () => {
      onClose();
      after?.();
    };

    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      finish();
    } else {
      gsap.to(
        dialog.current!.querySelector('[data-dialog-body]'),
        {
          opacity: 0,
          y: -14,
          duration: .22,
          onComplete: finish,
        }
      );
    }
  }

  const title =
    value.type === 'menu' ? 'A private world.' :
    value.type === 'enquiry' ? 'Let us begin.' :
    value.type === 'muse' ? muses[value.index].title :
    value.type === 'privacy' ? 'Privacy, considered.' :
    'Site information.';

  return (
    <dialog
      ref={dialog}
      className={s.dialog}
      aria-labelledby={headingId}
      data-lenis-prevent
      onCancel={event => {
        event.preventDefault();
        close();
      }}
      onClick={event => {
        if (event.target === event.currentTarget) close();
      }}
    >
      <div className={s.modalBody} data-dialog-body>
        <div className={s.modalTop}>
          <span>ELEGANT AGENCY</span>
          <button
            type="button"
            className={s.closeButton}
            onClick={() => close()}
            aria-label="Close dialog"
          >
            <span>CLOSE</span>
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                d="m4 4 12 12M16 4 4 16"
                stroke="currentColor"
                fill="none"
              />
            </svg>
          </button>
        </div>

        {value.type === 'menu' ? (
          <>
            <h2 id={headingId} className={s.menuHeading}>{title}</h2>

            <nav
              aria-label="Full navigation"
              className={s.menuLinks}
            >
              {[
                ['philosophy', 'The philosophy'],
                ['muses', 'Our muses'],
                ['experience', 'The experience'],
                ['contact', 'Private enquiry'],
              ].map(([id, label], i) => (
                <div className={s.mask} key={id}>
                  <a
                    data-menu-link
                    href={'#' + id}
                    onClick={event => {
                      event.preventDefault();

                      close(() => {
                        window.location.hash = id;
                        document.getElementById(id)?.focus({
                          preventScroll: true,
                        });
                      });
                    }}
                  >
                    <span>0{i + 1}</span>
                    <span>{label}</span>
                    <Arrow />
                  </a>
                </div>
              ))}
              {site.botUrl && (
                <div className={s.mask}>
                  <a
                    data-menu-link
                    href={site.botUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <span>05</span>
                    <span>Telegram Bot</span>
                    <Arrow />
                  </a>
                </div>
              )}
            </nav>

            <p className={s.menuFoot}>
              PRIVATE BY NATURE. / EXCLUSIVELY 18+
            </p>
          </>
        ) : value.type === 'muse' ? (
          <div className={s.profile}>
            <Photo
              index={muses[value.index].index}
              alt={'Fictional adult fashion portrait: ' + title}
            />

            <div>
              <p className={s.micro}>
                EDITORIAL PORTRAIT / {muses[value.index].id}
              </p>

              <h2 id={headingId}>{title}</h2>
              <i>{muses[value.index].chapter}</i>
              <p>{muses[value.index].note}</p>

              <p className={s.profileNote}>
                A fictional adult muse from the Elegant editorial
                collection. The portrait expresses an atmosphere;
                it is not a live availability listing.
              </p>

              <button
                type="button"
                className={s.cta}
                onClick={() => open({
                  type: 'enquiry',
                  muse: title,
                })}
              >
                START A CONVERSATION <Arrow />
              </button>
            </div>
          </div>
        ) : value.type === 'enquiry' ? (
          <div className={s.formLayout}>
            <div>
              <p className={s.micro}>A PERSONAL INTRODUCTION</p>
              <h2 id={headingId}>{title}</h2>
              <p>
                A few considered details.
                <br />
                The beginning of a conversation.
              </p>
            </div>
            <EnquiryForm muse={value.muse} />
          </div>
        ) : (
          <div className={s.legalCopy}>
            <p className={s.micro}>ELEGANT AGENCY / INFORMATION</p>
            <h2 id={headingId}>{title}</h2>

            {value.type === 'privacy' ? (
              <>
                <p>
                  Enquiry details stay in this browser until you
                  choose to copy them, download them or open your
                  email application. They are not sent to a server
                  by this website.
                </p>
                <p>
                  Session storage remembers whether you have seen
                  the opening sequence. Closing your browsing
                  session clears that preference. No analytics
                  or advertising trackers are included.
                </p>
                <p>
                  If you send an email, your chosen email provider
                  handles that communication under its own privacy
                  terms. No claim of anonymous or encrypted
                  delivery is made here.
                </p>
              </>
            ) : (
              <>
                <p>
                  Exclusively for adults aged 18 and over.
                  This website presents an editorial concept for
                  private social companionship and personal
                  introductions.
                </p>
                <p>
                  All campaign portraits depict fictional adults.
                  Editorial titles are not verified profiles or
                  statements of availability. No bookings or
                  payments are processed through this website.
                </p>
                <p>
                  Any introduction requires mutual consent and
                  clear expectations. Operator details and
                  contact information must be supplied by the
                  agency before commercial launch.
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </dialog>
  );
}

function EnquiryForm({ muse }: { muse?: string }) {
  const [draft, setDraft] = useState('');
  const [message, setMessage] = useState('');
  const prefix = useId();

  function prepare(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    setDraft([
      'PRIVATE ENQUIRY — ELEGANT AGENCY',
      '',
      'Name: ' + String(data.get('name')).trim(),
      'Contact: ' + String(data.get('email')).trim(),
      muse ? 'Editorial interest: ' + muse : '',
      '',
      String(data.get('note')).trim(),
    ].filter(Boolean).join('\n'));

    setMessage(
      'Your enquiry is prepared. Choose how you would like to share it.'
    );
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(draft);
      setMessage('Enquiry copied.');
    } catch {
      setMessage(
        'Select and copy your enquiry from the text below.'
      );
    }
  }

  return (
    <form className={s.form} onSubmit={prepare}>
      <label htmlFor={prefix + '-name'}>
        YOUR NAME
        <input
          id={prefix + '-name'}
          name="name"
          autoComplete="name"
          maxLength={100}
          required
          placeholder="How should we address you?"
        />
      </label>

      <label htmlFor={prefix + '-email'}>
        CONTACT EMAIL
        <input
          id={prefix + '-email'}
          name="email"
          type="email"
          autoComplete="email"
          maxLength={200}
          required
          placeholder="Your preferred email address"
        />
      </label>

      <label htmlFor={prefix + '-note'}>
        A FEW WORDS
        <textarea
          id={prefix + '-note'}
          name="note"
          maxLength={2000}
          rows={3}
          required
          placeholder="The occasion. The atmosphere. What matters to you."
        />
      </label>

      <label className={s.consent}>
        <input type="checkbox" required />
        <span>
          I am 18 or over and understand that this step prepares
          an enquiry for me to share.
        </span>
      </label>

      <button type="submit" className={s.cta}>
        PREPARE MY ENQUIRY <Arrow />
      </button>

      <p className={s.status} role="status" aria-live="polite">
        {message}
      </p>

      {draft && (
        <div className={s.draft}>
          <label htmlFor={prefix + '-draft'}>
            YOUR PRIVATE ENQUIRY
          </label>

          <textarea
            id={prefix + '-draft'}
            value={draft}
            readOnly
            rows={7}
          />

          <div>
            <button type="button" onClick={copy}>
              COPY ENQUIRY <Arrow />
            </button>

            <a
              href={
                'data:text/plain;charset=utf-8,' +
                encodeURIComponent(draft)
              }
              download="elegant-enquiry.txt"
            >
              SAVE DRAFT <Arrow />
            </a>

            {site.contactEmail && (
              <a
                href={
                  'mailto:' + site.contactEmail +
                  '?subject=' +
                  encodeURIComponent('Private enquiry — Elegant Agency') +
                  '&body=' +
                  encodeURIComponent(draft)
                }
              >
                OPEN EMAIL <Arrow />
              </a>
            )}

            {site.botUrl && (
              <a
                href={site.botUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                OPEN TELEGRAM BOT <Arrow />
              </a>
            )}
          </div>
        </div>
      )}
    </form>
  );
}
