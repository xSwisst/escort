import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChevronDown, ChevronLeft, ChevronRight, Plus, Sparkles } from 'lucide-react';
import { createPortal } from 'react-dom';
import { useSearchParams } from 'react-router-dom';

import eyeSlashIcon from '@/assets/icons/eye-slash.svg';
import filterIcon from '@/assets/icons/filter.svg';
import heartCrackIcon from '@/assets/icons/heart-crack.svg';
import heartIcon from '@/assets/icons/heart.svg';
import heartXmarkIcon from '@/assets/icons/heart-xmark.svg';
import shieldHeartIcon from '@/assets/icons/shield-heart.svg';
import sortIcon from '@/assets/icons/sort.svg';
import telegramIcon from '@/assets/icons/telegram.svg';
import trueIcon from '@/assets/icons/true.svg';
import { useSessionStore } from '@/entities/session/sessionStore';
import { addFavorite, addProfileAddress, getFavorites, getModel, getModels, getProfile, getSupport, markModelOpened, prepareModelBooking, removeFavorite, resolveModelBookingPayment, setProfileCity, setProfileCityStatus } from '@/shared/api/webAppApi';
import { formatPrice } from '@/shared/lib/format';
import { normalizeTelegramHref } from '@/shared/lib/telegram';
import type { BookingPaymentMethodKey, BookingPaymentResponse, BookingPrepareRequest, BookingPrepareResponse, FavoriteCodesResponse, ModelSummary, ProfileResponse } from '@/shared/types/web-app';
import { MaskedIcon } from '@/shared/ui/MaskedIcon';
import { SearchIcon } from '@/shared/ui/SearchIcon';
import modelsPageContentRaw from './modelsPageContent.yaml?raw';

const modelsPageContent = JSON.parse(modelsPageContentRaw) as {
  allModelsLabel: string;
  favoriteModelsLabel: string;
  quickSearchPlaceholder: string;
  filterButtonLabel: string;
  sortButtonLabel: string;
  sortSheetCloseLabel: string;
  sortSheetDoneLabel: string;
  sortLatestLabel: string;
  sortPriceAscLabel: string;
  sortPriceDescLabel: string;
  sortRatingAscLabel: string;
  sortRatingDescLabel: string;
  cardAction: string;
  cardVerificationLabel: string;
  cardHealthLabel: string;
  favoriteAddLabel: string;
  favoriteRemoveLabel: string;
  sheetCloseLabel: string;
  sheetReviewWord: string;
  sheetActionLabel: string;
  sheetAgeLabel: string;
  sheetHeightLabel: string;
  sheetSizeLabel: string;
  sheetOneHourLabel: string;
  sheetTwoHoursLabel: string;
  sheetThreeHoursLabel: string;
  sheetNightLabel: string;
  sheetAdditionalsTitle: string;
  sheetAboutTitle: string;
  sheetServicesTitle: string;
  sheetDescriptionFallback: string;
  sheetServicesFallback: string;
  sheetLoadingLabel: string;
  emptyModelsLabel: string;
  emptyFavoritesLabel: string;
  cityGateTitle: string;
  cityGateDescription: string;
  cityGatePlaceholder: string;
  cityGateSubmitLabel: string;
  cityGateLoadingLabel: string;
  cityGateErrorFallback: string;
  cityGateNotFoundLabel: string;
  citySwitcherToggleLabel: string;
  citySwitcherMenuTitle: string;
  citySwitcherSelectedPrefix: string;
  citySwitcherAddLabel: string;
  citySwitcherAddButtonLabel: string;
  citySwitcherAddTitle: string;
  citySwitcherBackLabel: string;
  citySwitcherCloseLabel: string;
  bookingBackLabel: string;
  bookingDateTimeTitle: string;
  bookingDateWheelTitle: string;
  bookingTimeWheelTitle: string;
  bookingContinueLabel: string;
  bookingPlaceTitle: string;
  bookingAddressTitle: string;
  bookingTariffTitle: string;
  bookingAdditionalsTitle: string;
  bookingPaymentMethodTitle: string;
  bookingPaymentTitle: string;
  bookingPaymentLoadingLabel: string;
  bookingPlaceAtModelLabel: string;
  bookingPlaceAtMineLabel: string;
  bookingAddressEmptyLabel: string;
  bookingAddressAddLabel: string;
  bookingAddressCreateTitle: string;
  bookingAddressTitlePlaceholder: string;
  bookingAddressValuePlaceholder: string;
  bookingAddressConfirmLabel: string;
  bookingTariffOneHourLabel: string;
  bookingTariffTwoHoursLabel: string;
  bookingTariffThreeHoursLabel: string;
  bookingTariffNightLabel: string;
  bookingPaymentCardLabel: string;
  bookingPaymentCashLabel: string;
  bookingSummaryDateLabel: string;
  bookingSummaryTimeLabel: string;
  bookingSummaryPlaceLabel: string;
  bookingSummaryAddressLabel: string;
  bookingSummaryTariffLabel: string;
  bookingSummaryAmountLabel: string;
  bookingPaymentOrderLabel: string;
  bookingPaymentModelLabel: string;
  bookingPaymentMethodLabel: string;
  bookingPaymentBankLabel: string;
  bookingPaymentHolderLabel: string;
  bookingPaymentRequisitesTitle: string;
  bookingSupportTitle: string;
  bookingSupportDescription: string;
  bookingSupportActionLabel: string;
  bookingEmptySupportLinkLabel: string;
  bookingCashUnavailableTitle: string;
  bookingCashUnavailableDescription: string;
};

type ModelsSection = 'all' | 'favorites';
type ModelsSortOption = 'latest' | 'priceAsc' | 'priceDesc' | 'ratingAsc' | 'ratingDesc';
type ModelsSectionTransition = 'static' | 'slide-left' | 'slide-right';
type BookingStep = 'datetime' | 'place' | 'address' | 'tariff' | 'additionals' | 'payment-method' | 'payment';
type BookingAddressMode = 'list' | 'create';
type BookingPlace = BookingPrepareRequest['meetingPlace'];
type BookingTariffKey = BookingPrepareRequest['tariff'];
type FavoriteExitGhost = {
  code: string;
  item: ModelSummary;
  rect: {
    top: number;
    left: number;
    width: number;
    height: number;
  };
};

const SHEET_TRANSITION_MS = 420;
const SHEET_OUTER_ELASTIC_FACTOR = 1.5;
const SORT_SHEET_TRANSITION_MS = 420;
const FAVORITE_EXIT_TRANSITION_MS = 420;
const FAVORITE_ICON_JELLO_MS = 560;
const FAVORITE_ICON_SHAKE_MS = 220;
const CITY_SWITCHER_TRANSITION_MS = 420;
const PROFILE_QUERY_STALE_MS = 5 * 60 * 1000;
const MODELS_QUERY_STALE_MS = 2 * 60 * 1000;
const MODEL_DETAILS_QUERY_STALE_MS = 10 * 60 * 1000;
const SUPPORT_QUERY_STALE_MS = 30 * 60 * 1000;
const MODEL_DETAILS_PREFETCH_LIMIT = 6;
const HERO_AUTOPLAY_MS = 3000;
const HERO_TRANSITION_MS = 900;
const HERO_REPEAT_MULTIPLIER = 3;

function applyElasticResistance(distance: number, factor: number) {
  return Math.sqrt(Math.max(0, distance)) * factor;
}

function HealthBadgeIcon() {
  return <MaskedIcon src={shieldHeartIcon} className="model-card__badge-icon model-card__badge-icon--health" />;
}

function CheckBadgeIcon() {
  return <MaskedIcon src={trueIcon} className="model-card__badge-icon model-card__badge-icon--check" />;
}

function RatingStarIcon() {
  return (
    <svg viewBox="0 0 576 512" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" className="models-sheet__rating-icon">
      <path
        d="M309.5-18.9c-4.1-8-12.4-13.1-21.4-13.1s-17.3 5.1-21.4 13.1L193.1 125.3 33.2 150.7c-8.9 1.4-16.3 7.7-19.1 16.3s-.5 18 5.8 24.4l114.4 114.5-25.2 159.9c-1.4 8.9 2.3 17.9 9.6 23.2s16.9 6.1 25 2L288.1 417.6 432.4 491c8 4.1 17.7 3.3 25-2s11-14.2 9.6-23.2L441.7 305.9 556.1 191.4c6.4-6.4 8.6-15.8 5.8-24.4s-10.1-14.9-19.1-16.3L383 125.3 309.5-18.9z"
        fill="currentColor"
      />
    </svg>
  );
}

function TelegramActionIcon() {
  return <MaskedIcon src={telegramIcon} className="models-booking__support-cta-svg" />;
}

function getCityGateErrorMessage(error: Error | null, notFoundLabel: string, fallbackLabel: string) {
  const normalized = error?.message?.trim().toLowerCase() ?? '';

  if (
    normalized === 'not found'
    || normalized === 'not found.'
    || normalized === 'такой город не был найден'
    || normalized === 'город не найден'
    || normalized === 'город не найден.'
  ) {
    return notFoundLabel;
  }

  return error?.message || fallbackLabel;
}

function createEmptyBookingSelection() {
  return {
    selectedDate: null as string | null,
    selectedTime: null as string | null,
    selectedPlace: null as BookingPlace | null,
    selectedAddressId: null as number | null,
    selectedTariff: null as BookingTariffKey | null,
    selectedAdditionalIds: [] as number[],
  };
}

const bannerImages = Object.entries(
  import.meta.glob('../../assets/banners/*.{avif,jpeg,jpg,png,webp}', {
    eager: true,
    import: 'default',
    query: '?url',
  }) as Record<string, string>,
)
  .sort(([firstPath], [secondPath]) => firstPath.localeCompare(secondPath))
  .map(([, source]) => source);

const preloadedBannerSources = new Set<string>();

function preloadBannerImages(sources: string[]) {
  if (typeof window === 'undefined') {
    return;
  }

  sources.forEach((source) => {
    if (!source || preloadedBannerSources.has(source)) {
      return;
    }

    preloadedBannerSources.add(source);
    const image = new window.Image();
    image.decoding = 'async';
    image.src = source;
  });
}

function HeroCarousel() {
  const images = bannerImages.length > 0 ? bannerImages : ['/banner.jpg'];
  const isCarousel = images.length > 1;
  const slides = isCarousel ? Array.from({ length: HERO_REPEAT_MULTIPLIER }, () => images).flat() : images;
  const middleOffset = isCarousel ? images.length : 0;
  const [slideIndex, setSlideIndex] = useState(middleOffset);
  const [isAnimated, setIsAnimated] = useState(true);
  const [timerVersion, setTimerVersion] = useState(0);
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const pointerStartXRef = useRef<number | null>(null);

  useEffect(() => {
    preloadBannerImages(images);
  }, [images]);

  useEffect(() => {
    if (!isCarousel) return undefined;

    const timer = window.setInterval(() => {
      setIsAnimated(true);
      setSlideIndex((current) => current + 1);
    }, HERO_AUTOPLAY_MS);

    return () => window.clearInterval(timer);
  }, [isCarousel, isDragging, timerVersion]);

  useEffect(() => {
    if (!isCarousel) {
      setSlideIndex(0);
      return;
    }

    setSlideIndex(images.length);
    setIsAnimated(false);
    setDragOffset(0);
  }, [images.length, isCarousel]);

  const move = (direction: -1 | 1) => {
    if (!isCarousel) return;
    setIsAnimated(true);
    setSlideIndex((current) => current + direction);
    setTimerVersion((current) => current + 1);
  };

  const handleTransitionEnd = () => {
    if (!isCarousel) return;

    if (slideIndex < images.length) {
      setIsAnimated(false);
      setSlideIndex((current) => current + images.length);
    } else if (slideIndex >= images.length * 2) {
      setIsAnimated(false);
      setSlideIndex((current) => current - images.length);
    }
  };

  return (
    <div
      className="hero"
      aria-label="Баннеры"
      onPointerDown={(event) => {
        if (!isCarousel) return;
        pointerStartXRef.current = event.clientX;
        setIsDragging(true);
        setIsAnimated(false);
        setDragOffset(0);
        event.currentTarget.setPointerCapture(event.pointerId);
      }}
      onPointerMove={(event) => {
        if (pointerStartXRef.current === null) return;
        setDragOffset(event.clientX - pointerStartXRef.current);
      }}
      onPointerUp={(event) => {
        if (pointerStartXRef.current === null) return;
        const distance = event.clientX - pointerStartXRef.current;
        const threshold = event.currentTarget.clientWidth * 0.18;
        pointerStartXRef.current = null;
        setIsDragging(false);
        setDragOffset(0);
        setIsAnimated(true);
        if (event.currentTarget.hasPointerCapture(event.pointerId)) {
          event.currentTarget.releasePointerCapture(event.pointerId);
        }
        if (Math.abs(distance) >= threshold) {
          move(distance < 0 ? 1 : -1);
        } else {
          setTimerVersion((current) => current + 1);
        }
      }}
      onPointerCancel={() => {
        pointerStartXRef.current = null;
        setIsDragging(false);
        setDragOffset(0);
        setIsAnimated(true);
      }}
    >
      <div
        className="hero__track"
        style={{
          transform: `translateX(calc(-${slideIndex * 100}% - ${slideIndex * 15}px + ${dragOffset}px))`,
          transition: isAnimated ? `transform ${HERO_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)` : 'none',
        }}
        onTransitionEnd={handleTransitionEnd}
      >
        {slides.map((source, index) => (
          <img key={`${source}-${index}`} src={source} alt="Баннер" draggable={false} decoding="async" />
        ))}
      </div>
    </div>
  );
}

export function ModelsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const token = useSessionStore((state) => state.session?.sessionToken ?? '');
  const queryClient = useQueryClient();
  const profileQuery = useQuery({
    queryKey: ['profile', token],
    queryFn: () => getProfile(token),
    enabled: Boolean(token),
    staleTime: PROFILE_QUERY_STALE_MS,
  });
  const activeCitySlot = Math.max(1, profileQuery.data?.client.cityStatus || 1);
  const firstCity = profileQuery.data?.client.firstCity?.trim() ?? '';
  const secondCity = profileQuery.data?.client.secondCity?.trim() ?? '';
  const profileAddresses = profileQuery.data?.addresses ?? [];
  const isAddressSystemEnabled = Boolean(profileQuery.data?.client.addressSystemEnabled);
  const activeCity = (
    activeCitySlot === 2
      ? secondCity
      : firstCity
  )?.trim() ?? '';
  const hasActiveCity = Boolean(activeCity);
  const isProfileGateLoading = !token || profileQuery.isPending || (profileQuery.isFetching && !profileQuery.data);
  const citySlots = [
    { slot: 1, city: firstCity },
    { slot: 2, city: secondCity },
  ] as const;
  const query = useQuery({
    queryKey: ['models', token],
    queryFn: () => getModels(token),
    enabled: Boolean(token && hasActiveCity),
    staleTime: MODELS_QUERY_STALE_MS,
  });
  const favoritesQuery = useQuery({
    queryKey: ['favorites', token],
    queryFn: () => getFavorites(token),
    enabled: Boolean(token && hasActiveCity),
    staleTime: MODELS_QUERY_STALE_MS,
  });
  const items = useMemo<ModelSummary[]>(() => query.data?.items ?? [], [query.data]);
  const [favoriteCodes, setFavoriteCodes] = useState<string[]>([]);
  const [exitingFavoriteCodes, setExitingFavoriteCodes] = useState<string[]>([]);
  const [favoriteExitGhosts, setFavoriteExitGhosts] = useState<FavoriteExitGhost[]>([]);
  const [favoriteIconAnimations, setFavoriteIconAnimations] = useState<Record<string, 'jello' | 'shake'>>({});
  const [cityValue, setCityValue] = useState('');
  const [isCitySwitcherMounted, setIsCitySwitcherMounted] = useState(false);
  const [isCitySwitcherOpen, setIsCitySwitcherOpen] = useState(false);
  const [isCitySwitcherDragging, setIsCitySwitcherDragging] = useState(false);
  const [citySwitcherOffset, setCitySwitcherOffset] = useState(0);
  const [citySwitcherHeight, setCitySwitcherHeight] = useState(0);
  const [citySwitcherMode, setCitySwitcherMode] = useState<'list' | 'add'>('list');
  const initialSection = searchParams.get('section') === 'favorites' ? 'favorites' : 'all';
  const [activeSection, setActiveSection] = useState<ModelsSection>(initialSection);
  const [sectionTransition, setSectionTransition] = useState<ModelsSectionTransition>('static');
  const [appliedSort, setAppliedSort] = useState<ModelsSortOption>('latest');
  const [pendingSort, setPendingSort] = useState<ModelsSortOption>('latest');
  const [searchValue, setSearchValue] = useState('');
  const [isSortSheetMounted, setIsSortSheetMounted] = useState(false);
  const [isSortSheetOpen, setIsSortSheetOpen] = useState(false);
  const [isSortSheetDragging, setIsSortSheetDragging] = useState(false);
  const [sortSheetOffset, setSortSheetOffset] = useState(0);
  const [sortSheetHeight, setSortSheetHeight] = useState(0);
  const [sheetModel, setSheetModel] = useState<ModelSummary | null>(null);
  const [activePhotoIndex, setActivePhotoIndex] = useState(0);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isBookingFlowOpen, setIsBookingFlowOpen] = useState(false);
  const [bookingStep, setBookingStep] = useState<BookingStep>('datetime');
  const [bookingAddressMode, setBookingAddressMode] = useState<BookingAddressMode>('list');
  const [bookingSelection, setBookingSelection] = useState(createEmptyBookingSelection);
  const [bookingAddressTitle, setBookingAddressTitle] = useState('');
  const [bookingAddressValue, setBookingAddressValue] = useState('');
  const [expandedBookingSelect, setExpandedBookingSelect] = useState<'date' | 'time' | null>(null);
  const [preparedBooking, setPreparedBooking] = useState<BookingPrepareResponse | null>(null);
  const [bookingPayment, setBookingPayment] = useState<BookingPaymentResponse | null>(null);
  const [isSheetDragging, setIsSheetDragging] = useState(false);
  const [sheetOffset, setSheetOffset] = useState(0);
  const [sheetHeight, setSheetHeight] = useState(0);
  const [sheetContentHeight, setSheetContentHeight] = useState<number | null>(null);
  const [citySwitcherContentHeight, setCitySwitcherContentHeight] = useState<number | null>(null);
  const sortSheetRef = useRef<HTMLElement | null>(null);
  const citySwitcherSheetRef = useRef<HTMLElement | null>(null);
  const sheetRef = useRef<HTMLElement | null>(null);
  const sheetContentRef = useRef<HTMLDivElement | null>(null);
  const sheetScrollRef = useRef<HTMLDivElement | null>(null);
  const sheetScrollInnerRef = useRef<HTMLDivElement | null>(null);
  const bookingBodyRef = useRef<HTMLDivElement | null>(null);
  const closeTimeoutRef = useRef<number | null>(null);
  const sortSheetCloseTimeoutRef = useRef<number | null>(null);
  const citySwitcherCloseTimeoutRef = useRef<number | null>(null);
  const sortDragPointerIdRef = useRef<number | null>(null);
  const sortDragStartYRef = useRef(0);
  const sortDragStartOffsetRef = useRef(0);
  const sortSheetOffsetRef = useRef(0);
  const citySwitcherDragPointerIdRef = useRef<number | null>(null);
  const citySwitcherDragStartYRef = useRef(0);
  const citySwitcherDragStartOffsetRef = useRef(0);
  const citySwitcherOffsetRef = useRef(0);
  const citySwitcherHasScrollRef = useRef(false);
  const citySwitcherDragStartHeightRef = useRef(0);
  const dragPointerIdRef = useRef<number | null>(null);
  const dragStartYRef = useRef(0);
  const dragStartOffsetRef = useRef(0);
  const sheetOffsetRef = useRef(0);
  const sheetHasScrollRef = useRef(false);
  const sheetInitialHeightRef = useRef<number | null>(null);
  const sheetDragStartHeightRef = useRef(0);
  const photoTouchStartXRef = useRef(0);
  const photoTouchStartYRef = useRef(0);
  const sheetScrollTouchStartYRef = useRef(0);
  const favoriteExitTimeoutsRef = useRef<Record<string, number>>({});
  const favoriteIconAnimationTimeoutsRef = useRef<Record<string, number>>({});
  const favoriteExitKickoffTimeoutsRef = useRef<Record<string, number>>({});
  const favoriteSlotRefs = useRef<Record<string, HTMLElement | null>>({});
  const previousFavoriteSlotRectsRef = useRef<Record<string, DOMRect>>({});
  const favoriteLayoutReadyRef = useRef(false);
  const favoriteLayoutFrameRef = useRef<number | null>(null);
  const sheetQuery = useQuery({
    queryKey: ['model-sheet', token, sheetModel?.code],
    queryFn: () => getModel(token, sheetModel?.code ?? ''),
    enabled: Boolean(token && sheetModel?.code && hasActiveCity),
    staleTime: MODEL_DETAILS_QUERY_STALE_MS,
  });
  const supportQuery = useQuery({
    queryKey: ['support', token],
    queryFn: () => getSupport(token),
    enabled: Boolean(token && isBookingFlowOpen),
    staleTime: SUPPORT_QUERY_STALE_MS,
  });
  const filteredItems = useMemo(
    () => items.filter((item) => item.code.toLowerCase().includes(searchValue.trim().toLowerCase())),
    [items, searchValue],
  );
  const sectionItems = useMemo(
    () => (
      activeSection === 'favorites'
        ? filteredItems.filter((item) => favoriteCodes.includes(item.code))
        : filteredItems
    ),
    [activeSection, favoriteCodes, filteredItems],
  );
  const visibleItems = useMemo(() => {
    const source = sectionItems.map((item, index) => ({ item, index }));

    const getPrice = (item: ModelSummary) => item.prices.oneHour ?? null;
    const getRating = (item: ModelSummary) => item.rating ?? null;
    const compareNullableNumber = (left: number | null, right: number | null, direction: 'asc' | 'desc') => {
      if (left == null && right == null) {
        return 0;
      }

      if (left == null) {
        return 1;
      }

      if (right == null) {
        return -1;
      }

      return direction === 'asc' ? left - right : right - left;
    };

    switch (appliedSort) {
      case 'priceAsc':
        source.sort((left, right) => compareNullableNumber(getPrice(left.item), getPrice(right.item), 'asc'));
        break;
      case 'priceDesc':
        source.sort((left, right) => compareNullableNumber(getPrice(left.item), getPrice(right.item), 'desc'));
        break;
      case 'ratingAsc':
        source.sort((left, right) => compareNullableNumber(getRating(left.item), getRating(right.item), 'asc'));
        break;
      case 'ratingDesc':
        source.sort((left, right) => compareNullableNumber(getRating(left.item), getRating(right.item), 'desc'));
        break;
      case 'latest':
      default:
        source.sort((left, right) => left.index - right.index);
        break;
    }

    return source.map(({ item }) => item);
  }, [appliedSort, sectionItems]);
  const sortOptions = useMemo(
    () => [
      { value: 'latest' as const, label: modelsPageContent.sortLatestLabel },
      { value: 'priceAsc' as const, label: modelsPageContent.sortPriceAscLabel },
      { value: 'priceDesc' as const, label: modelsPageContent.sortPriceDescLabel },
      { value: 'ratingAsc' as const, label: modelsPageContent.sortRatingAscLabel },
      { value: 'ratingDesc' as const, label: modelsPageContent.sortRatingDescLabel },
    ],
    [],
  );
  const detailModel = sheetQuery.data;
  const sheetPhotos = useMemo(
    () => (
      detailModel?.photoUrls?.filter(Boolean).length
        ? detailModel.photoUrls.filter(Boolean)
        : sheetModel?.photoUrls?.filter(Boolean).length
          ? sheetModel.photoUrls.filter(Boolean)
          : sheetModel?.previewPhotoUrl
            ? [sheetModel.previewPhotoUrl]
            : []
    ),
    [detailModel, sheetModel],
  );
  const sheetRatingValue = detailModel?.rating ?? sheetModel?.rating ?? null;
  const sheetReviewsCount = detailModel?.reviews.length ?? sheetModel?.reviewsCount ?? 0;
  const prefetchModelDetails = (code: string) => queryClient.prefetchQuery({
    queryKey: ['model-sheet', token, code],
    queryFn: () => getModel(token, code),
    staleTime: MODEL_DETAILS_QUERY_STALE_MS,
  });

  useEffect(() => {
    if (!token || !hasActiveCity || !visibleItems.length) {
      return;
    }

    visibleItems.slice(0, MODEL_DETAILS_PREFETCH_LIMIT).forEach((item) => {
      void prefetchModelDetails(item.code);
    });
  }, [hasActiveCity, token, visibleItems]);
  const sheetServices = useMemo(
    () => detailModel?.services?.map((service: { name: string }) => service.name).filter(Boolean) ?? [],
    [detailModel],
  );
  const sheetPriceItems = useMemo(() => {
    const prices = detailModel?.prices ?? sheetModel?.prices;

    if (!prices) {
      return [];
    }

    return [
      { key: 'oneHour', label: modelsPageContent.sheetOneHourLabel, value: prices.oneHour },
      { key: 'twoHours', label: modelsPageContent.sheetTwoHoursLabel, value: prices.twoHours },
      { key: 'threeHours', label: modelsPageContent.sheetThreeHoursLabel, value: prices.threeHours },
      { key: 'night', label: modelsPageContent.sheetNightLabel, value: prices.night },
    ].filter((item) => typeof item.value === 'number' && item.value > 0);
  }, [detailModel, sheetModel]);
  const sheetAdditionals = useMemo(
    () => detailModel?.additionals?.filter((additional) => Boolean(additional.name?.trim())) ?? [],
    [detailModel],
  );
  const bookingDateOptions = useMemo(() => {
    const now = new Date();
    const startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const endDate = new Date(now.getFullYear(), now.getMonth() + 2, 0);
    const result: Array<{ key: string; label: string }> = [];

    for (
      let dateValue = new Date(startDate);
      dateValue <= endDate;
      dateValue = new Date(dateValue.getFullYear(), dateValue.getMonth(), dateValue.getDate() + 1)
    ) {
      const iso = [
        dateValue.getFullYear(),
        String(dateValue.getMonth() + 1).padStart(2, '0'),
        String(dateValue.getDate()).padStart(2, '0'),
      ].join('-');

      result.push({
        key: iso,
        label: new Intl.DateTimeFormat('ru-RU', {
          day: '2-digit',
          month: 'short',
        }).format(dateValue),
      });
    }

    return result;
  }, []);
  const bookingTimes = useMemo(
    () => [...Array.from({ length: 23 }, (_, index) => `${String(index + 1).padStart(2, '0')}:00`), '00:00'],
    [],
  );
  const bookingTariffOptions = useMemo(() => {
    const prices = detailModel?.prices ?? sheetModel?.prices;

    if (!prices) {
      return [];
    }

    return [
      { key: '1h' as const, label: modelsPageContent.bookingTariffOneHourLabel, value: prices.oneHour },
      { key: '2h' as const, label: modelsPageContent.bookingTariffTwoHoursLabel, value: prices.twoHours },
      { key: '3h' as const, label: modelsPageContent.bookingTariffThreeHoursLabel, value: prices.threeHours },
      { key: 'night' as const, label: modelsPageContent.bookingTariffNightLabel, value: prices.night },
    ].filter((item) => typeof item.value === 'number' && item.value > 0);
  }, [detailModel, sheetModel]);
  const bookingPlaceLabels = useMemo(
    () => ({
      model: modelsPageContent.bookingPlaceAtModelLabel,
      client: modelsPageContent.bookingPlaceAtMineLabel,
    }),
    [],
  );
  const bookingPaymentMethodLabels = useMemo(
    () => ({
      card: modelsPageContent.bookingPaymentCardLabel,
      cash: modelsPageContent.bookingPaymentCashLabel,
    }),
    [],
  );
  const supportHref = useMemo(
    () => normalizeTelegramHref(supportQuery.data?.supportBotUrl ?? ''),
    [supportQuery.data?.supportBotUrl],
  );
  const selectedBookingTariff = useMemo(
    () => bookingTariffOptions.find((item) => item.key === bookingSelection.selectedTariff) ?? null,
    [bookingSelection.selectedTariff, bookingTariffOptions],
  );
  const selectedBookingAdditionals = useMemo(
    () => sheetAdditionals.filter((additional) => bookingSelection.selectedAdditionalIds.includes(additional.id)),
    [bookingSelection.selectedAdditionalIds, sheetAdditionals],
  );
  const selectedBookingAdditionalsTotal = useMemo(
    () => selectedBookingAdditionals.reduce((total, additional) => total + Math.max(Number(additional.price) || 0, 0), 0),
    [selectedBookingAdditionals],
  );
  const hasBookingAdditionals = sheetAdditionals.length > 0;
  const selectedBookingAddress = useMemo(
    () => profileAddresses.find((item) => item.id === bookingSelection.selectedAddressId) ?? null,
    [bookingSelection.selectedAddressId, profileAddresses],
  );
  const selectedBookingDateOption = useMemo(
    () => bookingDateOptions.find((item) => item.key === bookingSelection.selectedDate) ?? null,
    [bookingDateOptions, bookingSelection.selectedDate],
  );
  const bookingSummaryItems = useMemo(() => {
    const result: Array<{ label: string; value: string }> = [];

    if (bookingSelection.selectedDate) {
      result.push({
        label: modelsPageContent.bookingSummaryDateLabel,
        value: new Intl.DateTimeFormat('ru-RU', {
          day: '2-digit',
          month: 'long',
        }).format(new Date(bookingSelection.selectedDate)),
      });
    }

    if (bookingSelection.selectedTime) {
      result.push({
        label: modelsPageContent.bookingSummaryTimeLabel,
        value: bookingSelection.selectedTime,
      });
    }

    if (bookingSelection.selectedPlace) {
      result.push({
        label: modelsPageContent.bookingSummaryPlaceLabel,
        value: bookingPlaceLabels[bookingSelection.selectedPlace],
      });
    }

    if (bookingSelection.selectedPlace === 'client' && selectedBookingAddress) {
      result.push({
        label: modelsPageContent.bookingSummaryAddressLabel,
        value: selectedBookingAddress.title,
      });
    }

    if (selectedBookingTariff) {
      result.push({
        label: modelsPageContent.bookingSummaryTariffLabel,
        value: selectedBookingTariff.label,
      });
    }

    const computedAmount = preparedBooking?.amount ?? ((selectedBookingTariff?.value ?? 0) + selectedBookingAdditionalsTotal);

    if (preparedBooking?.amount || selectedBookingTariff?.value || selectedBookingAdditionalsTotal) {
      result.push({
        label: modelsPageContent.bookingSummaryAmountLabel,
        value: formatPrice(computedAmount),
      });
    }

    return result;
  }, [bookingPlaceLabels, bookingSelection.selectedDate, bookingSelection.selectedPlace, bookingSelection.selectedTime, modelsPageContent.bookingSummaryAddressLabel, modelsPageContent.bookingSummaryAmountLabel, modelsPageContent.bookingSummaryDateLabel, modelsPageContent.bookingSummaryPlaceLabel, modelsPageContent.bookingSummaryTariffLabel, modelsPageContent.bookingSummaryTimeLabel, preparedBooking?.amount, selectedBookingAdditionalsTotal, selectedBookingAddress, selectedBookingTariff]);
  const sheetClosedOffset = (sheetHeight || 450) + 36;
  const maxSheetDrag = sheetClosedOffset;
  const sheetTranslateY = isSheetOpen ? sheetOffset : sheetClosedOffset;
  const sheetProgress = isSheetOpen ? Math.min(1, Math.max(0, 1 - (sheetOffset / maxSheetDrag))) : 0;
  const sortSheetClosedOffset = (sortSheetHeight || 300) + 36;
  const maxSortSheetDrag = sortSheetClosedOffset;
  const sortSheetTranslateY = isSortSheetOpen ? sortSheetOffset : sortSheetClosedOffset;
  const sortSheetProgress = isSortSheetOpen ? Math.min(1, Math.max(0, 1 - (sortSheetOffset / maxSortSheetDrag))) : 0;
  const citySwitcherClosedOffset = (citySwitcherHeight || 450) + 36;
  const maxCitySwitcherDrag = citySwitcherClosedOffset;
  const citySwitcherTranslateY = isCitySwitcherOpen ? citySwitcherOffset : citySwitcherClosedOffset;
  const citySwitcherProgress = isCitySwitcherOpen ? Math.min(1, Math.max(0, 1 - (citySwitcherOffset / maxCitySwitcherDrag))) : 0;

  const syncFavoriteCodes = (codes: string[]) => {
    const normalizedCodes = Array.from(new Set(codes.map((code) => String(code))));
    setFavoriteCodes(normalizedCodes);
    queryClient.setQueryData<FavoriteCodesResponse>(['favorites', token], { codes: normalizedCodes });
  };

  const addFavoriteMutation = useMutation({
    mutationFn: (code: string) => addFavorite(token, code),
    onMutate: async (code: string) => {
      await queryClient.cancelQueries({ queryKey: ['favorites', token] });
      const previousCodes = queryClient.getQueryData<FavoriteCodesResponse>(['favorites', token])?.codes ?? favoriteCodes;
      const nextCodes = previousCodes.includes(code) ? previousCodes : [...previousCodes, code];
      syncFavoriteCodes(nextCodes);
      return { previousCodes };
    },
    onError: (_error: Error, _code: string, context?: { previousCodes: string[] }) => {
      syncFavoriteCodes(context?.previousCodes ?? []);
    },
    onSuccess: (data: FavoriteCodesResponse) => {
      syncFavoriteCodes(data.codes);
    },
  });

  const removeFavoriteMutation = useMutation({
    mutationFn: (code: string) => removeFavorite(token, code),
    onMutate: async (code: string) => {
      await queryClient.cancelQueries({ queryKey: ['favorites', token] });
      const previousCodes = queryClient.getQueryData<FavoriteCodesResponse>(['favorites', token])?.codes ?? favoriteCodes;
      const nextCodes = previousCodes.filter((favoriteCode: string) => favoriteCode !== code);
      syncFavoriteCodes(nextCodes);
      return { previousCodes, code };
    },
    onError: (_error: Error, _code: string, context?: { previousCodes: string[]; code: string }) => {
      syncFavoriteCodes(context?.previousCodes ?? []);
      if (context?.code) {
        setExitingFavoriteCodes((current) => current.filter((favoriteCode) => favoriteCode !== context.code));
        setFavoriteExitGhosts((current) => current.filter((ghost) => ghost.code !== context.code));
      }
    },
    onSuccess: (data: FavoriteCodesResponse) => {
      syncFavoriteCodes(data.codes);
    },
  });

  const triggerFavoriteIconAnimation = (code: string, animation: 'jello' | 'shake') => {
    if (favoriteIconAnimationTimeoutsRef.current[code]) {
      window.clearTimeout(favoriteIconAnimationTimeoutsRef.current[code]);
    }

    setFavoriteIconAnimations((current) => ({ ...current, [code]: animation }));
    favoriteIconAnimationTimeoutsRef.current[code] = window.setTimeout(() => {
      setFavoriteIconAnimations((current) => {
        const next = { ...current };
        delete next[code];
        return next;
      });
      delete favoriteIconAnimationTimeoutsRef.current[code];
    }, animation === 'shake' ? FAVORITE_ICON_SHAKE_MS : FAVORITE_ICON_JELLO_MS);
  };

  const setCityMutation = useMutation({
    mutationFn: ({ cityName, slot }: { cityName: string; slot: number }) => setProfileCity(token, cityName, slot),
    onSuccess: (data) => {
      queryClient.setQueryData<ProfileResponse | undefined>(['profile', token], (current) => (
        current ? { ...current, client: data.client } : current
      ));
      queryClient.invalidateQueries({ queryKey: ['models', token] });
      queryClient.invalidateQueries({ queryKey: ['favorites', token] });
      queryClient.invalidateQueries({ queryKey: ['model-sheet', token] });
      closeCitySwitcher();
      closeSheet();
      setSectionTransition('static');
      setActiveSection('all');
    },
  });

  const setCityStatusMutation = useMutation({
    mutationFn: (cityStatus: number) => setProfileCityStatus(token, cityStatus),
    onSuccess: (data) => {
      queryClient.setQueryData<ProfileResponse | undefined>(['profile', token], (current) => (
        current ? { ...current, client: data.client } : current
      ));
      queryClient.invalidateQueries({ queryKey: ['models', token] });
      queryClient.invalidateQueries({ queryKey: ['favorites', token] });
      queryClient.invalidateQueries({ queryKey: ['model-sheet', token] });
      closeCitySwitcher();
      closeSheet();
      setSectionTransition('static');
      setActiveSection('all');
    },
  });

  const prepareBookingMutation = useMutation({
    mutationFn: (body: BookingPrepareRequest) => {
      if (!sheetModel) {
        throw new Error('Модель не выбрана');
      }

      return prepareModelBooking(token, sheetModel.code, body);
    },
    onSuccess: (data) => {
      setPreparedBooking(data);
      setBookingPayment(null);
    },
  });

  const resolveBookingPaymentMutation = useMutation({
    mutationFn: (paymentMethod: BookingPaymentMethodKey) => {
      if (!preparedBooking) {
        throw new Error('Заявка не подготовлена');
      }

      return resolveModelBookingPayment(token, preparedBooking.orderNumber, paymentMethod);
    },
    onSuccess: (data) => {
      setBookingPayment(data);
      setBookingStep('payment');
    },
  });

  const addBookingAddressMutation = useMutation({
    mutationFn: ({ title, address }: { title: string; address: string }) => addProfileAddress(token, title, address),
    onSuccess: (data) => {
      queryClient.setQueryData<ProfileResponse | undefined>(['profile', token], (current) => (
        current ? { ...current, addresses: data.addresses } : current
      ));
      setBookingAddressTitle('');
      setBookingAddressValue('');
      setBookingAddressMode('list');
      void profileQuery.refetch();
    },
  });

  const resetBookingFlow = () => {
    setIsBookingFlowOpen(false);
    setBookingStep('datetime');
    setBookingAddressMode('list');
    setBookingSelection(createEmptyBookingSelection());
    setBookingAddressTitle('');
    setBookingAddressValue('');
    setExpandedBookingSelect(null);
    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();
    addBookingAddressMutation.reset();
  };

  const handleStartBooking = () => {
    resetBookingFlow();
    setBookingSelection({
      selectedDate: bookingDateOptions[0]?.key ?? null,
      selectedTime: bookingTimes[0] ?? null,
      selectedPlace: null,
      selectedAddressId: null,
      selectedTariff: null,
      selectedAdditionalIds: [],
    });
    setExpandedBookingSelect(null);
    setIsBookingFlowOpen(true);
  };

  const handleBookingDateSelect = (dateKey: string) => {
    setBookingSelection((current) => ({
      ...current,
      selectedDate: dateKey,
      selectedPlace: null,
        selectedAddressId: null,
      selectedTariff: null,
      selectedAdditionalIds: [],
    }));
    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();
    setExpandedBookingSelect(null);
  };

  const handleBookingTimeSelect = (timeValue: string) => {
    setBookingSelection((current) => ({
      ...current,
      selectedTime: timeValue,
      selectedPlace: null,
        selectedAddressId: null,
      selectedTariff: null,
      selectedAdditionalIds: [],
    }));
    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();
    setExpandedBookingSelect(null);
  };

  const handleBookingDateTimeContinue = () => {
    if (!bookingSelection.selectedDate || !bookingSelection.selectedTime) {
      return;
    }

    setExpandedBookingSelect(null);
    setBookingStep('place');
  };

  const handleBookingPlaceSelect = (place: BookingPlace) => {
    setBookingSelection((current) => ({
      ...current,
      selectedPlace: place,
        selectedAddressId: null,
      selectedTariff: null,
      selectedAdditionalIds: [],
    }));
    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();

      setBookingAddressMode('list');
      setBookingAddressTitle('');
      setBookingAddressValue('');
      addBookingAddressMutation.reset();

      if (place === 'client' && isAddressSystemEnabled) {
        setBookingStep('address');
        return;
      }

      setBookingStep('tariff');
  };

    const handleBookingAddressSelect = (addressId: number) => {
      setBookingSelection((current) => ({
        ...current,
        selectedAddressId: addressId,
        selectedTariff: null,
        selectedAdditionalIds: [],
      }));
      setPreparedBooking(null);
      setBookingPayment(null);
      prepareBookingMutation.reset();
      resolveBookingPaymentMutation.reset();
      setBookingStep('tariff');
    };

    const handleBookingAddressSubmit = (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const title = bookingAddressTitle.trim();
      const address = bookingAddressValue.trim();
      if (!title || !address) {
        return;
      }

      addBookingAddressMutation.mutate({ title, address });
    };

  const handlePrepareBooking = (tariff: BookingTariffKey, additionalIds: number[]) => {
    if (!bookingSelection.selectedDate || !bookingSelection.selectedTime || !bookingSelection.selectedPlace) {
      return;
    }

    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();
    setBookingStep('payment-method');
    prepareBookingMutation.mutate({
      meetingDate: bookingSelection.selectedDate,
      meetingTime: bookingSelection.selectedTime,
      meetingPlace: bookingSelection.selectedPlace,
      tariff,
        addressId: bookingSelection.selectedPlace === 'client' ? bookingSelection.selectedAddressId : null,
      additionals: additionalIds,
    });
  };

  const handleBookingTariffSelect = (tariff: BookingTariffKey) => {
    setBookingSelection((current) => ({
      ...current,
      selectedTariff: tariff,
      selectedAdditionalIds: [],
    }));
    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();

    if (hasBookingAdditionals) {
      setBookingStep('additionals');
      return;
    }

    handlePrepareBooking(tariff, []);
  };

  const handleBookingAdditionalToggle = (additionalId: number) => {
    setBookingSelection((current) => {
      const isSelected = current.selectedAdditionalIds.includes(additionalId);
      return {
        ...current,
        selectedAdditionalIds: isSelected
          ? current.selectedAdditionalIds.filter((id) => id !== additionalId)
          : [...current.selectedAdditionalIds, additionalId],
      };
    });
    setPreparedBooking(null);
    setBookingPayment(null);
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();
  };

  const handleBookingAdditionalsContinue = () => {
    if (!bookingSelection.selectedTariff) {
      return;
    }

    handlePrepareBooking(bookingSelection.selectedTariff, bookingSelection.selectedAdditionalIds);
  };

  const handleBookingPaymentMethodSelect = (paymentMethod: BookingPaymentMethodKey) => {
    if (paymentMethod === 'cash') {
      setBookingPayment({ status: 'cash_unavailable', orderNumber: '', modelName: '', modelCode: '', amount: 0, currency: '', paymentMethod: 'cash' });
      setBookingStep('payment');
      return;
    }
    setBookingPayment(null);
    resolveBookingPaymentMutation.mutate(paymentMethod);
  };

  const handleBookingBack = () => {
    prepareBookingMutation.reset();
    resolveBookingPaymentMutation.reset();

    switch (bookingStep) {
      case 'datetime':
        closeSheet();
        return;
      case 'place':
        setBookingStep('datetime');
        setBookingSelection((current) => ({
          ...current,
          selectedPlace: null,
          selectedAddressId: null,
          selectedTariff: null,
          selectedAdditionalIds: [],
        }));
        setExpandedBookingSelect(null);
        return;
      case 'address':
        if (bookingAddressMode === 'create') {
          setBookingAddressMode('list');
          setBookingAddressTitle('');
          setBookingAddressValue('');
          addBookingAddressMutation.reset();
          return;
        }
        setBookingStep('place');
        setBookingSelection((current) => ({
          ...current,
          selectedAddressId: null,
          selectedTariff: null,
          selectedAdditionalIds: [],
        }));
        return;
      case 'tariff':
        setBookingStep(bookingSelection.selectedPlace === 'client' && isAddressSystemEnabled ? 'address' : 'place');
        setBookingSelection((current) => ({
          ...current,
          selectedTariff: null,
          selectedAdditionalIds: [],
        }));
        return;
      case 'additionals':
        setBookingStep('tariff');
        setBookingSelection((current) => ({
          ...current,
          selectedAdditionalIds: [],
        }));
        setPreparedBooking(null);
        setBookingPayment(null);
        return;
      case 'payment-method':
        setBookingStep(hasBookingAdditionals ? 'additionals' : 'tariff');
        setPreparedBooking(null);
        setBookingPayment(null);
        return;
      case 'payment':
        setBookingStep('payment-method');
        setBookingPayment(null);
        return;
      default:
        return;
    }
  };

  const handleSectionChange = (nextSection: ModelsSection) => {
    if (nextSection === activeSection) {
      return;
    }

    setSectionTransition(nextSection === 'favorites' ? 'slide-left' : 'slide-right');
    setActiveSection(nextSection);
  };

  const toggleFavorite = (code: string) => {
    if (favoriteCodes.includes(code)) {
      if (activeSection === 'favorites') {
        if (favoriteExitTimeoutsRef.current[code] || favoriteExitKickoffTimeoutsRef.current[code]) {
          return;
        }

        triggerFavoriteIconAnimation(code, 'shake');
        favoriteExitKickoffTimeoutsRef.current[code] = window.setTimeout(() => {
          const item = visibleItems.find((model) => model.code === code);
          const element = favoriteSlotRefs.current[code];
          if (item && element) {
            const rect = element.getBoundingClientRect();
            setFavoriteExitGhosts((current) => [
              ...current.filter((ghost) => ghost.code !== code),
              {
                code,
                item,
                rect: {
                  top: rect.top,
                  left: rect.left,
                  width: rect.width,
                  height: rect.height,
                },
              },
            ]);
          }
          setExitingFavoriteCodes((current) => (current.includes(code) ? current : [...current, code]));
          removeFavoriteMutation.mutate(code);
          favoriteExitTimeoutsRef.current[code] = window.setTimeout(() => {
            setExitingFavoriteCodes((current) => current.filter((favoriteCode) => favoriteCode !== code));
            setFavoriteExitGhosts((current) => current.filter((ghost) => ghost.code !== code));
            delete favoriteExitTimeoutsRef.current[code];
          }, FAVORITE_EXIT_TRANSITION_MS);
          delete favoriteExitKickoffTimeoutsRef.current[code];
        }, FAVORITE_ICON_SHAKE_MS);
        return;
      }

      triggerFavoriteIconAnimation(code, 'shake');
      removeFavoriteMutation.mutate(code);
      return;
    }

    triggerFavoriteIconAnimation(code, 'jello');
    addFavoriteMutation.mutate(code);
  };

  useEffect(() => {
    const sectionFromUrl = searchParams.get('section') === 'favorites' ? 'favorites' : 'all';
    if (sectionFromUrl !== activeSection) {
      setSectionTransition('static');
      setActiveSection(sectionFromUrl);
    }
  }, [searchParams]);

  useEffect(() => {
    const nextSearchParams = new URLSearchParams(searchParams);

    if (activeSection === 'favorites') {
      nextSearchParams.set('section', 'favorites');
    } else {
      nextSearchParams.delete('section');
    }

    if (nextSearchParams.toString() !== searchParams.toString()) {
      setSearchParams(nextSearchParams, { replace: true });
    }
  }, [activeSection, searchParams, setSearchParams]);

  useEffect(() => {
    if (!sheetModel && !isSortSheetMounted && !isCitySwitcherMounted) {
      return undefined;
    }

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.body.classList.add('models-sheet-open');

    return () => {
      document.body.style.overflow = originalOverflow;
      document.body.classList.remove('models-sheet-open');
    };
  }, [isCitySwitcherMounted, isSortSheetMounted, sheetModel]);

  useEffect(() => {
    if (!sheetModel) {
      return undefined;
    }

    const frameId = window.requestAnimationFrame(() => {
      setIsSheetOpen(true);
    });

    return () => {
      window.cancelAnimationFrame(frameId);
    };
  }, [sheetModel]);

  useLayoutEffect(() => {
    sheetInitialHeightRef.current = null;
  }, [bookingStep, isBookingFlowOpen]);

  useLayoutEffect(() => {
    if (!sheetModel) {
      setSheetContentHeight(null);
      return undefined;
    }

    const syncSheetMetrics = () => {
      const innerElement = sheetScrollInnerRef.current;
      const bookingElement = bookingBodyRef.current;
      const measuredElement = isBookingFlowOpen && bookingElement ? bookingElement : innerElement;

      if (!measuredElement) {
        return;
      }

      const maxContentHeight = Math.min(
        window.innerHeight * (bookingStep === 'payment' ? 0.92 : 0.82),
        bookingStep === 'payment' ? 920 : 820,
      );
      const measuredInnerHeight = isBookingFlowOpen && bookingElement
        ? (
          bookingStep === 'datetime' && expandedBookingSelect !== null
            ? Math.ceil(bookingElement.getBoundingClientRect().height)
            : bookingElement.scrollHeight || Math.ceil(bookingElement.getBoundingClientRect().height)
        )
        : (measuredElement.scrollHeight || Math.ceil(measuredElement.getBoundingClientRect().height));
      const bookingHeightPadding = bookingStep === 'payment'
        ? 40
        : bookingStep === 'datetime' && expandedBookingSelect !== null
          ? 4
          : 24;
      const nextMeasuredHeight = measuredInnerHeight + (isBookingFlowOpen ? bookingHeightPadding : 26);
      const nextContentHeight = Math.min(
        nextMeasuredHeight,
        maxContentHeight,
      );

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

    if (sheetScrollInnerRef.current) {
      resizeObserver.observe(sheetScrollInnerRef.current);
    }

      if (bookingBodyRef.current) {
      resizeObserver.observe(bookingBodyRef.current);
    }

    window.addEventListener('resize', syncSheetMetrics);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', syncSheetMetrics);
    };
    }, [
    sheetModel,
    isBookingFlowOpen,
    bookingStep,
    expandedBookingSelect,
    bookingSelection.selectedDate,
    bookingSelection.selectedTime,
    prepareBookingMutation.isPending,
    preparedBooking?.paymentMethods?.length,
    resolveBookingPaymentMutation.isPending,
    bookingPayment?.status,
  ]);

  useEffect(() => {
    if (!sheetModel) {
      return undefined;
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeSheet();
      }
    };

    window.addEventListener('keydown', handleEscape);

    return () => {
      window.removeEventListener('keydown', handleEscape);
    };
  }, [sheetModel]);

  useEffect(() => () => {
    if (favoriteLayoutFrameRef.current) {
      window.cancelAnimationFrame(favoriteLayoutFrameRef.current);
    }
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
    }
    if (sortSheetCloseTimeoutRef.current) {
      window.clearTimeout(sortSheetCloseTimeoutRef.current);
    }
    Object.values(favoriteExitTimeoutsRef.current).forEach((timeoutId) => {
      window.clearTimeout(timeoutId);
    });
    Object.values(favoriteIconAnimationTimeoutsRef.current).forEach((timeoutId) => {
      window.clearTimeout(timeoutId);
    });
    Object.values(favoriteExitKickoffTimeoutsRef.current).forEach((timeoutId) => {
      window.clearTimeout(timeoutId);
    });
    if (citySwitcherCloseTimeoutRef.current) {
      window.clearTimeout(citySwitcherCloseTimeoutRef.current);
    }
  }, []);

  useEffect(() => {
    if (!favoritesQuery.data) {
      return;
    }

    setFavoriteCodes(Array.from(new Set(favoritesQuery.data.codes.map((code: string) => String(code)))));
  }, [favoritesQuery.data]);

  useEffect(() => {
    if (!isCitySwitcherMounted) {
      return undefined;
    }

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeCitySwitcher();
      }
    };

    window.addEventListener('keydown', handleEscape);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isCitySwitcherMounted]);

  useEffect(() => {
    if (!isCitySwitcherMounted) {
      return undefined;
    }

    const syncCitySwitcherHeight = () => {
      setCitySwitcherHeight(citySwitcherSheetRef.current?.getBoundingClientRect().height ?? 0);
    };

    syncCitySwitcherHeight();
    window.addEventListener('resize', syncCitySwitcherHeight);

    return () => {
      window.removeEventListener('resize', syncCitySwitcherHeight);
    };
  }, [isCitySwitcherMounted, citySwitcherMode]);

  useEffect(() => {
    if (!isCitySwitcherMounted) {
      return undefined;
    }

    const frameId = window.requestAnimationFrame(() => {
      setIsCitySwitcherOpen(true);
    });

    return () => {
      window.cancelAnimationFrame(frameId);
    };
  }, [isCitySwitcherMounted]);

  useLayoutEffect(() => {
    if (activeSection !== 'favorites') {
      previousFavoriteSlotRectsRef.current = {};
      favoriteLayoutReadyRef.current = false;
      return;
    }

    const nextRects: Record<string, DOMRect> = {};

    visibleItems.forEach((item) => {
      const element = favoriteSlotRefs.current[item.code];

      if (!element) {
        return;
      }

      const nextRect = element.getBoundingClientRect();
      nextRects[item.code] = nextRect;
    });

    if (!favoriteLayoutReadyRef.current || !Object.keys(previousFavoriteSlotRectsRef.current).length) {
      previousFavoriteSlotRectsRef.current = nextRects;

      if (favoriteLayoutFrameRef.current) {
        window.cancelAnimationFrame(favoriteLayoutFrameRef.current);
      }

      favoriteLayoutFrameRef.current = window.requestAnimationFrame(() => {
        const stableRects: Record<string, DOMRect> = {};

        visibleItems.forEach((item) => {
          const element = favoriteSlotRefs.current[item.code];

          if (!element) {
            return;
          }

          stableRects[item.code] = element.getBoundingClientRect();
        });

        previousFavoriteSlotRectsRef.current = stableRects;
        favoriteLayoutReadyRef.current = true;
        favoriteLayoutFrameRef.current = null;
      });

      return () => {
        if (favoriteLayoutFrameRef.current) {
          window.cancelAnimationFrame(favoriteLayoutFrameRef.current);
          favoriteLayoutFrameRef.current = null;
        }
      };
    }

    visibleItems.forEach((item) => {
      const element = favoriteSlotRefs.current[item.code];

      if (!element) {
        return;
      }

      const nextRect = nextRects[item.code];
      const previousRect = previousFavoriteSlotRectsRef.current[item.code];

      if (!previousRect || !nextRect || exitingFavoriteCodes.includes(item.code)) {
        return;
      }

      const deltaY = previousRect.top - nextRect.top;

      if (Math.abs(deltaY) < 1) {
        return;
      }

      element.animate(
        [
          { transform: `translate(0, ${deltaY}px)` },
          { transform: 'translate(0, 0)' },
        ],
        {
          duration: FAVORITE_EXIT_TRANSITION_MS + 80,
          easing: 'cubic-bezier(0.18, 0.88, 0.24, 1)',
        },
      );
    });

    previousFavoriteSlotRectsRef.current = nextRects;
  }, [activeSection, exitingFavoriteCodes, visibleItems]);

  useEffect(() => {
    if (!isSortSheetMounted) {
      return undefined;
    }

    const frameId = window.requestAnimationFrame(() => {
      setIsSortSheetOpen(true);
    });

    return () => {
      window.cancelAnimationFrame(frameId);
    };
  }, [isSortSheetMounted]);

  useEffect(() => {
    if (!isSortSheetMounted) {
      return undefined;
    }

    const syncSortSheetHeight = () => {
      setSortSheetHeight(sortSheetRef.current?.getBoundingClientRect().height ?? 0);
    };

    syncSortSheetHeight();
    window.addEventListener('resize', syncSortSheetHeight);

    return () => {
      window.removeEventListener('resize', syncSortSheetHeight);
    };
  }, [isSortSheetMounted]);

  useEffect(() => {
    if (!isSortSheetMounted) {
      return undefined;
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeSortSheet();
      }
    };

    window.addEventListener('keydown', handleEscape);

    return () => {
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isSortSheetMounted]);

  const updateSheetOffset = (nextOffset: number) => {
    sheetOffsetRef.current = nextOffset;
    setSheetOffset(nextOffset);
  };

  const updateSortSheetOffset = (nextOffset: number) => {
    sortSheetOffsetRef.current = nextOffset;
    setSortSheetOffset(nextOffset);
  };

  const updateCitySwitcherOffset = (nextOffset: number) => {
    citySwitcherOffsetRef.current = nextOffset;
    setCitySwitcherOffset(nextOffset);
  };

  const handlePhotoTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    photoTouchStartXRef.current = event.touches[0].clientX;
    photoTouchStartYRef.current = event.touches[0].clientY;
  };

  const handlePhotoTouchEnd = (event: React.TouchEvent<HTMLDivElement>) => {
    if (sheetPhotos.length <= 1) return;
    const deltaX = event.changedTouches[0].clientX - photoTouchStartXRef.current;
    const deltaY = event.changedTouches[0].clientY - photoTouchStartYRef.current;

    if (Math.abs(deltaX) > 36 && Math.abs(deltaX) > Math.abs(deltaY) * 1.1) {
      if (deltaX > 0) {
        setActivePhotoIndex((current) => (current - 1 + sheetPhotos.length) % sheetPhotos.length);
      } else {
        setActivePhotoIndex((current) => (current + 1) % sheetPhotos.length);
      }
    }
  };

  const handleSheetScrollTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    sheetScrollTouchStartYRef.current = event.touches[0].clientY;
  };

  const handleSheetScrollTouchMove = (event: React.TouchEvent<HTMLDivElement>) => {
    const el = event.currentTarget;
    const touchY = event.touches[0].clientY;
    const isPullingDown = touchY > sheetScrollTouchStartYRef.current;
    const isPullingUp = touchY < sheetScrollTouchStartYRef.current;

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

  const openSheet = (model: ModelSummary) => {
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }

    void prefetchModelDetails(model.code);
    if (token) {
      void markModelOpened(token, model.code).catch(() => undefined);
    }
    resetBookingFlow();
    setActivePhotoIndex(0);
    updateSheetOffset(0);
    setIsSheetDragging(false);
    setIsSheetOpen(false);
    setSheetModel(model);
  };

  const handleStartBookingForModel = (model: ModelSummary) => {
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }

    void prefetchModelDetails(model.code);
    setActivePhotoIndex(0);
    updateSheetOffset(0);
    setIsSheetDragging(false);
    setIsSheetOpen(false);
    setSheetModel(model);
    setBookingSelection({
      selectedDate: bookingDateOptions[0]?.key ?? null,
      selectedTime: bookingTimes[0] ?? null,
      selectedPlace: null,
        selectedAddressId: null,
      selectedTariff: null,
      selectedAdditionalIds: [],
    });
    setExpandedBookingSelect(null);
    setBookingStep('datetime');
    setIsBookingFlowOpen(true);
  };

  const finalizeSheetClose = () => {
    resetBookingFlow();
    setSheetModel(null);
    setSheetContentHeight(null);
    sheetInitialHeightRef.current = null;
    updateSheetOffset(0);
    closeTimeoutRef.current = null;
  };

  const closeSheet = () => {
    setIsSheetDragging(false);
    setIsSheetOpen(false);

    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
    }

    closeTimeoutRef.current = window.setTimeout(finalizeSheetClose, SHEET_TRANSITION_MS);
  };

  const openSortSheet = () => {
    if (sortSheetCloseTimeoutRef.current) {
      window.clearTimeout(sortSheetCloseTimeoutRef.current);
      sortSheetCloseTimeoutRef.current = null;
    }

    setPendingSort(appliedSort);
    updateSortSheetOffset(0);
    setIsSortSheetDragging(false);
    setIsSortSheetOpen(false);
    setIsSortSheetMounted(true);
  };

  const closeSortSheet = () => {
    setIsSortSheetDragging(false);
    setIsSortSheetOpen(false);

    if (sortSheetCloseTimeoutRef.current) {
      window.clearTimeout(sortSheetCloseTimeoutRef.current);
    }

    sortSheetCloseTimeoutRef.current = window.setTimeout(() => {
      setIsSortSheetMounted(false);
      updateSortSheetOffset(0);
      sortSheetCloseTimeoutRef.current = null;
    }, SORT_SHEET_TRANSITION_MS);
  };

  const applySortSheet = () => {
    setAppliedSort(pendingSort);
    closeSortSheet();
  };

  const handleCitySubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedCity = cityValue.trim();
    if (!normalizedCity) {
      return;
    }

    const targetSlot = hasActiveCity && !secondCity ? 2 : activeCitySlot;
    setCityMutation.mutate({ cityName: normalizedCity, slot: targetSlot });
  };

  const toggleCitySwitcher = () => {
    if (isCitySwitcherMounted) {
      closeCitySwitcher();
      return;
    }

    if (citySwitcherCloseTimeoutRef.current) {
      window.clearTimeout(citySwitcherCloseTimeoutRef.current);
      citySwitcherCloseTimeoutRef.current = null;
    }

    updateCitySwitcherOffset(0);
    setIsCitySwitcherDragging(false);
    setIsCitySwitcherOpen(false);
    setIsCitySwitcherMounted(true);
  };

  const openAddCityMode = () => {
    setCitySwitcherMode('add');
    setCityValue('');
    setCityMutation.reset();
  };

  const returnToCityList = () => {
    setCitySwitcherMode('list');
    setCityValue('');
    setCityMutation.reset();
  };

  const handleCitySlotSelect = (slot: number) => {
    const slotCity = slot === 2 ? secondCity : firstCity;

    if (!slotCity || slot === activeCitySlot || setCityStatusMutation.isPending) {
      return;
    }

    setCityStatusMutation.mutate(slot);
  };

  const closeCitySwitcher = () => {
    setIsCitySwitcherDragging(false);
    setIsCitySwitcherOpen(false);

    if (citySwitcherCloseTimeoutRef.current) {
      window.clearTimeout(citySwitcherCloseTimeoutRef.current);
    }

    citySwitcherCloseTimeoutRef.current = window.setTimeout(() => {
      setIsCitySwitcherMounted(false);
      setCitySwitcherMode('list');
      setCityMutation.reset();
      setCityValue('');
      setCitySwitcherContentHeight(null);
      updateCitySwitcherOffset(0);
      citySwitcherCloseTimeoutRef.current = null;
    }, CITY_SWITCHER_TRANSITION_MS);
  };

  const handleCitySwitcherDragStart = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!isCitySwitcherMounted || !isCitySwitcherOpen) {
      return;
    }

    citySwitcherDragPointerIdRef.current = event.pointerId;
    citySwitcherDragStartYRef.current = event.clientY;
    citySwitcherDragStartOffsetRef.current = citySwitcherOffsetRef.current;
    setIsCitySwitcherDragging(true);
    event.currentTarget.setPointerCapture(event.pointerId);

    citySwitcherHasScrollRef.current = false;
    citySwitcherDragStartHeightRef.current = citySwitcherContentHeight || citySwitcherSheetRef.current?.getBoundingClientRect().height || 400;
  };

  const handleCitySwitcherDragMove = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!isCitySwitcherDragging || citySwitcherDragPointerIdRef.current !== event.pointerId) {
      return;
    }

    const delta = event.clientY - citySwitcherDragStartYRef.current;
    if (delta > 0) {
      const rawOffset = citySwitcherDragStartOffsetRef.current + delta;
      updateCitySwitcherOffset(rawOffset);
    } else {
      updateCitySwitcherOffset(0);
    }
  };

  const handleCitySwitcherDragEnd = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (citySwitcherDragPointerIdRef.current !== event.pointerId) {
      return;
    }

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    citySwitcherDragPointerIdRef.current = null;
    setIsCitySwitcherDragging(false);

    const nextOffset = citySwitcherOffsetRef.current;
    const shouldClose = nextOffset > Math.min(160, (citySwitcherHeight || 380) * 0.32);

    if (shouldClose) {
      closeCitySwitcher();
      return;
    }

    updateCitySwitcherOffset(0);
  };

  const getSheetModelValue = <K extends keyof ModelSummary>(key: K): ModelSummary[K] | undefined => {
    if (detailModel && key in detailModel) {
      return detailModel[key];
    }

    return sheetModel?.[key];
  };

  const handleSheetDragStart = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!sheetModel || !isSheetOpen) {
      return;
    }

    dragPointerIdRef.current = event.pointerId;
    dragStartYRef.current = event.clientY;
    dragStartOffsetRef.current = sheetOffsetRef.current;
    setIsSheetDragging(true);
    event.currentTarget.setPointerCapture(event.pointerId);

    const scrollEl = sheetScrollRef.current;
    const hasScroll = Boolean(scrollEl && scrollEl.scrollHeight > scrollEl.clientHeight + 1);
    sheetHasScrollRef.current = hasScroll;
    sheetDragStartHeightRef.current = sheetContentHeight || sheetRef.current?.getBoundingClientRect().height || 450;
  };

  const handleSheetDragMove = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!isSheetDragging || dragPointerIdRef.current !== event.pointerId) {
      return;
    }

    const delta = event.clientY - dragStartYRef.current;
    const initialHeight = sheetInitialHeightRef.current ?? 450;
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
        const maxNeededHeight = Math.min(
          Math.max(300, window.innerHeight - 44),
          (sheetScrollRef.current?.scrollHeight ?? 0) + 26,
        );
        const nextHeight = Math.min(maxNeededHeight, sheetDragStartHeightRef.current + stretch);
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

    const initialHeight = sheetInitialHeightRef.current ?? 450;
    const wasExpanded = sheetDragStartHeightRef.current > initialHeight + 20;
    const delta = event.clientY - dragStartYRef.current;

    if (sheetOffsetRef.current > Math.min(180, (sheetHeight || 400) * 0.35)) {
      closeSheet();
      return;
    }

    updateSheetOffset(0);

    if (wasExpanded) {
      if (delta > 20) {
        setSheetContentHeight(initialHeight);
      } else if (delta < -30) {
        const maxNeededHeight = Math.min(
          Math.max(300, window.innerHeight - 44),
          (sheetScrollRef.current?.scrollHeight ?? 0) + 26,
        );
        setSheetContentHeight(maxNeededHeight);
      } else {
        const maxNeededHeight = Math.min(
          Math.max(300, window.innerHeight - 44),
          (sheetScrollRef.current?.scrollHeight ?? 0) + 26,
        );
        setSheetContentHeight(maxNeededHeight);
      }
    } else {
      if (delta < -50 && sheetHasScrollRef.current) {
        const maxNeededHeight = Math.min(
          Math.max(300, window.innerHeight - 44),
          (sheetScrollRef.current?.scrollHeight ?? 0) + 26,
        );
        setSheetContentHeight(maxNeededHeight);
      }
    }
  };

  const handleSortSheetDragStart = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!isSortSheetOpen) {
      return;
    }

    sortDragPointerIdRef.current = event.pointerId;
    sortDragStartYRef.current = event.clientY;
    sortDragStartOffsetRef.current = sortSheetOffsetRef.current;
    setIsSortSheetDragging(true);
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handleSortSheetDragMove = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (!isSortSheetDragging || sortDragPointerIdRef.current !== event.pointerId) {
      return;
    }

    const delta = event.clientY - sortDragStartYRef.current;
    const rawOffset = sortDragStartOffsetRef.current + delta;
    let nextOffset: number;

    if (rawOffset < 0) {
      nextOffset = 0;
    } else {
      nextOffset = rawOffset;
    }

    updateSortSheetOffset(nextOffset);
  };

  const handleSortSheetDragEnd = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (sortDragPointerIdRef.current !== event.pointerId) {
      return;
    }

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    sortDragPointerIdRef.current = null;
    setIsSortSheetDragging(false);

    if (sortSheetOffsetRef.current > Math.min(160, (sortSheetHeight || 300) * 0.32)) {
      closeSortSheet();
      return;
    }

    updateSortSheetOffset(0);
  };

  return (
    <section className="models-page__stack">
      {isProfileGateLoading ? (
        <div className="models-city-gate">
          <div className="models-city-gate__shell glass-block-soft glass-accent-blue">
            {modelsPageContent.cityGateLoadingLabel}
          </div>
        </div>
      ) : !hasActiveCity ? (
        <div className="models-city-gate">
          <form className="models-city-gate__panel" onSubmit={handleCitySubmit}>
            <h2 className="models-city-gate__title">{modelsPageContent.cityGateTitle}</h2>
            <p className="models-city-gate__description">{modelsPageContent.cityGateDescription}</p>

            <label className="models-city-gate__input">
              <SearchIcon />
              <input
                className="models-city-gate__input-field"
                type="text"
                inputMode="text"
                autoComplete="address-level2"
                placeholder={modelsPageContent.cityGatePlaceholder}
                value={cityValue}
                onChange={(event) => setCityValue(event.target.value)}
                disabled={setCityMutation.isPending}
              />
            </label>

            <button
              type="submit"
              className="models-sheet__action"
              disabled={!cityValue.trim() || setCityMutation.isPending}
            >
              {setCityMutation.isPending ? modelsPageContent.cityGateLoadingLabel : modelsPageContent.cityGateSubmitLabel}
            </button>

            {setCityMutation.error ? (
              <p className="models-city-gate__error">
                {getCityGateErrorMessage(
                  setCityMutation.error,
                  modelsPageContent.cityGateNotFoundLabel,
                  modelsPageContent.cityGateErrorFallback,
                )}
              </p>
            ) : null}
          </form>
        </div>
      ) : (
        <>
          <HeroCarousel />

          <div className="models-sections" role="tablist" aria-label={modelsPageContent.allModelsLabel}>
            <button
              type="button"
              role="tab"
              aria-selected={activeSection === 'all'}
              className={`models-sections__button${activeSection === 'all' ? ' models-sections__button--active' : ''}`}
              onClick={() => handleSectionChange('all')}
            >
              {modelsPageContent.allModelsLabel}
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeSection === 'favorites'}
              className={`models-sections__button${activeSection === 'favorites' ? ' models-sections__button--active' : ''}`}
              onClick={() => handleSectionChange('favorites')}
            >
              {modelsPageContent.favoriteModelsLabel}
            </button>
          </div>

          <div key={activeSection} className={`models-section-panel models-section-panel--${sectionTransition}`}>
            {activeSection === 'all' ? (
              <div className="models-page__controls">
                <div className="models-search-row">
                  <label className="models-search">
                    <SearchIcon />
                    <input
                      className="models-search__input"
                      type="text"
                      inputMode="search"
                      placeholder={modelsPageContent.quickSearchPlaceholder}
                      value={searchValue}
                      onChange={(event) => setSearchValue(event.target.value)}
                    />
                  </label>

                  <div className="models-city-switcher">
                    <button
                      type="button"
                      className="models-city-chip"
                      aria-label={modelsPageContent.citySwitcherToggleLabel}
                      aria-expanded={isCitySwitcherMounted}
                      onClick={toggleCitySwitcher}
                    >
                      <span className="models-city-chip__value">{activeCity}</span>
                    </button>
                  </div>
                </div>

                <div className="models-toolbar" aria-label={modelsPageContent.quickSearchPlaceholder}>
                  <button
                    type="button"
                    className="models-toolbar__button"
                    aria-label={modelsPageContent.filterButtonLabel}
                    aria-expanded={isSortSheetMounted}
                    onClick={openSortSheet}
                  >
                    <FilterIcon />
                  </button>

                  <button
                    type="button"
                    className="models-toolbar__button"
                    aria-label={modelsPageContent.sortButtonLabel}
                    aria-expanded={isSortSheetMounted}
                    onClick={openSortSheet}
                  >
                    <SortIcon />
                  </button>
                </div>
              </div>
            ) : null}

            {activeSection === 'favorites' && !visibleItems.length && !query.isLoading && !favoritesQuery.isLoading ? (
              <div className="models-empty-panel">
                <div className="models-empty-state models-empty-state--favorites">
                  <EmptyFavoritesIcon />
                  <p className="models-empty-state__text">{modelsPageContent.emptyFavoritesLabel}</p>
                </div>
              </div>
            ) : activeSection === 'all' && !visibleItems.length && !query.isLoading ? (
              <div className="models-empty-panel">
                <div className="models-empty-state models-empty-state--models">
                  <EmptyModelsIcon />
                  <p className="models-empty-state__text">{modelsPageContent.emptyModelsLabel}</p>
                </div>
              </div>
            ) : (
            <div className={`models-grid grid${activeSection === 'favorites' ? ' models-grid--favorites' : ''}`}>
              {visibleItems.map((item) => (
                <article
                  key={item.code}
                  ref={(element) => {
                    favoriteSlotRefs.current[item.code] = element;
                  }}
                  className={`card${exitingFavoriteCodes.includes(item.code) ? ' model-card--favorite-exit' : ''}`}
                >
                  <div className="photo-wrap" onClick={() => openSheet(item)}>
                    {item.previewPhotoUrl ? (
                      <img src={item.previewPhotoUrl} alt={item.name} className="photo" />
                    ) : (
                      <div className="model-card__image-placeholder">
                        <Sparkles size={18} />
                      </div>
                    )}
                    {item.flags.verification || item.flags.document ? (
                      <div className="model-card__badges">
                        {item.flags.document ? (
                          <div className="model-card__badge model-card__badge--health">
                            <HealthBadgeIcon />
                            <span>{modelsPageContent.cardHealthLabel}</span>
                          </div>
                        ) : null}
                        {item.flags.verification ? (
                          <div className="model-card__badge model-card__badge--check">
                            <CheckBadgeIcon />
                            <span>{modelsPageContent.cardVerificationLabel}</span>
                          </div>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                  <div className="card-info" onClick={() => openSheet(item)}>
                    <h2>{item.name}</h2>
                    <p>
                      {item.age} лет • {item.height} см • {item.tits} size
                    </p>
                  </div>
                  <div className="actions">
                    <button
                      type="button"
                      className="order"
                      onClick={() => handleStartBookingForModel(item)}
                    >
                      {modelsPageContent.cardAction}
                    </button>
                    <button
                      className={`basket${favoriteCodes.includes(item.code) ? ' basket--active' : ''}`}
                      type="button"
                      aria-label={favoriteCodes.includes(item.code) ? modelsPageContent.favoriteRemoveLabel : modelsPageContent.favoriteAddLabel}
                      aria-pressed={favoriteCodes.includes(item.code)}
                      onClick={() => toggleFavorite(item.code)}
                    >
                      {favoriteCodes.includes(item.code) ? (
                        <MaskedIcon
                          src={heartIcon}
                          className={`model-card__favorite-icon model-card__favorite-icon--active${favoriteIconAnimations[item.code] ? ` model-card__favorite-icon--${favoriteIconAnimations[item.code]}` : ''}`}
                        />
                      ) : (
                        <MaskedIcon
                          src={heartCrackIcon}
                          className={`model-card__favorite-icon model-card__favorite-icon--inactive${favoriteIconAnimations[item.code] ? ` model-card__favorite-icon--${favoriteIconAnimations[item.code]}` : ''}`}
                        />
                      )}
                    </button>
                  </div>
                </article>
              ))}
            </div>
            )}
          </div>
        </>
      )}
      {isCitySwitcherMounted ? createPortal(
        <>
          <button
            type="button"
            className="models-sheet-backdrop"
            aria-label={modelsPageContent.citySwitcherCloseLabel}
            onClick={closeCitySwitcher}
            style={{
              opacity: citySwitcherProgress,
              background: `rgba(9, 10, 14, ${0.1 + (citySwitcherProgress * 0.16)})`,
              backdropFilter: `blur(${citySwitcherProgress * 16}px)`,
              WebkitBackdropFilter: `blur(${citySwitcherProgress * 16}px)`,
              transition: isCitySwitcherDragging
                ? 'none'
                : `opacity ${CITY_SWITCHER_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), background ${CITY_SWITCHER_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), backdrop-filter ${CITY_SWITCHER_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), -webkit-backdrop-filter ${CITY_SWITCHER_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          />
          <section
            ref={citySwitcherSheetRef}
            className="models-sheet models-city-switcher-sheet"
            aria-label={modelsPageContent.citySwitcherMenuTitle}
            style={{
              transform: `translateY(${citySwitcherTranslateY}px)`,
              transition: isCitySwitcherDragging ? 'none' : `transform ${CITY_SWITCHER_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          >
            <button
              type="button"
              className="models-sheet__drag"
              aria-label={modelsPageContent.citySwitcherCloseLabel}
              onPointerDown={handleCitySwitcherDragStart}
              onPointerMove={handleCitySwitcherDragMove}
              onPointerUp={handleCitySwitcherDragEnd}
              onPointerCancel={handleCitySwitcherDragEnd}
            />
            <div className="models-sheet__content" style={citySwitcherContentHeight ? { height: `${citySwitcherContentHeight}px` } : undefined}>
              <div
                className="models-city-switcher-sheet__body"
                onTouchStart={handleSheetScrollTouchStart}
                onTouchMove={handleSheetScrollTouchMove}
              >
                <div className="models-city-switcher-sheet__header">
                  {citySwitcherMode === 'add' ? (
                    <button
                      type="button"
                      className="models-booking__back-btn"
                      onClick={returnToCityList}
                      aria-label={modelsPageContent.citySwitcherBackLabel}
                    >
                      <ChevronLeft size={15} />
                      <span>{modelsPageContent.citySwitcherBackLabel}</span>
                    </button>
                  ) : null}
                  <p className="models-city-switcher__title">
                    {citySwitcherMode === 'add' ? modelsPageContent.citySwitcherAddTitle : modelsPageContent.citySwitcherMenuTitle}
                  </p>
                  {citySwitcherMode === 'list' ? (
                    <p className="models-city-switcher__subtitle">
                      {modelsPageContent.citySwitcherSelectedPrefix} {activeCity}
                    </p>
                  ) : null}
                </div>

                {citySwitcherMode === 'add' ? (
                  <form className="models-city-switcher__form" onSubmit={handleCitySubmit}>
                    <label className="models-city-switcher__input">
                      <SearchIcon />
                      <input
                        className="models-city-switcher__input-field"
                        type="text"
                        inputMode="text"
                        autoComplete="address-level2"
                        placeholder={modelsPageContent.cityGatePlaceholder}
                        value={cityValue}
                        onChange={(event) => setCityValue(event.target.value)}
                        disabled={setCityMutation.isPending}
                      />
                    </label>

                    <button
                      type="submit"
                      className="models-city-switcher__action"
                      disabled={!cityValue.trim() || setCityMutation.isPending}
                    >
                      {setCityMutation.isPending ? modelsPageContent.cityGateLoadingLabel : modelsPageContent.cityGateSubmitLabel}
                    </button>

                    {setCityMutation.error ? (
                      <p className="models-city-switcher__error">
                        {getCityGateErrorMessage(
                          setCityMutation.error,
                          modelsPageContent.cityGateNotFoundLabel,
                          modelsPageContent.cityGateErrorFallback,
                        )}
                      </p>
                    ) : null}
                  </form>
                ) : (
                  <div className="models-city-switcher__menu">
                    {citySlots.map(({ slot, city }) => {
                      if (!city) {
                        return slot === 2 ? (
                          <button
                            key={`city-slot-${slot}`}
                            type="button"
                            className="models-city-switcher__item models-city-switcher__item--add"
                            onClick={openAddCityMode}
                          >
                            <Plus size={18} />
                            <span>{modelsPageContent.citySwitcherAddButtonLabel}</span>
                          </button>
                        ) : null;
                      }

                      const isActiveSlot = slot === activeCitySlot;

                      if (isActiveSlot) {
                        return (
                          <div
                            key={`city-slot-${slot}`}
                            className="models-city-switcher__item models-city-switcher__item--current"
                          >
                            <span>
                              <svg viewBox="0 0 384 512" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" className="models-city-switcher__current-icon">
                                <path d="M0 188.6C0 84.4 86 0 192 0S384 84.4 384 188.6c0 119.3-120.2 262.3-170.4 316.8-11.8 12.8-31.5 12.8-43.3 0-50.2-54.5-170.4-197.5-170.4-316.8zM192 256a64 64 0 1 0 0-128 64 64 0 1 0 0 128z" fill="currentColor"/>
                              </svg>
                              {city}
                            </span>
                          </div>
                        );
                      }

                      return (
                        <button
                          key={`city-slot-${slot}`}
                          type="button"
                          className="models-city-switcher__item"
                          onClick={() => handleCitySlotSelect(slot)}
                          disabled={setCityStatusMutation.isPending}
                        >
                          <span>{city}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </section>
        </>,
        document.body,
      ) : null}
      {sheetModel ? createPortal(
        <>
          <button
            type="button"
            className="models-sheet-backdrop"
            aria-label={modelsPageContent.sheetCloseLabel}
            onClick={closeSheet}
            style={{
              opacity: sheetProgress,
              background: `rgba(9, 10, 14, ${0.1 + (sheetProgress * 0.16)})`,
              backdropFilter: `blur(${sheetProgress * 16}px)`,
              WebkitBackdropFilter: `blur(${sheetProgress * 16}px)`,
              transition: isSheetDragging
                ? 'none'
                : `opacity ${SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), background ${SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), backdrop-filter ${SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), -webkit-backdrop-filter ${SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          />
          <section
            ref={sheetRef}
            className="models-sheet"
            aria-label={sheetModel.name}
            style={{
              transform: `translateY(${sheetTranslateY}px)`,
              transition: isSheetDragging ? 'none' : `transform ${SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          >
            <button
              type="button"
              className="models-sheet__drag"
              aria-label={modelsPageContent.sheetCloseLabel}
              onPointerDown={handleSheetDragStart}
              onPointerMove={handleSheetDragMove}
              onPointerUp={handleSheetDragEnd}
              onPointerCancel={handleSheetDragEnd}
            />
            <div
              ref={sheetContentRef}
              className={`models-sheet__content${isBookingFlowOpen ? ' models-sheet__content--booking' : ''}${bookingStep === 'payment' ? ' models-sheet__content--payment' : ''}`}
              style={{
                ...(sheetContentHeight ? { height: `${sheetContentHeight}px` } : {}),
                transition: isSheetDragging ? 'none' : `height ${SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
              }}
            >
              <div className="models-sheet__viewport">
                <div
                  ref={sheetScrollRef}
                  className="models-sheet__scroll"
                  onTouchStart={handleSheetScrollTouchStart}
                  onTouchMove={handleSheetScrollTouchMove}
                >
                  <div ref={sheetScrollInnerRef} className="models-sheet__scroll-inner">
                    {isBookingFlowOpen ? (
                      <div
                        ref={bookingBodyRef}
                        className={`models-sheet__body models-booking${bookingStep === 'payment' ? ' models-booking--payment' : ''}${bookingStep === 'additionals' ? ' models-booking--additionals' : ''}`}
                      >
                        <div className="models-booking__header">
                          <button
                            type="button"
                            className="models-booking__back-btn"
                            aria-label={modelsPageContent.bookingBackLabel || 'Назад'}
                            onClick={handleBookingBack}
                          >
                            <ChevronLeft size={15} />
                            <span>{modelsPageContent.bookingBackLabel || 'Назад'}</span>
                          </button>
                          <h2 className="models-booking__title">
                            {{
                              datetime: modelsPageContent.bookingDateTimeTitle,
                              place: modelsPageContent.bookingPlaceTitle,
                                address: bookingAddressMode === 'create'
                                  ? modelsPageContent.bookingAddressCreateTitle
                                  : modelsPageContent.bookingAddressTitle,
                              tariff: modelsPageContent.bookingTariffTitle,
                              additionals: modelsPageContent.bookingAdditionalsTitle,
                              'payment-method': modelsPageContent.bookingPaymentMethodTitle,
                              payment: modelsPageContent.bookingPaymentTitle,
                            }[bookingStep]}
                          </h2>
                        </div>

                        {bookingStep !== 'datetime' && bookingSummaryItems.length ? (
                          <div className="models-booking__summary">
                            {bookingSummaryItems.map((item) => (
                              <div key={item.label} className="models-booking__summary-row">
                                <span className="models-booking__summary-label">{item.label}</span>
                                <span className="models-booking__summary-value">{item.value}</span>
                              </div>
                            ))}
                          </div>
                        ) : null}

                        {bookingStep === 'datetime' ? (
                          <>
                            <div className="models-booking__selectors">
                              <section className={`models-booking__select${expandedBookingSelect === 'date' ? ' models-booking__select--open' : ''}`}>
                                <button
                                  type="button"
                                  className="models-booking__select-trigger"
                                  onClick={() => setExpandedBookingSelect((current) => (current === 'date' ? null : 'date'))}
                                >
                                  <span className="models-booking__select-copy">
                                    <span className="models-booking__select-label">{modelsPageContent.bookingDateWheelTitle}</span>
                                    <span className="models-booking__select-value">{selectedBookingDateOption?.label ?? '—'}</span>
                                  </span>
                                  <ChevronDown className={`models-booking__select-icon${expandedBookingSelect === 'date' ? ' models-booking__select-icon--open' : ''}`} size={18} />
                                </button>

                                {expandedBookingSelect === 'date' ? (
                                  <div className="models-booking__select-menu">
                                    {bookingDateOptions.map((item) => (
                                      <button
                                        key={item.key}
                                        type="button"
                                        className={`models-booking__select-option${bookingSelection.selectedDate === item.key ? ' models-booking__select-option--active' : ''}`}
                                        onClick={() => handleBookingDateSelect(item.key)}
                                      >
                                        {item.label}
                                      </button>
                                    ))}
                                  </div>
                                ) : null}
                              </section>

                              <section className={`models-booking__select${expandedBookingSelect === 'time' ? ' models-booking__select--open' : ''}`}>
                                <button
                                  type="button"
                                  className="models-booking__select-trigger"
                                  onClick={() => setExpandedBookingSelect((current) => (current === 'time' ? null : 'time'))}
                                >
                                  <span className="models-booking__select-copy">
                                    <span className="models-booking__select-label">{modelsPageContent.bookingTimeWheelTitle}</span>
                                    <span className="models-booking__select-value">{bookingSelection.selectedTime ?? '—'}</span>
                                  </span>
                                  <ChevronDown className={`models-booking__select-icon${expandedBookingSelect === 'time' ? ' models-booking__select-icon--open' : ''}`} size={18} />
                                </button>

                                {expandedBookingSelect === 'time' ? (
                                  <div className="models-booking__select-menu">
                                    {bookingTimes.map((item) => (
                                      <button
                                        key={item}
                                        type="button"
                                        className={`models-booking__select-option${bookingSelection.selectedTime === item ? ' models-booking__select-option--active' : ''}`}
                                        onClick={() => handleBookingTimeSelect(item)}
                                      >
                                        {item}
                                      </button>
                                    ))}
                                  </div>
                                ) : null}
                              </section>
                            </div>

                            <button
                              type="button"
                              className="models-booking__cta"
                              onClick={handleBookingDateTimeContinue}
                              disabled={!bookingSelection.selectedDate || !bookingSelection.selectedTime}
                            >
                              {modelsPageContent.bookingContinueLabel}
                            </button>
                          </>
                        ) : null}

                        {bookingStep === 'place' ? (
                          <div className="models-booking__grid">
                            {(['model', 'client'] as const).map((place) => (
                              <button
                                key={place}
                                type="button"
                                className="models-booking__option"
                                onClick={() => handleBookingPlaceSelect(place)}
                              >
                                <span className="models-booking__option-label">{bookingPlaceLabels[place]}</span>
                              </button>
                            ))}
                          </div>
                        ) : null}

                        {bookingStep === 'address' ? (
                          bookingAddressMode === 'create' ? (
                            <form className="profile-page__promo-form" onSubmit={handleBookingAddressSubmit}>
                              <label className="profile-page__promo-input">
                                <input
                                  className="profile-page__promo-input-field"
                                  type="text"
                                  value={bookingAddressTitle}
                                  onChange={(event) => setBookingAddressTitle(event.target.value)}
                                  placeholder={modelsPageContent.bookingAddressTitlePlaceholder}
                                  disabled={addBookingAddressMutation.isPending}
                                />
                              </label>

                              <label className="profile-page__promo-input">
                                <input
                                  className="profile-page__promo-input-field"
                                  type="text"
                                  value={bookingAddressValue}
                                  onChange={(event) => setBookingAddressValue(event.target.value)}
                                  placeholder={modelsPageContent.bookingAddressValuePlaceholder}
                                  disabled={addBookingAddressMutation.isPending}
                                  autoComplete="street-address"
                                />
                              </label>

                              <button
                                type="submit"
                                className="profile-page__sheet-action"
                                disabled={!bookingAddressTitle.trim() || !bookingAddressValue.trim() || addBookingAddressMutation.isPending}
                              >
                                {addBookingAddressMutation.isPending ? modelsPageContent.bookingPaymentLoadingLabel : modelsPageContent.bookingAddressConfirmLabel}
                              </button>

                              {addBookingAddressMutation.error ? (
                                <p className="models-booking__status models-booking__status--error">{addBookingAddressMutation.error.message}</p>
                              ) : null}
                            </form>
                          ) : (
                            <>
                              {profileAddresses.length ? (
                                <div className="models-booking__grid models-booking__grid--stack">
                                  {profileAddresses.map((address) => (
                                    <button
                                      key={address.id}
                                      type="button"
                                      className={`models-booking__option models-booking__option--row${bookingSelection.selectedAddressId === address.id ? ' models-booking__option--selected' : ''}`}
                                      onClick={() => handleBookingAddressSelect(address.id)}
                                    >
                                      <span className="models-booking__option-main">
                                        <span className="models-booking__option-label">{address.title}</span>
                                        <span className="models-booking__option-meta">{address.address}</span>
                                      </span>
                                    </button>
                                  ))}
                                </div>
                              ) : (
                                <p className="models-booking__status">{modelsPageContent.bookingAddressEmptyLabel}</p>
                              )}

                              <button
                                type="button"
                                className="profile-page__sheet-action"
                                onClick={() => {
                                  addBookingAddressMutation.reset();
                                  setBookingAddressTitle('');
                                  setBookingAddressValue('');
                                  setBookingAddressMode('create');
                                }}
                              >
                                {modelsPageContent.bookingAddressAddLabel}
                              </button>
                            </>
                          )
                        ) : null}

                        {bookingStep === 'tariff' ? (
                          <div className="models-booking__grid">
                            {bookingTariffOptions.map((item, index) => {
                              const isLastOddItem = bookingTariffOptions.length % 2 === 1 && index === bookingTariffOptions.length - 1;

                              return (
                                <button
                                  key={item.key}
                                  type="button"
                                  className={`models-booking__option${isLastOddItem ? ' models-booking__option--full' : ''}`}
                                  onClick={() => handleBookingTariffSelect(item.key)}
                                  disabled={prepareBookingMutation.isPending}
                                >
                                  <span className="models-booking__option-label">{item.label}</span>
                                  <span className="models-booking__option-meta">{formatPrice(item.value)}</span>
                                </button>
                              );
                            })}
                          </div>
                        ) : null}

                        {bookingStep === 'additionals' ? (
                          <>
                            <div className="models-booking__grid">
                              {sheetAdditionals.map((additional) => {
                                const isSelected = bookingSelection.selectedAdditionalIds.includes(additional.id);

                                return (
                                  <button
                                    key={additional.id}
                                    type="button"
                                    className={`models-booking__option${isSelected ? ' models-booking__option--selected' : ''}`}
                                    onClick={() => handleBookingAdditionalToggle(additional.id)}
                                  >
                                    <span className="models-booking__option-main">
                                      <span className="models-booking__option-label">{additional.name}</span>
                                      <span className="models-booking__option-meta">{formatPrice(additional.price)}</span>
                                    </span>
                                  </button>
                                );
                              })}
                            </div>

                            <button
                              type="button"
                              className="models-booking__cta"
                              onClick={handleBookingAdditionalsContinue}
                              disabled={!bookingSelection.selectedTariff || prepareBookingMutation.isPending}
                            >
                              {modelsPageContent.bookingContinueLabel}
                            </button>
                          </>
                        ) : null}

                        {bookingStep === 'payment-method' ? (
                          <>
                            {prepareBookingMutation.isPending ? (
                              <div className="models-booking__grid">
                                {(['card', 'cash'] as const).map((paymentKey) => (
                                  <div
                                    key={paymentKey}
                                    className="models-booking__option models-booking__option--loading"
                                    aria-hidden="true"
                                  >
                                    <span className="models-booking__option-label">{bookingPaymentMethodLabels[paymentKey]}</span>
                                  </div>
                                ))}
                              </div>
                            ) : null}
                            {prepareBookingMutation.error ? (
                              <p className="models-booking__status models-booking__status--error">{prepareBookingMutation.error.message}</p>
                            ) : null}
                            {preparedBooking?.paymentMethods?.length ? (
                              <div className="models-booking__grid">
                                {preparedBooking.paymentMethods.map((item) => (
                                  <button
                                    key={item.key}
                                    type="button"
                                    className="models-booking__option"
                                    onClick={() => handleBookingPaymentMethodSelect(item.key)}
                                    disabled={resolveBookingPaymentMutation.isPending || prepareBookingMutation.isPending}
                                  >
                                    <span className="models-booking__option-label">{bookingPaymentMethodLabels[item.key]}</span>
                                  </button>
                                ))}
                              </div>
                            ) : null}
                            {resolveBookingPaymentMutation.error ? (
                              <p className="models-booking__status models-booking__status--error">{resolveBookingPaymentMutation.error.message}</p>
                            ) : null}
                          </>
                        ) : null}

                        {bookingStep === 'payment' ? (
                          <>
                            {resolveBookingPaymentMutation.isPending ? (
                              <p className="models-booking__status">{modelsPageContent.bookingPaymentLoadingLabel}</p>
                            ) : null}

                            {bookingPayment?.status === 'card_requisites' && bookingPayment.card ? (
                              <section className="models-sheet__section">
                                <h3 className="models-sheet__section-title">{modelsPageContent.bookingPaymentRequisitesTitle}</h3>
                                <div className="models-booking__payment-list">
                                  <div className="models-booking__summary-row">
                                    <span className="models-booking__summary-label">{modelsPageContent.bookingPaymentOrderLabel}</span>
                                    <span className="models-booking__summary-value">#{bookingPayment.orderNumber}</span>
                                  </div>
                                  <div className="models-booking__summary-row">
                                    <span className="models-booking__summary-label">{modelsPageContent.bookingPaymentModelLabel}</span>
                                    <span className="models-booking__summary-value">{bookingPayment.modelName}</span>
                                  </div>
                                  <div className="models-booking__summary-row">
                                    <span className="models-booking__summary-label">{modelsPageContent.bookingPaymentMethodLabel}</span>
                                    <span className="models-booking__summary-value">{bookingPaymentMethodLabels[bookingPayment.paymentMethod]}</span>
                                  </div>
                                  <div className="models-booking__summary-row">
                                    <span className="models-booking__summary-label">{modelsPageContent.bookingSummaryAmountLabel}</span>
                                    <span className="models-booking__summary-value">{formatPrice(bookingPayment.amount)}</span>
                                  </div>
                                  <div className="models-booking__payment-card">
                                    <span className="models-booking__payment-card-number">{bookingPayment.card.cardNumber}</span>
                                    <div className="models-booking__payment-card-meta">
                                      <span>{modelsPageContent.bookingPaymentBankLabel}: {bookingPayment.card.bankName || '—'}</span>
                                      <span>{modelsPageContent.bookingPaymentHolderLabel}: {bookingPayment.card.holderName || '—'}</span>
                                    </div>
                                  </div>
                                </div>
                                <div className="models-booking__support-cta-wrap">
                                  <button
                                    type="button"
                                    className="models-booking__support-cta"
                                    onClick={() => {}}
                                  >
                                    <span className="models-booking__support-cta-inner">
                                      <span className="models-booking__support-cta-label">Отправить чек</span>
                                    </span>
                                  </button>
                                </div>
                              </section>
                            ) : null}

                            {bookingPayment?.status === 'manual_support' ? (
                              <>
                                <section className="models-sheet__section">
                                  <h3 className="models-sheet__section-title">{modelsPageContent.bookingSupportTitle}</h3>
                                  <p className="models-sheet__section-text models-booking__support-text">{modelsPageContent.bookingSupportDescription}</p>
                                </section>
                                <div className="models-booking__support-cta-wrap">
                                  {supportHref ? (
                                    <a
                                      href={supportHref}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="models-booking__support-cta"
                                    >
                                      <span className="models-booking__support-cta-inner">
                                        <span className="models-booking__support-cta-icon" aria-hidden="true">
                                          <TelegramActionIcon />
                                        </span>
                                        <span className="models-booking__support-cta-label">{modelsPageContent.bookingSupportActionLabel}</span>
                                      </span>
                                    </a>
                                  ) : (
                                    <div className="models-booking__support-cta models-booking__support-cta--disabled">
                                      <span className="models-booking__support-cta-inner">
                                        <span className="models-booking__support-cta-icon" aria-hidden="true">
                                          <TelegramActionIcon />
                                        </span>
                                        <span className="models-booking__support-cta-label">{modelsPageContent.bookingEmptySupportLinkLabel}</span>
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </>
                            ) : null}

                            {bookingPayment?.status === 'cash_unavailable' ? (
                              <section className="models-sheet__section models-booking__cash-unavailable">
                                <h3 className="models-booking__cash-unavailable-title">НАЛИЧНЫЕ СЕЙЧАС НЕДОСТУПНЫ</h3>
                                <p className="models-booking__cash-unavailable-desc">Для оплаты наличными необходимо иметь более 3-х успешных заказов.</p>
                              </section>
                            ) : null}
                          </>
                        ) : null}
                      </div>
                    ) : (
                      <>
                        <div className="models-sheet__media-wrap">
                          <div
                            className="models-sheet__media"
                            onTouchStart={handlePhotoTouchStart}
                            onTouchEnd={handlePhotoTouchEnd}
                          >
                            {sheetPhotos.length ? (
                              <img
                                src={sheetPhotos[activePhotoIndex] || sheetPhotos[0]}
                                alt={sheetModel.name}
                                className="models-sheet__photo"
                                onClick={() => {
                                  if (sheetPhotos.length > 1) {
                                    setActivePhotoIndex((current) => (current + 1) % sheetPhotos.length);
                                  }
                                }}
                              />
                            ) : (
                              <div className="models-sheet__media-placeholder">
                                <Sparkles size={28} />
                              </div>
                            )}
                          </div>

                          {sheetPhotos.length > 1 ? (
                            <>
                              <button
                                type="button"
                                className="models-sheet__arrow models-sheet__arrow--prev"
                                aria-label="Предыдущее фото"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setActivePhotoIndex((current) => (current - 1 + sheetPhotos.length) % sheetPhotos.length);
                                }}
                              >
                                <ChevronLeft size={18} />
                              </button>
                              <button
                                type="button"
                                className="models-sheet__arrow models-sheet__arrow--next"
                                aria-label="Следующее фото"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setActivePhotoIndex((current) => (current + 1) % sheetPhotos.length);
                                }}
                              >
                                <ChevronRight size={18} />
                              </button>
                            </>
                          ) : null}
                        </div>
                        {sheetPhotos.length > 1 ? (
                          <div className="models-sheet__dots" aria-hidden="true">
                            {sheetPhotos.map((_, index) => (
                              <button
                                key={`sheet-dot-${index}`}
                                type="button"
                                className={`models-sheet__dot${index === activePhotoIndex ? ' models-sheet__dot--active' : ''}`}
                                onClick={() => setActivePhotoIndex(index)}
                                aria-label={`Фото ${index + 1}`}
                              />
                            ))}
                          </div>
                        ) : null}
                        <div className="models-sheet__body">
                          <div className="models-sheet__hero">
                            <h2 className="models-sheet__title">{sheetModel.name}</h2>
                            <div className="models-sheet__rating">
                              <RatingStarIcon />
                              <span>
                                {sheetRatingValue != null ? sheetRatingValue.toFixed(1) : '—'} ({sheetReviewsCount} {modelsPageContent.sheetReviewWord})
                              </span>
                            </div>
                          </div>

                          <button
                            type="button"
                            className="models-sheet__action"
                            onClick={handleStartBooking}
                            disabled={!bookingTariffOptions.length}
                          >
                            {modelsPageContent.sheetActionLabel}
                          </button>

                          <div className="models-sheet__facts">
                            <div className="models-sheet__fact">
                              <span className="models-sheet__label">{modelsPageContent.sheetHeightLabel}</span>
                              <span className="models-sheet__value">{getSheetModelValue('height')} см</span>
                            </div>
                            <div className="models-sheet__fact">
                              <span className="models-sheet__label">{modelsPageContent.sheetAgeLabel}</span>
                              <span className="models-sheet__value">{getSheetModelValue('age')} года</span>
                            </div>
                            <div className="models-sheet__fact">
                              <span className="models-sheet__label">{modelsPageContent.sheetSizeLabel}</span>
                              <span className="models-sheet__value">{getSheetModelValue('tits')} размер</span>
                            </div>
                          </div>

                          {sheetPriceItems.length ? (
                            <div className="models-sheet__prices">
                              {sheetPriceItems.map((item, index) => (
                                <div
                                  key={item.key}
                                  className={`models-sheet__price${sheetPriceItems.length % 2 === 1 && index === sheetPriceItems.length - 1 ? ' models-sheet__price--full' : ''}`}
                                >
                                  <span className="models-sheet__label">{item.label}</span>
                                  <span className="models-sheet__value">{formatPrice(item.value)}</span>
                                </div>
                              ))}
                            </div>
                          ) : null}

                          {sheetQuery.isLoading || sheetServices.length ? (
                            <section className="models-sheet__section">
                              <h3 className="models-sheet__section-title">{modelsPageContent.sheetServicesTitle}</h3>
                              {sheetQuery.isLoading ? (
                                <p className="models-sheet__section-text">{modelsPageContent.sheetLoadingLabel}</p>
                              ) : (
                                <div className="models-sheet__services">
                                  {sheetServices.map((service: string) => (
                                    <span key={service} className="models-sheet__service">
                                      {service}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </section>
                          ) : null}

                          {sheetQuery.isLoading || sheetAdditionals.length ? (
                            <section className="models-sheet__section">
                              <h3 className="models-sheet__section-title">{modelsPageContent.sheetAdditionalsTitle}</h3>
                              {sheetQuery.isLoading ? (
                                <p className="models-sheet__section-text">{modelsPageContent.sheetLoadingLabel}</p>
                              ) : (
                                <div className="models-sheet__additionals">
                                  {sheetAdditionals.map((additional) => (
                                    <div key={additional.id} className="models-sheet__additional">
                                      <span className="models-sheet__additional-name">{additional.name}</span>
                                      <span className="models-sheet__additional-price">{formatPrice(additional.price)}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </section>
                          ) : null}
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </>,
        document.body,
      ) : null}
      {favoriteExitGhosts.length ? createPortal(
        <div className="model-card-ghost-layer" aria-hidden="true">
          {favoriteExitGhosts.map((ghost) => (
            <article
              key={`favorite-exit-${ghost.code}`}
              className="card model-card-ghost model-card-ghost--favorite-exit"
              style={{
                top: `${ghost.rect.top}px`,
                left: `${ghost.rect.left}px`,
                width: `${ghost.rect.width}px`,
                height: `${ghost.rect.height}px`,
              }}
            >
              <div className="photo-wrap">
                {ghost.item.previewPhotoUrl ? (
                  <img src={ghost.item.previewPhotoUrl} alt={ghost.item.name} className="photo" />
                ) : (
                  <div className="model-card__image-placeholder">
                    <Sparkles size={18} />
                  </div>
                )}
                {ghost.item.flags.verification || ghost.item.flags.document ? (
                  <div className="model-card__badges">
                    {ghost.item.flags.document ? (
                      <div className="model-card__badge model-card__badge--health">
                        <HealthBadgeIcon />
                        <span>{modelsPageContent.cardHealthLabel}</span>
                      </div>
                    ) : null}
                    {ghost.item.flags.verification ? (
                      <div className="model-card__badge model-card__badge--check">
                        <CheckBadgeIcon />
                        <span>{modelsPageContent.cardVerificationLabel}</span>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
              <div className="card-info">
                <h2>{ghost.item.name}</h2>
                <p>
                  {ghost.item.age} лет • {ghost.item.height} см • {ghost.item.tits} size
                </p>
              </div>
              <div className="actions">
                <button type="button" className="order" tabIndex={-1}>
                  {modelsPageContent.cardAction}
                </button>
                <button
                  className="basket basket--active"
                  type="button"
                  aria-hidden="true"
                  tabIndex={-1}
                >
                  <MaskedIcon
                    src={heartIcon}
                    className="model-card__favorite-icon model-card__favorite-icon--active model-card__favorite-icon--shake"
                  />
                </button>
              </div>
            </article>
          ))}
        </div>,
        document.body,
      ) : null}
      {isSortSheetMounted ? createPortal(
        <>
          <button
            type="button"
            className="models-sheet-backdrop"
            aria-label={modelsPageContent.sortSheetCloseLabel}
            onClick={closeSortSheet}
            style={{
              opacity: sortSheetProgress,
              background: `rgba(9, 10, 14, ${0.1 + (sortSheetProgress * 0.16)})`,
              backdropFilter: `blur(${sortSheetProgress * 16}px)`,
              WebkitBackdropFilter: `blur(${sortSheetProgress * 16}px)`,
              transition: isSortSheetDragging
                ? 'none'
                : `opacity ${SORT_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), background ${SORT_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), backdrop-filter ${SORT_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1), -webkit-backdrop-filter ${SORT_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          />
          <section
            ref={sortSheetRef}
            className="models-sheet models-sort-sheet"
            aria-label={modelsPageContent.sortButtonLabel}
            style={{
              transform: `translateY(${sortSheetTranslateY}px)`,
              transition: isSortSheetDragging ? 'none' : `transform ${SORT_SHEET_TRANSITION_MS}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          >
            <button
              type="button"
              className="models-sheet__drag"
              aria-label={modelsPageContent.sortSheetCloseLabel}
              onPointerDown={handleSortSheetDragStart}
              onPointerMove={handleSortSheetDragMove}
              onPointerUp={handleSortSheetDragEnd}
              onPointerCancel={handleSortSheetDragEnd}
            />
            <div className="models-sheet__content">
              <div className="models-sheet__viewport">
                <div
                  className="models-sheet__scroll"
                  onTouchStart={handleSheetScrollTouchStart}
                  onTouchMove={handleSheetScrollTouchMove}
                >
                  <div className="models-sheet__scroll-inner">
                    <div className="models-sheet__body models-sort-sheet__body">
                      <div className="models-sort-sheet__options" role="radiogroup" aria-label={modelsPageContent.sortButtonLabel}>
                        {sortOptions.map((option) => (
                          <button
                            key={option.value}
                            type="button"
                            role="radio"
                            aria-checked={pendingSort === option.value}
                            className={`models-sort-sheet__option${pendingSort === option.value ? ' models-sort-sheet__option--active' : ''}`}
                            onClick={() => setPendingSort(option.value)}
                          >
                            <span className="models-sort-sheet__radio" aria-hidden="true" />
                            <span className="models-sort-sheet__option-label">{option.label}</span>
                          </button>
                        ))}
                      </div>
                      <button type="button" className="models-sort-sheet__action models-sheet__action glass-block-muted" onClick={applySortSheet}>
                        {modelsPageContent.sortSheetDoneLabel}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </>,
        document.body,
      ) : null}
    </section>
  );
}

function FilterIcon() {
  return <MaskedIcon src={filterIcon} className="models-toolbar__icon models-toolbar__icon--filter" />;
}

function SortIcon() {
  return <MaskedIcon src={sortIcon} className="models-toolbar__icon models-toolbar__icon--sort" />;
}

function EmptyFavoritesIcon() {
  return <MaskedIcon src={heartXmarkIcon} className="models-empty-state__icon models-empty-state__icon--favorites" />;
}

function EmptyModelsIcon() {
  return <MaskedIcon src={eyeSlashIcon} className="models-empty-state__icon models-empty-state__icon--models" />;
}
