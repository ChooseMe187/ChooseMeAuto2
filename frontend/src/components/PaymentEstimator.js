import React, { useState, useEffect, useCallback } from "react";
import { useLanguage } from "../context/LanguageContext";

// Default financing config
const DEFAULT_CONFIG = {
  defaultApr: 10.99,
  defaultDownPayment: 2000,
  defaultTerm: 72,
  minDownPayment: 0,
  maxDownPayment: 10000,
  terms: [36, 48, 60, 72],
};

// Payment calculation helper
const calculateMonthlyPayment = (price, downPayment, term, apr) => {
  const principal = Math.max(0, price - downPayment);
  if (principal <= 0 || term <= 0) return 0;
  
  const monthlyRate = apr / 100 / 12;
  if (monthlyRate === 0) return principal / term;
  
  const payment =
    (principal * monthlyRate * Math.pow(1 + monthlyRate, term)) /
    (Math.pow(1 + monthlyRate, term) - 1);
  
  return Math.round(payment);
};

const PaymentEstimator = ({ 
  price, 
  compact = false,
  showDisclaimer = true,
  onChange = null,
  initialDownPayment = DEFAULT_CONFIG.defaultDownPayment,
  initialTerm = DEFAULT_CONFIG.defaultTerm,
}) => {
  const { lang } = useLanguage();
  const [downPayment, setDownPayment] = useState(initialDownPayment);
  const [term, setTerm] = useState(initialTerm);
  const [monthlyPayment, setMonthlyPayment] = useState(0);

  const { defaultApr, minDownPayment, maxDownPayment, terms } = DEFAULT_CONFIG;

  // Calculate payment whenever inputs change
  useEffect(() => {
    if (price && price > 0) {
      const payment = calculateMonthlyPayment(price, downPayment, term, defaultApr);
      setMonthlyPayment(payment);
      onChange?.({ downPayment, term, monthlyPayment: payment });
    }
  }, [price, downPayment, term, defaultApr, onChange]);

  const handleDownPaymentChange = useCallback((value) => {
    const numValue = Math.max(minDownPayment, Math.min(maxDownPayment, Number(value) || 0));
    setDownPayment(numValue);
  }, [minDownPayment, maxDownPayment]);

  const copy = {
    downPayment: { en: "Down Payment", es: "Enganche" },
    term: { en: "Term", es: "Plazo" },
    months: { en: "months", es: "meses" },
    estMonthly: { en: "Est.", es: "Est." },
    perMonth: { en: "/mo", es: "/mes" },
    basedOn: { en: "Based on", es: "Basado en" },
    down: { en: "down", es: "de enganche" },
    disclaimer: {
      en: "Estimated payment is for illustration only. Actual terms vary based on credit, lender approval, taxes, fees, and trade-in. Not a commitment to lend.",
      es: "El pago estimado es solo ilustrativo. Los términos reales varían según crédito, aprobación del prestamista, impuestos, tarifas y vehículo a cambio. No es un compromiso de préstamo.",
    },
  };

  if (!price || price <= 0) {
    return null;
  }

  // Compact version for vehicle cards
  if (compact) {
    return (
      <div className="payment-estimator-compact">
        <div className="pe-inputs-row">
          <div className="pe-input-group">
            <label>{copy.downPayment[lang]}</label>
            <div className="pe-input-wrapper">
              <span className="pe-currency">$</span>
              <input
                type="number"
                value={downPayment}
                onChange={(e) => handleDownPaymentChange(e.target.value)}
                min={minDownPayment}
                max={maxDownPayment}
                step={500}
              />
            </div>
          </div>
          <div className="pe-input-group">
            <label>{copy.term[lang]}</label>
            <select value={term} onChange={(e) => setTerm(Number(e.target.value))}>
              {terms.map((t) => (
                <option key={t} value={t}>
                  {t} {copy.months[lang]}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="pe-result">
          <span className="pe-result-label">{copy.estMonthly[lang]}</span>
          <span className="pe-result-value">
            ${monthlyPayment.toLocaleString()}
            <span className="pe-result-period">{copy.perMonth[lang]}</span>
          </span>
        </div>
        
        <div className="pe-microcopy">
          {copy.basedOn[lang]} ${downPayment.toLocaleString()} {copy.down[lang]}, {term} {copy.months[lang]}
        </div>
      </div>
    );
  }

  // Full version with slider
  return (
    <div className="payment-estimator">
      <div className="pe-header">
        <h4>{lang === "es" ? "Calculadora de Pago" : "Payment Calculator"}</h4>
      </div>

      <div className="pe-body">
        {/* Down Payment */}
        <div className="pe-field">
          <div className="pe-field-header">
            <label>{copy.downPayment[lang]}</label>
            <div className="pe-input-wrapper">
              <span className="pe-currency">$</span>
              <input
                type="number"
                value={downPayment}
                onChange={(e) => handleDownPaymentChange(e.target.value)}
                min={minDownPayment}
                max={maxDownPayment}
                step={500}
              />
            </div>
          </div>
          <input
            type="range"
            className="pe-slider"
            value={downPayment}
            onChange={(e) => handleDownPaymentChange(e.target.value)}
            min={minDownPayment}
            max={maxDownPayment}
            step={500}
          />
          <div className="pe-slider-labels">
            <span>${minDownPayment.toLocaleString()}</span>
            <span>${maxDownPayment.toLocaleString()}</span>
          </div>
        </div>

        {/* Term */}
        <div className="pe-field">
          <label>{copy.term[lang]}</label>
          <div className="pe-term-buttons">
            {terms.map((t) => (
              <button
                key={t}
                type="button"
                className={`pe-term-btn ${term === t ? "active" : ""}`}
                onClick={() => setTerm(t)}
              >
                {t} {copy.months[lang]}
              </button>
            ))}
          </div>
        </div>

        {/* Result */}
        <div className="pe-result-box">
          <div className="pe-result-main">
            <span className="pe-result-label">{copy.estMonthly[lang]}</span>
            <span className="pe-result-value">
              ${monthlyPayment.toLocaleString()}
              <span className="pe-result-period">{copy.perMonth[lang]}</span>
            </span>
          </div>
          <div className="pe-microcopy">
            {copy.basedOn[lang]} ${downPayment.toLocaleString()} {copy.down[lang]}, {term} {copy.months[lang]}, {defaultApr}% APR
          </div>
        </div>
      </div>

      {showDisclaimer && (
        <div className="pe-disclaimer">
          <p>{copy.disclaimer[lang]}</p>
        </div>
      )}
    </div>
  );
};

export default PaymentEstimator;
