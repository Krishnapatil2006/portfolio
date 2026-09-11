# Responsiveness Bug-Fix Plan (Zero Visual Redesign)

Fix all viewport overflow and responsiveness bugs on mobile and tablet (320px to 1920px) while **strictly preserving 100% of the existing gamified Steam visual identity, colors, typography, cards, and desktop layout**.

## User Review Required

> [!IMPORTANT]
> **Zero Visual Redesign Guaranteed**:
> No colors, themes, typography, desktop layouts, animations, or gamified Steam UI components will be changed. The changes are purely responsive CSS boundary constraints, padding adjustments, and animation bounds so elements do not exceed the viewport on small screens.

## Identified Root Causes of Mobile Horizontal Overflow

Based on headless Chrome CDP layout audits across all target screen widths (320px to 1920px), the specific causes of horizontal overflow were identified:

1. **Card Header Negative Margins (`App.css`)**:
   - `body.CosmicTheme .card-header` has fixed `margin: -20px -20px 15px -20px;`.
   - On screens `<= 640px` and `<= 480px`, `.card` padding is reduced to `15px` and `12px 10px`, but `.card-header` still uses `-20px` margins, poking out `10px` to the left and `10px` to the right past the card boundary, causing a 368px width that overflows 320px and 360px viewports.
   - **Fix**: Adjust `.card-header` negative margins at `<= 640px` (`-15px -15px`) and `<= 480px` (`-12px -10px`) to match the card padding.

2. **Achievement Toast & Steam Notification Slide-in Animations (`AchievementToast.css` & `SteamNotification.css`)**:
   - Both use `@keyframes slideInRight` / `slideInFromRight` with `transform: translateX(120%)`.
   - Without `overflow: hidden` on their fixed containers, or when elements are 350px-410px wide, they project off-screen on 320px-430px viewports.
   - **Fix**: Constrain `.achievement-toast-container` and `.steam-notification-container` to `overflow: hidden; max-width: calc(100vw - 20px); left: 10px; right: 10px;`, and make toast/notification widths responsive `width: 100%; max-width: 100%;`.

3. **Chatbot Mobile Sizing (`TwinChatBot.css`)**:
   - Uses `width: calc(100vw - 30px);` which can overflow due to scrollbar width.
   - **Fix**: Use responsive container-relative widths (`width: 100%; max-width: 100%; left: 12px; right: 12px;`) at `<= 480px` and `<= 360px` without relying on `100vw`.

4. **GitHub Replay Carousel Mobile Padding (`GitHubReplay.css`)**:
   - `.replay-carousel` has `padding: 0 45px;` at `<= 768px`, which crunches slide content down to ~210px on a 320px phone.
   - **Fix**: Reduce side padding to `0 32px` on `<= 480px`, scale down navigation buttons to 30px, and ensure stats grids (`.stats-grid`, `.growth-stats`, `.impact-grid`) collapse cleanly to 1 column or 2 compact columns.

5. **Modals Mobile Bounds (`ProjectModal.css`, `AchievementModal.css`, `InfoModal.css`, `WalletModal.css`)**:
   - Ensure all overlays use `padding: 10px;` on mobile (`<= 480px`), `max-width: 100%`, and word-breaking (`overflow-wrap: anywhere;` or `word-break: break-word;`) on long project/repository titles so text does not clip or overflow.

6. **Global Foundation (`index.css` & `App.css`)**:
   - Ensure `box-sizing: border-box`, `html, body { width: 100%; max-width: 100%; margin: 0; padding: 0; }`, and `.container { width: 100%; max-width: 1200px; }`.

---

## Proposed Changes

### Core Styles
#### [MODIFY] [index.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/styles/index.css)
- Ensure `html, body` have `width: 100%; max-width: 100%; margin: 0; padding: 0;`.
- Ensure base box-sizing applies globally.

#### [MODIFY] [App.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/styles/App.css)
- Add responsive margin adjustments for `body.CosmicTheme .card-header` at `<= 640px` and `<= 480px` matching `.card`'s padding (`-15px -15px` and `-12px -10px`).
- Ensure `.content-wrapper` and `.container` don't exceed 100% width on 320px screens.

---

### Components & Modals
#### [MODIFY] [AchievementToast.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/components/AchievementToast.css)
- Set container `overflow: hidden; max-width: calc(100% - 20px);` at mobile breakpoints.
- Ensure toast width adapts gracefully without off-screen horizontal projection.

#### [MODIFY] [SteamNotification.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/components/SteamNotification.css)
- Constrain container width and overflow on mobile so `translateX(120%)` animation doesn't create document horizontal overflow.

#### [MODIFY] [TwinChatBot.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/components/TwinChatBot.css)
- Replace `100vw` calculations with responsive container bounds (`left: 12px; right: 12px; width: auto;`).

#### [MODIFY] [GitHubReplay.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/components/GitHubReplay.css)
- Adjust mobile carousel padding and navigation button size at `<= 480px`.
- Ensure internal heatmap scroller stays bounded.

#### [MODIFY] [ProjectModal.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/components/ProjectModal.css)
- Ensure modal overlay padding is 10px at `<= 480px` and modal title uses `overflow-wrap: anywhere;`.

#### [MODIFY] [Header.css](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/components/Header.css)
- Ensure navigation links and topbar items wrap cleanly on 320px/360px screens.

---

## Verification Plan

### Automated Viewport Audit Script
Run headless Chrome CDP audit across all required viewports:
- **Mobile**: 320px, 360px, 375px, 390px, 393px, 412px, 430px, 480px
- **Tablet**: 768px, 820px, 1024px
- **Desktop**: 1280px, 1440px, 1920px

**Pass Criteria**:
- `document.documentElement.scrollWidth === document.documentElement.clientWidth` for every viewport.
- 0 elements with `getBoundingClientRect().right > window.innerWidth`.
- Vitest unit tests pass (`npx vitest run`).
- Production build succeeds (`npm run build`).
