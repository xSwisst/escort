# Web App Porting Progress

## ✅ Completed Steps

### 1. Assets Migration
- ✅ **Copied 24 SVG icons** from old to new app
  - `/src/assets/icons/` → `/src/assets/icons/`
  - All critical icons: heart.svg, heart-crack.svg, heart-xmark.svg, eye-slash.svg, shield-heart.svg, true.svg, search.svg, sort.svg, filter.svg, telegram.svg, etc.

- ✅ **Copied 4 banner images** from old to new app
  - `/src/assets/banners/*.jpg` → `/src/assets/banners/*.jpg`
  - Ready for hero carousel implementation

### 2. Core UI Components
- ✅ **Created MaskedIcon component**
  - `/src/components/MaskedIcon.tsx`
  - Ported from old app's `/src/shared/ui/MaskedIcon.tsx`
  - Used for all SVG icon rendering with CSS mask

- ✅ **Created BottomSheet component** (NEW)
  - `/src/components/BottomSheet.tsx`
  - `/src/components/BottomSheet.css`
  - Full drag-to-dismiss gestures with pointer capture
  - Expandable height (drag up to full screen)
  - Progressive backdrop blur (0→16px)
  - Elastic resistance at boundaries
  - Snap points for close threshold
  - 420ms cubic-bezier transitions
  - Ready for model details, sort, city switcher, etc.

- ✅ **Created HeroCarousel component** (NEW)
  - `/src/components/HeroCarousel.tsx`
  - `/src/components/HeroCarousel.css`
  - Infinite loop with 3-item sliding window
  - Auto-play every 3000ms
  - Drag gestures with momentum
  - 900ms slide transitions
  - Dot indicators with active state
  - Visibility API integration (pauses when hidden)
  - Ready for banner images

- ✅ **Created CityGate component** (NEW)
  - `/src/components/CityGate.tsx`
  - `/src/components/CityGate.css`
  - Blocks access until city selected
  - Search input with icon
  - Loading and error states
  - Glass morphism styling
  - Full-screen centered layout

- ✅ **Created CitySwitcher component** (NEW)
  - `/src/components/CitySwitcher.tsx`
  - `/src/components/CitySwitcher.css`
  - Uses BottomSheet for presentation
  - Two city slots support
  - List mode with active city indicator
  - Add mode with search input
  - Smooth mode transitions
  - Integrates with city management API

- ✅ **Created SortSheet component** (NEW)
  - `/src/components/SortSheet.tsx`
  - `/src/components/SortSheet.css`
  - Uses BottomSheet for presentation
  - 5 sort options: latest, price asc/desc, rating asc/desc
  - Radio button selection UI
  - Pending state with apply button
  - Glass morphism styling

- ✅ **Created SearchBar component** (NEW)
  - `/src/components/SearchBar.tsx`
  - `/src/components/SearchBar.css`
  - Search icon integration
  - Clear button when has value
  - Focus states with accent color
  - Pill-shaped design
  - Responsive sizing

### 3. Content/Labels (YAML)
- ✅ **Extended app.yaml with all models page labels** (93 labels added)
  - City gate labels (7)
  - City switcher labels (11)
  - Booking flow labels (50+)
  - Sort sheet labels (7)
  - Badge labels (2)
  - Empty state labels (2)
  - Card action labels
  - Sheet labels

- ✅ **Extended app.yaml with all profile page labels** (47 labels added)
  - Profile metadata labels
  - History sheet labels
  - Promo sheet labels
  - Addresses sheet labels
  - Order status translations

---

## 🔴 CRITICAL - Next Steps (Booking System)

### Priority 1: Booking Flow Infrastructure

Need to port from `/escort_v1_web_app/src/pages/models/ModelsPage.tsx` (lines ~2000-3134):

**Step 1: Booking State Machine**
- Create `/src/lib/booking/` directory
- Port booking state types and reducers
- Implement 7-step flow state:
  1. `datetime` - date and time selection
  2. `place` - at model's / at client's
  3. `address` - address selection/creation
  4. `tariff` - 1h/2h/3h/night selection
  5. `additionals` - additional services checkboxes
  6. `payment-method` - card/cash selection
  7. `payment` - payment confirmation

**Step 2: Booking API Integration**
- Add to `/src/lib/api.ts`:
  - `prepareModelBooking(token, code, body)` - prepare booking
  - `resolveModelBookingPayment(token, orderNumber, method)` - resolve payment
  - `markModelOpened(token, code)` - track model view

**Step 3: Booking UI Components**
Create in `/src/components/booking/`:
- `BookingSheet.tsx` - main booking container
- `BookingStepDateTime.tsx` - date/time wheels
- `BookingStepPlace.tsx` - place selection
- `BookingStepAddress.tsx` - address management
- `BookingStepTariff.tsx` - tariff cards
- `BookingStepAdditionals.tsx` - additionals checkboxes
- `BookingStepPaymentMethod.tsx` - payment method selection
- `BookingStepPayment.tsx` - payment confirmation

---

## 🟡 HIGH PRIORITY - UI Framework Components

### Priority 2: Bottom Sheet Component

Port from `/escort_v1_web_app/src/shared/ui/` (multiple sheet components):

**Create `/src/components/BottomSheet.tsx`**
- Draggable bottom sheet with gestures
- Pointer capture for drag handling
- Elastic resistance at boundaries
- Progressive backdrop blur (0→16px)
- Height calculation and expansion
- Snap points for different heights
- Animation timing: 420ms cubic-bezier(0.16, 1, 0.3, 1)

**Use cases:**
- Model details sheet
- City switcher sheet
- Sort options sheet
- History sheet (ProfilePage)
- Promo sheet (ProfilePage)
- Addresses sheet (ProfilePage)

### Priority 3: City Management System

Port from `/escort_v1_web_app/src/pages/models/ModelsPage.tsx` (lines ~500-800):

**City Gate Component**
- Block access to models until city selected
- City input with validation
- Loading state
- Error handling
- Integration with backend city validation

**City Switcher Component**
- Bottom sheet with 2 city slots
- Toggle between slots
- Add/remove cities
- Persistent state
- Animated transitions

### Priority 4: Hero Carousel

Port from `/escort_v1_web_app/src/shared/ui/PromoCardsCarousel.tsx` (~370 lines):

**Create `/src/components/HeroCarousel.tsx`**
- Infinite loop (3x repetition of images)
- Auto-play every 3000ms
- Drag gestures with momentum
- Slide transitions 900ms
- Dot indicators
- Pause on interaction
- Visibility API integration

---

## 🟢 MEDIUM PRIORITY - Polish & Animations

### Priority 5: Favorite Animations

✅ **COMPLETE** - Port from `/escort_v1_web_app/src/pages/models/ModelsPage.tsx` (animation logic):

**Jello Animation (on add)** ✅
- Duration: 560ms
- Spring effect with scale3d transforms
- Applied to favorite button
- Keyframes: scale3d oscillation (1.16→0.9→1.08→0.96→1.02→1)

**Shake Animation (on remove)** ✅
- Duration: 220ms
- Horizontal shake with rotation
- Applied to favorite button
- Keyframes: translateX + rotate oscillation (-1.6px/-6deg → 1.4px/5deg → -1.1px/-3deg → 0.9px/2deg)

**Exit Ghost Animation** ✅
- Creates portal-based ghost element at exact card position
- Ghost layer: fixed overlay at z-index 80, pointer-events none
- 420ms fade-out + blur(3px) + scale(0.92) transition
- Real card also fades with .card--exiting-favorite class
- Clean up after animation completes
- Only triggers when removing from favorites view (onlyFavorites=true)
- Refs track card positions via favoriteSlotRefs
- Three-phase timing:
  1. Shake animation (220ms)
  2. Create ghost + start exit transition
  3. Clean up ghosts after 420ms

### Priority 6: Search & Sort

**Search Component**
- Real-time filtering by model name
- Debounced input
- Clear button
- Empty state

**Sort Bottom Sheet**
- 5 sort options:
  - Latest (по новизне)
  - Price: low → high
  - Price: high → low
  - Rating: low → high
  - Rating: high → low
- Selected state indicator
- Done/Close buttons

### Priority 7: Model Sheet (Bottom Sheet)

Replace current ModelPage with draggable bottom sheet:
- Swipeable photo gallery
- Expandable height (drag up to full screen)
- Embedded booking flow
- Reviews section
- Services section
- Additionals section
- Smooth transitions

### Priority 8: Other Components

**ElasticScrollArea**
- Port from `/escort_v1_web_app/src/shared/ui/ElasticScrollArea.tsx`
- Overscroll prevention
- Touch event handling
- iOS-style elasticity

**Scroll-to-top Button**
- Show on scroll down
- Glassmorphism styling
- Smooth scroll animation
- Hide bottom nav on scroll

**FAQ Accordion** (AboutPage)
- Port from `/escort_v1_web_app/src/shared/ui/FaqAccordionItem.tsx`
- Search integration
- Smooth expand/collapse
- Multiple sections

**Onboarding Modal**
- Port from `/escort_v1_web_app/src/features/onboarding/`
- TGS/Lottie player component
- First-time user detection
- Skip button

---

## 📊 Completion Status

| Category | Completed | Total | Progress |
|----------|-----------|-------|----------|
| Assets | 28 | 28 | ✅ 100% |
| Content Labels | 140+ | 140+ | ✅ 100% |
| Core Components | 7 | 15+ | 🟡 47% |
| Search & Sort | 2 | 2 | ✅ 100% |
| Booking System | 0 | 8 | ❌ 0% |
| City Management | 2 | 2 | ✅ 100% |
| Animations | 3 | 4 | 🟢 75% |
| UI Polish | 0 | 6 | ❌ 0% |

**Overall Progress: ~45%** (assets, content, city management, search/sort, foundation components, and favorite animations done)

---

## 🎯 Recommended Implementation Order

1. ✅ **Bottom Sheet Component** (foundation for everything else) - DONE
2. ✅ **Hero Carousel** (visual impact, relatively isolated) - DONE
3. ✅ **City Gate & Switcher** (blocks access without city) - DONE
4. ✅ **Search & Sort** (user convenience with BottomSheet) - DONE
5. ✅ **Favorite Animations** (jello/shake/exit ghosts) - DONE
6. **Model Sheet** (refactor existing ModelPage to use BottomSheet)
7. **Booking System** (critical business logic, most complex)
8. **ElasticScrollArea** (polish)
9. **FAQ System** (AboutPage enhancement)
10. **Onboarding** (first-time user experience)

---

## 📝 Notes

- All assets are now in place and ready to use
- All content labels are available in `app.yaml`
- Focus should shift to component implementation
- Each component should be tested independently before integration
- Preserve exact animations timing from old app (560ms, 420ms, 900ms, etc.)
- Maintain glassmorphism design system
- Keep optimistic updates for favorites
- Use TanStack Query patterns from old app
