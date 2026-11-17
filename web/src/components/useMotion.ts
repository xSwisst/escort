'use client';

import { useLayoutEffect, useRef, type RefObject } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import s from './Editorial.module.css';

export function useMotion(
  root: RefObject<HTMLDivElement | null>,
  ready: boolean
) {
  const initialNavigation = useRef(false);

  useLayoutEffect(() => {
    if (!ready || !root.current) return;

    gsap.registerPlugin(ScrollTrigger);

    const scope = root.current;

    const query = (selector: string) =>
      scope.querySelectorAll<HTMLElement>(selector);

    const one = (name: string) =>
      scope.querySelector<HTMLElement>('.' + name)!;

    const media = gsap.matchMedia();
    let alive = true;
    let refreshFrame = 0;

    media.add(
      {
        desktop: '(min-width: 960px)',
        mobile: '(max-width: 959px)',
        reduce: '(prefers-reduced-motion: reduce)',
        fine: '(hover: hover) and (pointer: fine)',
      },
      context => {
        const { desktop, reduce, fine } = context.conditions!;
        if (reduce) return;

        const lenis = desktop
          ? new Lenis({
              duration: 1.05,
              smoothWheel: true,
              syncTouch: false,
              autoRaf: false,
            })
          : null;

        const tick = (seconds: number) =>
          lenis?.raf(seconds * 1000);

        const sync = () => ScrollTrigger.update();

        if (lenis) {
          lenis.on('scroll', sync);
          gsap.ticker.add(tick);
        }

        const lock = (event: Event) => {
          if ((event as CustomEvent<boolean>).detail) {
            lenis?.stop();
          } else {
            lenis?.start();
          }
        };

        window.addEventListener('elegant:lock', lock);

        const disposers: (() => void)[] = [];

        gsap.to(one(s.progress), {
          scaleX: 1,
          ease: 'none',
          scrollTrigger: {
            trigger: scope,
            start: 'top top',
            end: 'bottom bottom',
            scrub: .15,
          },
        });

        ScrollTrigger.create({
          trigger: scope,
          start: 'top -50',
          end: 'bottom top',
          onUpdate: self => {
            scope.dataset.scrolled =
              self.scroll() > 50 ? 'true' : 'false';
          },
        });

        if (window.scrollY < 160) {
          gsap.timeline({
            defaults: { ease: 'power4.out' },
          })
            .from(
              query('[data-scene="hero"] [data-line]'),
              {
                yPercent: 115,
                rotate: 2,
                duration: 1.25,
                stagger: .16,
              },
              0
            )
            .from(
              one(s.heroPhoto),
              {
                clipPath: 'inset(0% 0% 100% 0%)',
                duration: 1.35,
              },
              .05
            )
            .from(
              query('[data-hero-detail]'),
              { opacity: 0, duration: .8, stagger: .1 },
              .65
            )
            .from(
              one(s.header),
              { y: -16, opacity: 0, duration: .8 },
              .55
            );
        }

        if (desktop) {
          gsap.timeline({
            scrollTrigger: {
              trigger: one(s.hero),
              start: 'top top',
              end: '+=80%',
              pin: true,
              scrub: .8,
              anticipatePin: 1,
            },
          })
            .to(
              one(s.heroElegance),
              {
                xPercent: -18,
                yPercent: -55,
                ease: 'none',
              },
              0
            )
            .to(
              one(s.heroArt),
              {
                xPercent: 15,
                yPercent: 35,
                ease: 'none',
              },
              0
            )
            .to(
              one(s.heroPhoto),
              {
                scale: 1.06,
                xPercent: -3,
                ease: 'none',
              },
              0
            )
            .to(
              query('[data-hero-detail]'),
              { opacity: 0, duration: .25 },
              0
            );
        } else {
          gsap.to(one(s.heroArt), {
            xPercent: 8,
            ease: 'none',
            scrollTrigger: {
              trigger: one(s.hero),
              start: 'top top',
              end: 'bottom top',
              scrub: true,
            },
          });
        }

        gsap.fromTo(
          query('[data-word]'),
          { opacity: .18 },
          {
            opacity: 1,
            stagger: .12,
            ease: 'none',
            scrollTrigger: {
              trigger: one(s.philosophy),
              start: 'top 70%',
              end: 'bottom 75%',
              scrub: .4,
            },
          }
        );

        const world = one(s.world);

        if (desktop) {
          const timeline = gsap.timeline({
            scrollTrigger: {
              trigger: world,
              start: 'top top',
              end: '+=170%',
              pin: true,
              scrub: .85,
              anticipatePin: 1,
            },
          });

          timeline
            .from(
              [
                one(s.worldOne),
                one(s.worldTwo),
                one(s.worldThree),
              ],
              {
                clipPath: 'inset(100% 0% 0% 0%)',
                yPercent: 12,
                duration: .7,
                stagger: .1,
              },
              0
            )
            .from(
              query('[data-world-word]'),
              {
                yPercent: 30,
                scale: .93,
                duration: .7,
                stagger: .1,
              },
              .1
            )
            .to(
              one(s.worldOne),
              {
                xPercent: -115,
                yPercent: -18,
                duration: .9,
              },
              .75
            )
            .to(
              one(s.worldTwo),
              {
                xPercent: 115,
                yPercent: 12,
                duration: .9,
              },
              .75
            )
            .to(
              one(s.worldThree),
              { yPercent: 120, duration: .9 },
              .75
            )
            .fromTo(
              one(s.worldCampaign),
              { clipPath: 'inset(48% 49% 48% 49%)' },
              {
                clipPath: 'inset(0% 0% 0% 0%)',
                duration: 1.05,
                ease: 'power2.inOut',
              },
              .65
            )
            .fromTo(
              one(s.worldVeil),
              { opacity: 0 },
              { opacity: .48, duration: .7 },
              1.1
            )
            .to(
              query('[data-world-word]'),
              {
                yPercent: -110,
                opacity: 0,
                stagger: .06,
                duration: .65,
              },
              1.45
            )
            .from(
              one(s.worldCaption),
              {
                clipPath: 'inset(100% 0% 0% 0%)',
                y: 20,
                duration: .65,
              },
              1.55
            );
        } else {
          gsap.from(one(s.worldCampaign), {
            clipPath: 'inset(15% 10% 15% 10%)',
            ease: 'none',
            scrollTrigger: {
              trigger: world,
              start: 'top 55%',
              end: 'bottom 85%',
              scrub: .5,
            },
          });
        }

        if (desktop) {
          const track = one(s.galleryTrack);

          const distance = () =>
            Math.max(
              0,
              track.scrollWidth -
                one(s.galleryViewport).clientWidth
            );

          const horizontal = gsap.to(track, {
            x: () => -distance(),
            ease: 'none',
            scrollTrigger: {
              trigger: one(s.gallery),
              start: 'top top',
              end: () => '+=' + Math.max(1, distance()),
              pin: true,
              scrub: .65,
              invalidateOnRefresh: true,
              anticipatePin: 1,
            },
          });

          const focus = (event: FocusEvent) => {
            const card = (event.target as HTMLElement)
              .closest<HTMLElement>('[data-muse]');

            if (!card) return;

            const rect = card.getBoundingClientRect();

            if (
              rect.left >= 0 &&
              rect.right <= window.innerWidth
            ) return;

            const trigger = horizontal.scrollTrigger!;

            const target =
              trigger.start +
              Math.min(
                distance(),
                Math.max(
                  0,
                  card.offsetLeft -
                    (window.innerWidth - card.clientWidth) / 2
                )
              );

            if (lenis) {
              lenis.scrollTo(target, { immediate: true });
            } else {
              window.scrollTo({ top: target });
            }
          };

          track.addEventListener('focusin', focus);

          disposers.push(() =>
            track.removeEventListener('focusin', focus)
          );
        } else {
          query('[data-muse]').forEach((card, i) => {
            gsap.from(
              card.querySelector('.' + s.photo),
              {
                clipPath: i % 2
                  ? 'inset(0% 0% 0% 100%)'
                  : 'inset(0% 100% 0% 0%)',
                duration: 1.1,
                ease: 'power3.inOut',
                scrollTrigger: {
                  trigger: card,
                  start: 'top 86%',
                  once: true,
                },
              }
            );
          });
        }

        gsap.fromTo(
          query('[data-experience-line]'),
          {
            xPercent: (i: number) => i ? 7 : -7,
          },
          {
            xPercent: 0,
            ease: 'none',
            scrollTrigger: {
              trigger: one(s.experience),
              start: 'top 85%',
              end: 'top 10%',
              scrub: .7,
            },
          }
        );

        gsap.from(
          query('[data-scene="discretion"] [data-char]'),
          {
            yPercent: 105,
            rotateX: -55,
            transformOrigin: '50% 100%',
            stagger: { each: .035, from: 'center' },
            ease: 'power3.out',
            scrollTrigger: {
              trigger: one(s.discretion),
              start: 'top 65%',
              end: 'top 5%',
              scrub: .7,
            },
          }
        );

        gsap.fromTo(
          one(s.discretionShutter),
          { xPercent: 0 },
          {
            xPercent: 102,
            ease: 'none',
            scrollTrigger: {
              trigger: one(s.discretion),
              start: 'top 65%',
              end: 'top 5%',
              scrub: .7,
            },
          }
        );

        gsap.fromTo(
          one(s.enquiryCurtain),
          { yPercent: 0 },
          {
            yPercent: -101,
            ease: 'power2.inOut',
            scrollTrigger: {
              trigger: one(s.enquiry),
              start: 'top 85%',
              end: 'top 20%',
              scrub: .6,
            },
          }
        );

        gsap.from(
          query('[data-scene="enquiry"] [data-line]'),
          {
            yPercent: 105,
            stagger: .13,
            duration: 1.15,
            ease: 'power4.out',
            scrollTrigger: {
              trigger: one(s.enquiry),
              start: 'top 40%',
              once: true,
            },
          }
        );

        gsap.from(query('[data-footer-brand]'), {
          yPercent: 35,
          scaleY: .78,
          transformOrigin: '50% 100%',
          stagger: .1,
          ease: 'none',
          scrollTrigger: {
            trigger: one(s.footer),
            start: 'top 90%',
            end: 'bottom bottom',
            scrub: .7,
          },
        });

        if (fine) {
          query('[data-magnetic]').forEach(button => {
            const x = gsap.quickTo(button, 'x', {
              duration: .4,
              ease: 'power3.out',
            });

            const y = gsap.quickTo(button, 'y', {
              duration: .4,
              ease: 'power3.out',
            });

            const move = (event: PointerEvent) => {
              const rect = button.getBoundingClientRect();

              x(
                (event.clientX - rect.left - rect.width / 2)
                * .018
              );

              y(
                (event.clientY - rect.top - rect.height / 2)
                * .045
              );
            };

            const leave = () => {
              x(0);
              y(0);
            };

            button.addEventListener('pointermove', move);
            button.addEventListener('pointerleave', leave);

            disposers.push(() => {
              button.removeEventListener('pointermove', move);
              button.removeEventListener('pointerleave', leave);
            });
          });

          const cursor = one(s.cursor);

          const x = gsap.quickTo(cursor, 'x', {
            duration: .18,
            ease: 'power3.out',
          });

          const y = gsap.quickTo(cursor, 'y', {
            duration: .18,
            ease: 'power3.out',
          });

          const opacity = gsap.quickTo(cursor, 'opacity', {
            duration: .18,
          });

          query('[data-cursor]').forEach(card => {
            const move = (event: PointerEvent) => {
              x(event.clientX + 18);
              y(event.clientY + 18);
            };

            const enter = () => opacity(1);
            const leave = () => opacity(0);

            card.addEventListener('pointermove', move);
            card.addEventListener('pointerenter', enter);
            card.addEventListener('pointerleave', leave);

            disposers.push(() => {
              card.removeEventListener('pointermove', move);
              card.removeEventListener('pointerenter', enter);
              card.removeEventListener('pointerleave', leave);
            });
          });
        }

        refreshFrame = requestAnimationFrame(() => {
          ScrollTrigger.refresh();

          if (!initialNavigation.current) {
            initialNavigation.current = true;

            const target = window.location.hash
              ? document.getElementById(
                  window.location.hash.slice(1)
                )
              : null;

            target?.scrollIntoView({ block: 'start' });
          }
        });

        return () => {
          disposers.forEach(dispose => dispose());
          window.removeEventListener('elegant:lock', lock);
          gsap.ticker.remove(tick);
          lenis?.off('scroll', sync);
          lenis?.destroy();
        };
      }
    );

    document.fonts.ready.then(() => {
      if (alive) ScrollTrigger.refresh();
    });

    return () => {
      alive = false;
      cancelAnimationFrame(refreshFrame);
      media.revert();
    };
  }, [root, ready]);
}
