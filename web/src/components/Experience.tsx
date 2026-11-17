'use client';

import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import gsap from 'gsap';
import { type Overlay } from '@/lib/config';
import { Characters } from './Primitives';
import {
  Hero,
  Philosophy,
  PrivateWorld,
  SelectedMuses,
  TheExperience,
  Discretion,
  PrivateEnquiry,
  Footer,
} from './sections';
import Dialogs from './Dialogs';
import { useMotion } from './useMotion';
import s from './Editorial.module.css';

export default function Experience() {
  const root = useRef<HTMLDivElement>(null);
  const introNode = useRef<HTMLDivElement>(null);

  const [intro, setIntro] = useState(true);
  const [overlay, setOverlay] = useState<Overlay>(null);

  const close = useCallback(() => setOverlay(null), []);

  const finish = useCallback(() => {
    const restore = Boolean(
      document.activeElement?.closest('#intro')
    );

    try {
      sessionStorage.setItem('elegant:intro', 'seen');
    } catch {}

    setIntro(false);

    if (restore) {
      requestAnimationFrame(() =>
        root.current
          ?.querySelector<HTMLAnchorElement>('header a')
          ?.focus({ preventScroll: true })
      );
    }
  }, []);

  useMotion(root, !intro);

  useLayoutEffect(() => {
    if (!intro) return;

    const reduce = matchMedia(
      '(prefers-reduced-motion: reduce)'
    );

    let seen = false;

    try {
      seen = sessionStorage.getItem('elegant:intro') === 'seen';
    } catch {}

    if (
      reduce.matches ||
      seen ||
      window.location.hash ||
      window.scrollY > 100
    ) {
      finish();
      return;
    }

    const onChange = () => {
      if (reduce.matches) finish();
    };

    reduce.addEventListener('change', onChange);

    introNode.current
      ?.querySelector<HTMLButtonElement>('button')
      ?.focus({ preventScroll: true });

    const context = gsap.context(() => {
      gsap.timeline({ onComplete: finish })
        .from(
          '[data-char]',
          {
            yPercent: 115,
            rotate: 4,
            duration: .7,
            stagger: .04,
            ease: 'power4.out',
          },
          .1
        )
        .from(
          '.' + s.introAgency,
          {
            opacity: 0,
            letterSpacing: '.75em',
            duration: .8,
            ease: 'power3.out',
          },
          .5
        )
        .to(
          '.' + s.introBrand,
          {
            scale: .72,
            y: -25,
            duration: .65,
            ease: 'power3.inOut',
          },
          1.25
        )
        .fromTo(
          '.' + s.introBar,
          { scaleY: 0 },
          {
            scaleY: 1,
            duration: .5,
            ease: 'power3.inOut',
          },
          1.65
        )
        .to(
          introNode.current,
          {
            clipPath: 'inset(0% 0% 100% 0%)',
            duration: .8,
            ease: 'power4.inOut',
          },
          2.05
        );
    }, introNode);

    return () => {
      context.revert();
      reduce.removeEventListener('change', onChange);
    };
  }, [intro, finish]);

  const locked = intro || overlay !== null;

  useEffect(() => {
    const previous = document.body.style.overflow;

    if (locked) document.body.style.overflow = 'hidden';

    window.dispatchEvent(
      new CustomEvent('elegant:lock', { detail: locked })
    );

    return () => {
      document.body.style.overflow = previous;

      window.dispatchEvent(
        new CustomEvent('elegant:lock', { detail: false })
      );
    };
  }, [locked]);

  return (
    <div ref={root} className={s.site}>
      <a
        href="#main"
        className={s.skipLink}
        tabIndex={intro ? -1 : 0}
      >
        Skip to content
      </a>

      <div className={s.progress} aria-hidden="true" />

      <header className={s.header} inert={intro}>
        <a
          className={s.wordmark}
          href="#top"
          aria-label="Elegant Agency, home"
        >
          ELEGANT<span>AGENCY</span>
        </a>

        <nav className={s.desktopNav} aria-label="Main navigation">
          <a href="#experience">THE EXPERIENCE</a>
          <a href="#muses">OUR MUSES</a>
          <a href="#contact">CONTACT</a>
        </nav>

        <button
          type="button"
          className={s.menuButton}
          onClick={() => setOverlay({ type: 'menu' })}
          aria-haspopup="dialog"
        >
          MENU
          <span aria-hidden="true"><i /><i /></span>
        </button>
      </header>

      <main id="main" tabIndex={-1} inert={intro}>
        <Hero />
        <Philosophy />
        <PrivateWorld />
        <SelectedMuses open={setOverlay} />
        <TheExperience />
        <Discretion />
        <PrivateEnquiry open={setOverlay} />
      </main>

      <div inert={intro}>
        <Footer open={setOverlay} />
      </div>

      <div className={s.cursor} aria-hidden="true">VIEW ↗</div>

      {overlay && (
        <Dialogs
          key={overlay.type}
          value={overlay}
          onClose={close}
          open={setOverlay}
        />
      )}

      {intro && (
        <div
          id="intro"
          className={s.intro}
          ref={introNode}
          aria-label="Opening sequence"
        >
          <div className={s.introBrand}>
            <div className={s.introWord}>
              <Characters text="ELEGANT" />
            </div>
            <span className={s.introAgency}>AGENCY</span>
          </div>

          <div className={s.introBar} />

          <button
            className={s.skipIntro}
            type="button"
            onClick={finish}
          >
            SKIP INTRO ↗
          </button>
        </div>
      )}
    </div>
  );
}
