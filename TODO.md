# TravelMate — Completion Status

## ✅ Fixed in this session

### Critical Bugs
- [x] **[TripView] Photo upload broken**: Replaced inline blob-URL approach with `usePhotoUpload` composable that properly uploads via `/api/files/upload` before saving
- [x] **[TripView] Invalid `capture` attribute**: `capture="environment"` → valid boolean `capture`

### TripView Refactoring
- [x] **Extracted duplicate map**: Created shared `TripMap.vue` component — `<LMap>` rendered once, used inline (desktop sidebar) + full map tab
- [x] **Delete confirmations**: Days/activities now show `ConfirmModal` before deletion
- [x] **Toast notifications**: All 10+ `catch { // ignore }` blocks replaced with `addToast("error", ...)`
- [x] **Loading states**: Added `creatingDay`/`creatingActivity`/`creatingExpense` refs to disable buttons during submission
- [x] **Global Escape handler**: `document.addEventListener("keydown")` closes all modals on Escape
- [x] **Mobile bottom nav**: Added `overflow-x-auto` + hidden scrollbar for 8 tabs

### Other Views
- [x] **DashboardView**: Trip search/filter by title, country, description
- [x] **DashboardView**: Pull-to-refresh only on touch devices (`ontouchstart` detection)
- [x] **SharedTripView**: SkeletonLoader + collapsible Leaflet map
- [x] **LoginView**: Password visibility toggle (👁️/🙈)
- [x] **RegisterView**: Password toggle + strength indicator bar
- [x] **GuestJoinView**: Join code format validation (`/^\d{6}$/`) + lookup loading state

### Components
- [x] **QuickNote**: FAB `bottom-28 md:bottom-24` (was `bottom-24`, overlapped mobile nav)
- [x] **OfflineBanner**: `fixed` → `relative` to avoid overlapping hero header
- [x] **ToastContainer**: Moved to `bottom-20 md:bottom-4 left-4` to avoid QuickNote FAB + mobile nav
- [x] **PollCard**: Added "🔒 截止" close-poll button

### Global
- [x] **Route transitions**: Page fade+slide via `<Transition>` in `App.vue`
- [x] **Auth guard**: Router `beforeEach` now checks `guest_token` alongside JWT

### Backend
- [x] **secret_key**: Removed hardcoded default — must be set in `.env` (already configured)
- [x] **XSS sanitization**: Added `sanitize()`/`sanitize_dict()` utilities, applied to trips/activities/memories create+update

## 🟡 Remaining (lower priority)

### UI/UX
- [ ] **TripView**: Split into composables + child components (1520 lines)
- [ ] **No swipe gesture**: Mobile users can't swipe between tabs
- [ ] **No dark mode**
- [ ] **No i18n**: Chinese/English inconsistent

### Functional
- [ ] **Dead components**: `ActivityComments`, `ConflictResolver`, `AppButton` exist but unused
- [ ] **Input trimming**: Partial — applied to key forms, not exhaustive
- [ ] **No pagination**: Trips/expenses/memories fetch all at once
- [ ] **Loading states**: Members/POIs now tracked, but settle-up could be integrated

### Infrastructure
- [ ] Alembic migrations
- [ ] Rate limiting on auth
- [ ] Frontend tests (Vitest)
- [ ] E2E tests (Playwright)
- [ ] CI/CD pipeline
- [ ] API versioning