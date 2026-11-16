import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChevronLeft, UserRound } from 'lucide-react';
import { createPortal } from 'react-dom';
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import discountIcon from '@/assets/icons/disount.svg';
import geoHomeIcon from '@/assets/icons/geo-home.svg';
import historyIcon from '@/assets/icons/history.svg';
import savedIcon from '@/assets/icons/saved.svg';
import { useSessionStore } from '@/entities/session/sessionStore';
import { activateProfilePromo, addProfileAddress, getProfile, getProfileOrders } from '@/shared/api/webAppApi';
import { formatDate } from '@/shared/lib/format';
import type { ProfileAddressItem } from '@/shared/types/web-app';
import { MaskedIcon } from '@/shared/ui/MaskedIcon';
import profilePageContentRaw from './profilePageContent.yaml?raw';

const PROFILE_SHEET_TRANSITION_MS = 420;
const PROFILE_ORDERS_QUERY_STALE_MS = 2 * 60 * 1000;

type ProfileSheetKind = 'history' | 'promo' | 'addresses';
type ProfileAddressesMode = 'list' | 'create';

const profilePageContent = JSON.parse(profilePageContentRaw) as {
  profileNameFallback: string;
  profileIdLabel: string;
  profileDateFallback: string;
  profileRegisteredPrefix: string;
  cityLabel: string;
  ratingLabel: string;
  ordersLabel: string;
  historyLabel: string;
  promoLabel: string;
  addressesLabel: string;
  favoritesLabel: string;
  metricFallback: string;
  loadingLabel: string;
  historyLoadingLabel: string;
  historySheetTitle: string;
  historySheetSubtitle: string;
  historyEmptyLabel: string;
  historyOrderNumberLabel: string;
  historyOrderDateFallback: string;
  historyOrderModelFallback: string;
  historyOrderCityFallback: string;
  historyOrderStatusLabels: Record<string, string>;
  promoSheetTitle: string;
  promoSheetSubtitle: string;
  promoInputPlaceholder: string;
  promoActivateLabel: string;
  promoLoadingLabel: string;
  promoActivePrefix: string;
  promoActiveAmountPrefix: string;
  promoSuccessPrefix: string;
  promoAmountSuffix: string;
  addressesSheetTitle: string;
  addressesSheetSubtitle: string;
  addressesEmptyLabel: string;
  addressesAddLabel: string;
  addressesCreateTitle: string;
  addressesCreateSubtitle: string;
  addressesTitlePlaceholder: string;
  addressesValuePlaceholder: string;
  addressesConfirmLabel: string;
  sheetCloseLabel: string;
};

function formatPromoAmount(amount: number | null | undefined) {
  if (amount == null) {
    return profilePageContent.metricFallback;
  }

  return `${amount} ${profilePageContent.promoAmountSuffix}`;
}

function getOrderStatusLabel(status: string) {
  return profilePageContent.historyOrderStatusLabels[status] || status;
}

function getPromoErrorMessage(errorMessage: string) {
  const normalized = errorMessage.trim().toLowerCase();

  if (normalized === 'not found' || normalized.includes('промокод') && normalized.includes('не найден') || normalized.includes('not found')) {
    return 'Промокод не найден';
  }

  return errorMessage;
}

export function ProfilePage() {
  const token = useSessionStore((state) => state.session?.sessionToken ?? '');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const profileQuery = useQuery({
    queryKey: ['profile', token],
    queryFn: () => getProfile(token),
    enabled: Boolean(token),
  });
  const [activeSheet, setActiveSheet] = useState<ProfileSheetKind | null>(null);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isSheetDragging, setIsSheetDragging] = useState(false);
  const [sheetOffset, setSheetOffset] = useState(0);
  const [sheetHeight, setSheetHeight] = useState(0);
  const [sheetContentHeight, setSheetContentHeight] = useState<number | null>(null);
  const [promoCode, setPromoCode] = useState('');
  const [addressesMode, setAddressesMode] = useState<ProfileAddressesMode>('list');
  const [addressTitle, setAddressTitle] = useState('');
  const [addressValue, setAddressValue] = useState('');
  const sheetRef = useRef<HTMLElement | null>(null);
  const sheetContentRef = useRef<HTMLDivElement | null>(null);
  const sheetBodyRef = useRef<HTMLDivElement | null>(null);
  const closeTimeoutRef = useRef<number | null>(null);
  const dragPointerIdRef = useRef<number | null>(null);
  const dragStartYRef = useRef(0);
  const dragStartOffsetRef = useRef(0);
  const sheetOffsetRef = useRef(0);
  const sheetHasScrollRef = useRef(false);
  const sheetInitialHeightRef = useRef<number | null>(null);
  const sheetDragStartHeightRef = useRef(0);

  const profile = profileQuery.data;
  const profileName = [profile?.user.firstName, profile?.user.lastName].filter(Boolean).join(' ').trim() || profilePageContent.profileNameFallback;
  const activeCity = (
    profile?.client.cityStatus === 2
      ? profile?.client.secondCity
      : profile?.client.firstCity
  )?.trim() || profilePageContent.metricFallback;
  const registeredAt = profile?.client.dateRegister
    ? formatDate(profile.client.dateRegister)
    : profilePageContent.profileDateFallback;
  const ratingValue = typeof profile?.client.rating === 'number'
    ? profile.client.rating.toFixed(1)
    : profilePageContent.metricFallback;
  const ordersValue = typeof profile?.client.orders === 'number'
    ? String(profile.client.orders)
    : profilePageContent.metricFallback;
  const activePromoCode = profile?.client.promo?.trim() ?? '';
  const activePromoAmount = profile?.client.promoAmount ?? null;
  const hasActivePromo = Boolean(activePromoCode);
  const isAddressSystemEnabled = Boolean(profile?.client.addressSystemEnabled);
  const profileAddresses = profile?.addresses ?? [];

  const ordersQuery = useQuery({
    queryKey: ['profile-orders', token],
    queryFn: () => getProfileOrders(token),
    enabled: Boolean(token),
    retry: false,
    staleTime: PROFILE_ORDERS_QUERY_STALE_MS,
    refetchOnWindowFocus: false,
  });

  const promoMutation = useMutation({
    mutationFn: (code: string) => activateProfilePromo(token, code),
    onSuccess: (data) => {
      queryClient.setQueryData(['profile', token], (current: typeof profile | undefined) => (
        current && data.client
          ? { ...current, client: data.client }
          : current
      ));
      if (data.client) {
        profileQuery.refetch();
      }
      setPromoCode('');
    },
  });

  const addAddressMutation = useMutation({
    mutationFn: ({ title, address }: { title: string; address: string }) => addProfileAddress(token, title, address),
    onSuccess: (data) => {
      queryClient.setQueryData(['profile', token], (current: typeof profile | undefined) => (
        current
          ? { ...current, addresses: data.addresses }
          : current
      ));
      setAddressTitle('');
      setAddressValue('');
      setAddressesMode('list');
      void profileQuery.refetch();
    },
  });

  const historyItems = useMemo(() => {
    return ordersQuery.data?.items ?? [];
  }, [ordersQuery.data?.items]);

  const sheetClosedOffset = (sheetHeight || 400) + 36;
  const maxSheetDrag = sheetClosedOffset;
  const sheetTranslateY = isSheetOpen ? sheetOffset : sheetClosedOffset;
  const sheetProgress = isSheetOpen ? Math.min(1, Math.max(0, 1 - (sheetOffset / maxSheetDrag))) : 0;

  const updateSheetOffset = (nextOffset: number) => {
    sheetOffsetRef.current = nextOffset;
    setSheetOffset(nextOffset);
  };

  const sheetTouchStartYRef = useRef(0);

  const handleSheetScrollTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    sheetTouchStartYRef.current = event.touches[0].clientY;
  };

  const handleSheetScrollTouchMove = (event: React.TouchEvent<HTMLDivElement>) => {
    const el = event.currentTarget;
    const touchY = event.touches[0].clientY;
    const isPullingDown = touchY > sheetTouchStartYRef.current;
    const isPullingUp = touchY < sheetTouchStartYRef.current;

    if (isPullingDown && el.scrollTop <= 0) {
      if (event.cancelable) {
        event.preventDefault();
      }
    } else if (isPullingUp && el.scrollTop + el.clientHeight >= el.scrollHeight - 1) {
      if (event.cancelable) {
        event.preventDefault();
      }
    }
  };

  const openSheet = (kind: ProfileSheetKind) => {
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }

    if (kind === 'history') {
      void ordersQuery.refetch();
    }

    if (kind === 'promo') {
      promoMutation.reset();
    }

    if (kind === 'addresses') {
      addAddressMutation.reset();
      setAddressesMode('list');
      setAddressTitle('');
      setAddressValue('');
    }

    updateSheetOffset(0);
    setIsSheetDragging(false);
    setActiveSheet(kind);
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        setIsSheetOpen(true);
      });
    });
  };

  const closeSheet = () => {
    setIsSheetDragging(false);
    setIsSheetOpen(false);

    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
    }

    closeTimeoutRef.current = window.setTimeout(() => {
      setActiveSheet(null);
      setPromoCode('');
      promoMutation.reset();
      addAddressMutation.reset();
      setAddressesMode('list');
      setAddressTitle('');
      setAddressValue('');
      setSheetContentHeight(null);
      sheetInitialHeightRef.current = null;
      updateSheetOffset(0);
      closeTimeoutRef.current = null;
    }, PROFILE_SHEET_TRANSITION_MS);
  };

  const handleSheetDragStart = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!activeSheet || !isSheetOpen) {
      return;
    }

    dragPointerIdRef.current = event.pointerId;
    dragStartYRef.current = event.clientY;
    dragStartOffsetRef.current = sheetOffsetRef.current;
    setIsSheetDragging(true);
    event.currentTarget.setPointerCapture(event.pointerId);

    const ordersEl = sheetRef.current?.querySelector('.profile-page__orders') as HTMLElement | null;
    const hasScroll = Boolean(ordersEl && (ordersEl.scrollHeight - ordersEl.clientHeight > 20));
    sheetHasScrollRef.current = hasScroll;
    sheetDragStartHeightRef.current = sheetContentHeight || sheetRef.current?.getBoundingClientRect().height || 400;
  };

  const handleSheetDragMove = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!isSheetDragging || dragPointerIdRef.current !== event.pointerId) {
      return;
    }

    const delta = event.clientY - dragStartYRef.current;
    const initialHeight = sheetInitialHeightRef.current ?? 400;
    const wasExpanded = sheetDragStartHeightRef.current > initialHeight + 20;

    if (delta > 0) {
      if (wasExpanded) {
        const remainingHeight = sheetDragStartHeightRef.current - delta;
        if (remainingHeight >= initialHeight) {
          setSheetContentHeight(remainingHeight);
          updateSheetOffset(0);
        } else {
          setSheetContentHeight(initialHeight);
          updateSheetOffset(initialHeight - remainingHeight);
        }
      } else {
        const rawOffset = dragStartOffsetRef.current + delta;
        updateSheetOffset(rawOffset);
      }
    } else {
      if (!sheetHasScrollRef.current) {
        updateSheetOffset(0);
      } else {
        updateSheetOffset(0);
        const stretch = -delta;
        const bodyHeight = (sheetRef.current?.querySelector('.profile-page__sheet-body')?.scrollHeight ?? 0) + 30;
        const topLimit = Math.min(Math.max(300, window.innerHeight - 44), bodyHeight);
        const nextHeight = Math.min(topLimit, sheetDragStartHeightRef.current + stretch);
        setSheetContentHeight(nextHeight);
      }
    }
  };

  const handleSheetDragEnd = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (dragPointerIdRef.current !== event.pointerId) {
      return;
    }

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    dragPointerIdRef.current = null;
    setIsSheetDragging(false);

    const initialHeight = sheetInitialHeightRef.current ?? 400;
    const wasExpanded = sheetDragStartHeightRef.current > initialHeight + 20;
    const delta = event.clientY - dragStartYRef.current;

    const shouldClose = sheetOffsetRef.current > Math.min(160, (sheetHeight || 400) * 0.32);
    if (shouldClose) {
      closeSheet();
      return;
    }

    updateSheetOffset(0);

    if (wasExpanded) {
      if (delta > 20) {
        setSheetContentHeight(initialHeight);
      } else if (delta < -30) {
        const bodyHeight = (sheetRef.current?.querySelector('.profile-page__sheet-body')?.scrollHeight ?? 0) + 30;
        const topLimit = Math.min(Math.max(300, window.innerHeight - 44), bodyHeight);
        setSheetContentHeight(topLimit);
      } else {
        const bodyHeight = (sheetRef.current?.querySelector('.profile-page__sheet-body')?.scrollHeight ?? 0) + 30;
        const topLimit = Math.min(Math.max(300, window.innerHeight - 44), bodyHeight);
        setSheetContentHeight(topLimit);
      }
    } else {
      if (delta < -50 && sheetHasScrollRef.current) {
        const bodyHeight = (sheetRef.current?.querySelector('.profile-page__sheet-body')?.scrollHeight ?? 0) + 30;
        const topLimit = Math.min(Math.max(300, window.innerHeight - 44), bodyHeight);
        setSheetContentHeight(topLimit);
      }
    }
  };

  const handlePromoSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedCode = promoCode.trim();
    if (!normalizedCode || hasActivePromo) {
      return;
    }

    promoMutation.mutate(normalizedCode);
  };

  const handleAddressSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedTitle = addressTitle.trim();
    const normalizedAddress = addressValue.trim();
    if (!normalizedTitle || !normalizedAddress) {
      return;
    }

    addAddressMutation.mutate({
      title: normalizedTitle,
      address: normalizedAddress,
    });
  };

  const openAddressesCreateMode = () => {
    addAddressMutation.reset();
    setAddressTitle('');
    setAddressValue('');
    setAddressesMode('create');
  };

  const handleSheetBack = () => {
    if (activeSheet === 'addresses' && addressesMode === 'create') {
      addAddressMutation.reset();
      setAddressTitle('');
      setAddressValue('');
      setAddressesMode('list');
      return;
    }

    closeSheet();
  };

  useEffect(() => {
    if (!activeSheet) {
      return undefined;
    }

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.body.classList.add('models-sheet-open');

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeSheet();
      }
    };

    window.addEventListener('keydown', handleEscape);

    return () => {
      document.body.style.overflow = originalOverflow;
      document.body.classList.remove('models-sheet-open');
      window.removeEventListener('keydown', handleEscape);
    };
  }, [activeSheet]);

  useEffect(() => {
    if (!activeSheet) {
      return undefined;
    }

    const frameId = window.requestAnimationFrame(() => {
      setIsSheetOpen(true);
    });

    return () => {
      window.cancelAnimationFrame(frameId);
    };
  }, [activeSheet]);

  useEffect(() => {
    if (!activeSheet) {
      return undefined;
    }

    const syncSheetHeight = () => {
      setSheetHeight(sheetRef.current?.getBoundingClientRect().height ?? 0);
    };

    syncSheetHeight();
    window.addEventListener('resize', syncSheetHeight);

    return () => {
      window.removeEventListener('resize', syncSheetHeight);
    };
  }, [activeSheet, ordersQuery.data, promoMutation.error, promoMutation.isPending, hasActivePromo]);

  useLayoutEffect(() => {
    if (!activeSheet) {
      setSheetContentHeight(null);
      return undefined;
    }

    const syncSheetMetrics = () => {
      const bodyElement = sheetBodyRef.current;
      if (!bodyElement) {
        return;
      }

      const maxContentHeight = Math.min(window.innerHeight * 0.78, 640);
      const nextContentHeight = Math.min(bodyElement.scrollHeight, maxContentHeight);

      if (sheetInitialHeightRef.current === null) {
        sheetInitialHeightRef.current = nextContentHeight;
      }

      setSheetContentHeight((current) => (
        current !== null && Math.abs(current - nextContentHeight) < 1
          ? current
          : nextContentHeight
      ));

      window.requestAnimationFrame(() => {
        setSheetHeight(sheetRef.current?.getBoundingClientRect().height ?? 0);
      });
    };

    syncSheetMetrics();
    const resizeObserver = new ResizeObserver(() => {
      syncSheetMetrics();
    });

    if (sheetBodyRef.current) {
      resizeObserver.observe(sheetBodyRef.current);
    }

    if (sheetRef.current) {
      resizeObserver.observe(sheetRef.current);
    }

    window.addEventListener('resize', syncSheetMetrics);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', syncSheetMetrics);
    };
  }, [
    activeSheet,
    historyItems.length,
    ordersQuery.isLoading,
    promoMutation.isPending,
    promoMutation.error,
    addAddressMutation.error,
    hasActivePromo,
    profileAddresses.length,
    addressesMode,
  ]);

  useEffect(() => () => {
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
    }
  }, []);

  return (
    <section className="profile-page">
      {profile ? (
        <div className="profile-page__stack">
          <section className="profile-page__hero glass-block-soft glass-accent-blue">
            <div className="profile-page__avatar-shell">
              <div className="profile-page__avatar">
                {profile.user.photoUrl ? (
                  <img src={profile.user.photoUrl} alt={profileName} className="profile-page__avatar-image" />
                ) : (
                  <UserRound size={40} />
                )}
              </div>
            </div>
            <div className="profile-page__hero-text">
              <h1 className="profile-page__name">{profileName}</h1>
              <p className="profile-page__meta">{profilePageContent.profileIdLabel} {profile.user.telegramId}</p>
              <p className="profile-page__meta">{profilePageContent.profileRegisteredPrefix} {registeredAt}</p>
            </div>
          </section>
          <section className="profile-page__metrics">
            <article className="profile-page__metric glass-block-soft glass-accent-blue">
              <p className="profile-page__metric-value">{activeCity}</p>
              <p className="profile-page__metric-label">{profilePageContent.cityLabel}</p>
            </article>
            <article className="profile-page__metric glass-block-soft glass-accent-blue">
              <p className="profile-page__metric-value">{ratingValue}</p>
              <p className="profile-page__metric-label">{profilePageContent.ratingLabel}</p>
            </article>
            <article className="profile-page__metric glass-block-soft glass-accent-blue">
              <p className="profile-page__metric-value">{ordersValue}</p>
              <p className="profile-page__metric-label">{profilePageContent.ordersLabel}</p>
            </article>
          </section>

          <section className="profile-page__actions">
            <button
              type="button"
              className="profile-page__action"
              onClick={() => openSheet('history')}
            >
              <span className="support-page__detail-icon profile-page__action-icon" aria-hidden="true">
                <MaskedIcon src={historyIcon} className="profile-page__action-svg profile-page__action-svg--history" />
              </span>
              <span className="profile-page__action-text">{profilePageContent.historyLabel}</span>
            </button>
            <button
              type="button"
              className="profile-page__action"
              onClick={() => openSheet('promo')}
            >
              <span className="support-page__detail-icon profile-page__action-icon" aria-hidden="true">
                <MaskedIcon src={discountIcon} className="profile-page__action-svg profile-page__action-svg--promo" />
              </span>
              <span className="profile-page__action-text">{profilePageContent.promoLabel}</span>
            </button>
            {isAddressSystemEnabled ? (
              <button
                type="button"
                className="profile-page__action"
                onClick={() => openSheet('addresses')}
              >
                <span className="support-page__detail-icon profile-page__action-icon" aria-hidden="true">
                  <MaskedIcon src={geoHomeIcon} className="profile-page__action-svg profile-page__action-svg--addresses" />
                </span>
                <span className="profile-page__action-text">{profilePageContent.addressesLabel}</span>
              </button>
            ) : null}
            <button
              type="button"
              className="profile-page__action"
              onClick={() => navigate('/models?section=favorites')}
            >
              <span className="support-page__detail-icon profile-page__action-icon" aria-hidden="true">
                <MaskedIcon src={savedIcon} className="profile-page__action-svg profile-page__action-svg--favorites" />
              </span>
              <span className="profile-page__action-text">{profilePageContent.favoritesLabel}</span>
            </button>
          </section>
        </div>
      ) : (
        <div className="profile-page__loading" aria-label={profilePageContent.loadingLabel} aria-busy="true">
          <div className="app-loading-spinner" aria-hidden="true" />
        </div>
      )}

      {activeSheet ? createPortal(
        <>
          <button
            type="button"
            className="models-sheet-backdrop"
            aria-label={profilePageContent.sheetCloseLabel}
            onClick={closeSheet}
            style={{
              opacity: sheetProgress,
              background: `rgba(9, 10, 14, ${0.1 + (sheetProgress * 0.16)})`,
              backdropFilter: `blur(${sheetProgress * 16}px)`,
              WebkitBackdropFilter: `blur(${sheetProgress * 16}px)`,
              transition: isSheetDragging
                ? 'none'
                : `opacity ${PROFILE_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), background ${PROFILE_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), backdrop-filter ${PROFILE_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), -webkit-backdrop-filter ${PROFILE_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          />
          <section
            ref={sheetRef}
            className="models-sheet profile-page__sheet"
            aria-label={
              activeSheet === 'history'
                ? profilePageContent.historySheetTitle
                : activeSheet === 'promo'
                  ? profilePageContent.promoSheetTitle
                  : addressesMode === 'create'
                    ? profilePageContent.addressesCreateTitle
                    : profilePageContent.addressesSheetTitle
            }
            style={{
              transform: `translateY(${sheetTranslateY}px)`,
              transition: isSheetDragging ? 'none' : `transform ${PROFILE_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          >
            <button
              type="button"
              className="models-sheet__drag"
              aria-label={profilePageContent.sheetCloseLabel}
              onPointerDown={handleSheetDragStart}
              onPointerMove={handleSheetDragMove}
              onPointerUp={handleSheetDragEnd}
              onPointerCancel={handleSheetDragEnd}
            />
              <div
                ref={sheetContentRef}
                className="models-sheet__content"
                style={{
                  ...(sheetContentHeight ? { height: `${sheetContentHeight}px` } : {}),
                  transition: isSheetDragging ? 'none' : `height ${PROFILE_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
                }}
              >
              <div
                ref={sheetBodyRef}
                className="profile-page__sheet-body"
                onTouchStart={handleSheetScrollTouchStart}
                onTouchMove={handleSheetScrollTouchMove}
              >
                <div className="profile-page__sheet-header">
                  <button
                    type="button"
                    className="models-booking__back-btn"
                    onClick={handleSheetBack}
                    aria-label="Назад"
                  >
                    <ChevronLeft size={15} />
                    <span>Назад</span>
                  </button>
                  <p className="profile-page__sheet-title">
                    {activeSheet === 'history'
                      ? profilePageContent.historySheetTitle
                      : activeSheet === 'promo'
                        ? profilePageContent.promoSheetTitle
                        : addressesMode === 'create'
                          ? profilePageContent.addressesCreateTitle
                          : profilePageContent.addressesSheetTitle}
                  </p>
                    {(activeSheet === 'history'
                      ? profilePageContent.historySheetSubtitle
                      : activeSheet === 'promo'
                        ? profilePageContent.promoSheetSubtitle
                        : addressesMode === 'create'
                          ? profilePageContent.addressesCreateSubtitle
                          : profilePageContent.addressesSheetSubtitle) ? (
                      <p className="profile-page__sheet-subtitle">
                        {activeSheet === 'history'
                          ? profilePageContent.historySheetSubtitle
                          : activeSheet === 'promo'
                            ? profilePageContent.promoSheetSubtitle
                            : addressesMode === 'create'
                              ? profilePageContent.addressesCreateSubtitle
                              : profilePageContent.addressesSheetSubtitle}
                      </p>
                    ) : null}
                </div>

                {activeSheet === 'history' ? (
                  <>
                    {ordersQuery.isLoading && !historyItems.length ? (
                      <div className="profile-page__sheet-state glass-block-muted">
                        {profilePageContent.historyLoadingLabel}
                      </div>
                    ) : historyItems.length ? (
                      <div
                        className="profile-page__orders"
                        onTouchStart={handleSheetScrollTouchStart}
                        onTouchMove={handleSheetScrollTouchMove}
                      >
                        {historyItems.map((order) => (
                          <article key={order.number} className="profile-page__order-card">
                            <div className="profile-page__order-topline">
                              <span className="profile-page__order-number">
                                {profilePageContent.historyOrderNumberLabel} #{order.number}
                              </span>
                              <span className={`profile-page__order-status profile-page__order-status--${order.status}`}>
                                {getOrderStatusLabel(order.status)}
                              </span>
                            </div>
                            <p className="profile-page__order-model">
                              {order.modelInfo || profilePageContent.historyOrderModelFallback}
                            </p>
                            <p className="profile-page__order-meta">
                              {order.date ? formatDate(order.date) : profilePageContent.historyOrderDateFallback}
                            </p>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <div className="profile-page__sheet-state">
                        {profilePageContent.historyEmptyLabel}
                      </div>
                    )}
                  </>
                ) : activeSheet === 'promo' ? (
                  <div className={`profile-page__promo-sheet${hasActivePromo ? ' profile-page__promo-sheet--active' : ''}`}>
                    {hasActivePromo ? (
                      <div className="profile-page__promo-status">
                        <>
                          <p className="profile-page__promo-status-title">
                            {profilePageContent.promoActivePrefix}: {activePromoCode}
                          </p>
                          <p className="profile-page__promo-status-subtitle">
                            {profilePageContent.promoActiveAmountPrefix}: {formatPromoAmount(activePromoAmount)}
                          </p>
                        </>
                      </div>
                    ) : null}

                    {!hasActivePromo ? (
                      <form className="profile-page__promo-form" onSubmit={handlePromoSubmit}>
                        <label className="profile-page__promo-input">
                          <input
                            className="profile-page__promo-input-field"
                            type="text"
                            value={promoCode}
                            onChange={(event) => setPromoCode(event.target.value)}
                            placeholder={profilePageContent.promoInputPlaceholder}
                            disabled={promoMutation.isPending}
                          />
                        </label>

                        <button
                          type="submit"
                          className="profile-page__sheet-action"
                          disabled={!promoCode.trim() || promoMutation.isPending}
                        >
                          {promoMutation.isPending ? profilePageContent.promoLoadingLabel : profilePageContent.promoActivateLabel}
                        </button>
                      </form>
                    ) : null}

                    {promoMutation.isSuccess && promoMutation.data.promo.code ? (
                      <p className="profile-page__promo-feedback profile-page__promo-feedback--success">
                        {profilePageContent.promoSuccessPrefix}: {promoMutation.data.promo.code}
                      </p>
                    ) : null}

                    {promoMutation.error ? (
                      <p className="profile-page__promo-feedback profile-page__promo-feedback--error">
                        {getPromoErrorMessage(promoMutation.error.message)}
                      </p>
                    ) : null}
                  </div>
                ) : activeSheet === 'addresses' ? (
                  addressesMode === 'create' ? (
                    <form className="profile-page__promo-form" onSubmit={handleAddressSubmit}>
                      <label className="profile-page__promo-input">
                        <input
                          className="profile-page__promo-input-field"
                          type="text"
                          value={addressTitle}
                          onChange={(event) => setAddressTitle(event.target.value)}
                          placeholder={profilePageContent.addressesTitlePlaceholder}
                          disabled={addAddressMutation.isPending}
                        />
                      </label>

                      <label className="profile-page__promo-input">
                        <input
                          className="profile-page__promo-input-field"
                          type="text"
                          value={addressValue}
                          onChange={(event) => setAddressValue(event.target.value)}
                          placeholder={profilePageContent.addressesValuePlaceholder}
                          disabled={addAddressMutation.isPending}
                          autoComplete="street-address"
                        />
                      </label>

                      <button
                        type="submit"
                        className="profile-page__sheet-action"
                        disabled={!addressTitle.trim() || !addressValue.trim() || addAddressMutation.isPending}
                      >
                        {addAddressMutation.isPending ? profilePageContent.loadingLabel : profilePageContent.addressesConfirmLabel}
                      </button>

                      {addAddressMutation.error ? (
                        <p className="profile-page__promo-feedback profile-page__promo-feedback--error">
                          {addAddressMutation.error.message}
                        </p>
                      ) : null}
                    </form>
                  ) : (
                    <div className="profile-page__promo-sheet">
                      {profileAddresses.length ? (
                        <div
                          className="profile-page__orders"
                          onTouchStart={handleSheetScrollTouchStart}
                          onTouchMove={handleSheetScrollTouchMove}
                        >
                          {profileAddresses.map((item: ProfileAddressItem) => (
                            <article key={item.id} className="profile-page__order-card">
                              <p className="profile-page__order-model">{item.title}</p>
                              <p className="profile-page__order-meta">{item.address}</p>
                            </article>
                          ))}
                        </div>
                      ) : (
                        <div className="profile-page__sheet-state">
                          {profilePageContent.addressesEmptyLabel}
                        </div>
                      )}

                      <button
                        type="button"
                        className="profile-page__sheet-action"
                        onClick={openAddressesCreateMode}
                      >
                        {profilePageContent.addressesAddLabel}
                      </button>
                    </div>
                  )
                ) : null}
              </div>
            </div>
          </section>
        </>,
        document.body,
      ) : null}
    </section>
  );
}
