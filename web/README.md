# ELEGANT AGENCY

Next.js / TypeScript / GSAP / ScrollTrigger / Lenis / CSS Modules.

## Run

npm install
npm run dev

## Check and export

npm run check
npm run build

The static export is generated in out/.

## Configuration

src/lib/config.ts contains the contact email and central asset manifest.

No receiving email is invented. Until configured, enquiries can be
prepared, copied and downloaded locally. Email delivery is never simulated.

There is no form backend, database, analytics or authentication.

The supplied campaign is an original generated triptych of fictional adults.
scripts/assets.mjs generates responsive WebP and AVIF versions.

To replace the campaign, replace public/campaign-source.png with an
equal-panel 3:2 campaign image, or adapt Photo and the asset manifest.

Editorial profiles are explicitly fictional, not live availability listings.

Supply operator and legal information before commercial launch.
Search indexing is disabled by default in src/app/layout.tsx.

## Motion and accessibility

The first-visit intro lasts approximately 2.9 seconds and can be skipped.
Session storage remembers the intro for the browsing session.

Desktop uses pinned hero, private-world and horizontal-gallery scenes.
Below 960px, scrolling is native, the gallery is vertical and pins are removed.

Reduced motion removes intro playback and scroll choreography.

GSAP animations and ScrollTriggers are owned by matchMedia contexts.
Lenis uses the GSAP ticker.
Instances, ticker callbacks and listeners are removed on cleanup.

Gallery keyboard focus brings off-screen portraits into view.
Native dialogs provide focus containment and Escape support.
Native fragment links preserve URL history.

## Verification status

The execution environment was unavailable during authoring.

Dependency installation, TypeScript compilation, production build,
browser testing, responsive screenshots and performance measurements
have not been completed.

Only source consistency and bootstrap syntax checks were possible.
