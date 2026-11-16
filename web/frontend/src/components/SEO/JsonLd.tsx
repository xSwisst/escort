import React from 'react';
import { FAQ_ITEMS } from '../../data/faqData';
import { MODELS_DATA } from '../../data/modelsData';

export const JsonLd: React.FC = () => {
  const organizationSchema = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    '@id': 'https://elegant.fun/#organization',
    name: 'Elegant Agency',
    legalName: 'Elegant Agency VIP Concierge Ltd',
    url: 'https://elegant.fun',
    logo: 'https://elegant.fun/favicon.svg',
    image: 'https://elegant.fun/og-preview.jpg',
    description:
      'Премиальное агентство VIP моделей и персонального консьерж-сопровождения. 100% верификация фото и медицинский контроль. Москва, СПб, Дубай, Сочи.',
    telephone: '+7 (999) 000-77-88',
    priceRange: '$$$$',
    currenciesAccepted: 'RUB, USD, EUR, USDT',
    paymentAccepted: 'Cash, Credit Card, Cryptocurrency',
    address: {
      '@type': 'PostalAddress',
      addressLocality: 'Москва',
      addressRegion: 'Москва',
      addressCountry: 'RU',
    },
    openingHoursSpecification: [
      {
        '@type': 'OpeningHoursSpecification',
        dayOfWeek: [
          'Monday',
          'Tuesday',
          'Wednesday',
          'Thursday',
          'Friday',
          'Saturday',
          'Sunday',
        ],
        opens: '00:00',
        closes: '23:59',
      },
    ],
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.98',
      bestRating: '5',
      worstRating: '1',
      ratingCount: '143',
    },
  };

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: FAQ_ITEMS.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  };

  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Главная',
        item: 'https://elegant.fun',
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Каталог моделей',
        item: 'https://elegant.fun/#catalog',
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: 'Форматы встреч',
        item: 'https://elegant.fun/#services',
      },
    ],
  };

  const productCatalogSchema = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Каталог VIP моделей Elegant Agency',
    itemListElement: MODELS_DATA.map((model, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      item: {
        '@type': 'Product',
        name: `${model.name} — VIP модель ${model.cityName}`,
        image: `https://elegant.fun${model.photos[0]}`,
        description: model.description,
        sku: model.code,
        offers: {
          '@type': 'Offer',
          url: `https://elegant.fun/#model-${model.id}`,
          priceCurrency: 'RUB',
          price: model.prices.oneHour,
          priceValidUntil: '2027-12-31',
          availability: 'https://schema.org/InStock',
        },
        aggregateRating: {
          '@type': 'AggregateRating',
          ratingValue: model.rating.toString(),
          reviewCount: model.reviewsCount.toString(),
        },
      },
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(productCatalogSchema) }}
      />
    </>
  );
};
