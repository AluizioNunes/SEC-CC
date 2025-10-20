import React, { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import pt from './locales/pt.json';
import en from './locales/en.json';

export type Locale = 'pt' | 'en';

type Dictionary = Record<string, string>;

const dictionaries: Record<Locale, Dictionary> = {
  pt,
  en,
};

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18nProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [locale, setLocale] = useState<Locale>(() => {
    const saved = localStorage.getItem('sec-locale') as Locale | null;
    if (saved === 'pt' || saved === 'en') return saved;
    const browserLang = navigator.language?.slice(0, 2);
    return browserLang === 'en' ? 'en' : 'pt';
  });

  const dict = useMemo(() => dictionaries[locale], [locale]);

  const t = useMemo(
    () => (key: string, vars?: Record<string, string | number>) => {
      const template = dict[key] ?? key;
      if (!vars) return template;
      return template.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? `{${k}}`));
    },
    [dict]
  );

  const value: I18nContextType = {
    locale,
    setLocale: (l) => {
      localStorage.setItem('sec-locale', l);
      setLocale(l);
    },
    t,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export const useI18n = () => {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
};