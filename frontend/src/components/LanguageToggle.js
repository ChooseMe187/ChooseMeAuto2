import React from "react";
import { useLanguage } from "../context/LanguageContext";
import "../styles/language-toggle.css";

const LanguageToggle = () => {
  const { lang, toggleLang } = useLanguage();

  return (
    <button
      onClick={toggleLang}
      className="cma-lang-toggle"
      aria-label={lang === "en" ? "Switch to Spanish" : "Switch to English"}
    >
      {lang === "en" ? "ES" : "EN"}
    </button>
  );
};

export default LanguageToggle;
