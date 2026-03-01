import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslation from './locales/en.json';
import hiTranslation from './locales/hi.json';
import knTranslation from './locales/kn.json';
import teTranslation from './locales/te.json';
import taTranslation from './locales/ta.json';

const resources = {
    en: { translation: enTranslation },
    hi: { translation: hiTranslation },
    kn: { translation: knTranslation },
    te: { translation: teTranslation },
    ta: { translation: taTranslation },
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: 'en',
        debug: false,
        interpolation: {
            escapeValue: false,
        },
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
        },
    });

export default i18n;
