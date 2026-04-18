"""
arcticsecurityshield_app.py - Flask web application

Tabs: URL Scanner | Email Analyser | Phone Checker | Stay Safe Guide

Run:
  pip install flask joblib pandas numpy scikit-learn
  python app/arcticsecurityshield_app.py
  Open: http://localhost:5000
"""

import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.filterwarnings("ignore")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, request, jsonify, render_template_string
from src.predict import predict
from src.email_analyzer import analyze_email
from src.phone_checker import check_phone

app = Flask(__name__)

INLINE_HTML = r"""<!DOCTYPE html>
<html lang="en" id="html-root">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ArcticSecurityShield</title>
  <style>
    :root{
      --teal:#004B5A;--teal-light:#E6F2F4;--teal-mid:#007A8C;
      --red:#D32F2F;--red-light:#FFEBEE;
      --orange:#E65100;--orange-light:#FFF3E0;
      --green:#2E7D32;--green-light:#E8F5E9;
      --grey:#607D8B;--bg:#F5F7F8;--white:#FFFFFF;
      --radius:12px;--shadow:0 4px 24px rgba(0,75,90,0.10);
      --base-size: 16px;
    }
    *{box-sizing:border-box;margin:0;padding:0}
    html{font-size:var(--base-size)}
    body{font-family:'Segoe UI',Arial,sans-serif;background:var(--bg);color:#1a1a2e;min-height:100vh}

    /* ── Top bar ── */
    nav{background:var(--teal);padding:0 1.2rem;display:flex;align-items:center;gap:.8rem;min-height:60px;box-shadow:0 2px 8px rgba(0,0,0,0.2);flex-wrap:wrap;gap:.5rem}
    nav .logo{font-size:1.2rem;font-weight:800;color:#fff;white-space:nowrap}
    nav .tagline{font-size:0.78rem;color:rgba(255,255,255,0.65);display:none}
    @media(min-width:600px){nav .tagline{display:block}}
    .nav-controls{margin-left:auto;display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}

    /* ── Language switcher ── */
    .lang-btn{background:rgba(255,255,255,0.15);color:#fff;border:1px solid rgba(255,255,255,0.3);
              padding:4px 10px;border-radius:20px;font-size:.78rem;font-weight:700;cursor:pointer;transition:background .2s}
    .lang-btn.active{background:rgba(255,255,255,0.9);color:var(--teal)}
    .lang-btn:hover:not(.active){background:rgba(255,255,255,0.25)}

    /* ── Font size controls ── */
    .size-controls{display:flex;align-items:center;gap:3px}
    .size-btn{background:rgba(255,255,255,0.15);color:#fff;border:1px solid rgba(255,255,255,0.3);
              width:28px;height:28px;border-radius:6px;font-size:.85rem;font-weight:700;
              cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s}
    .size-btn:hover{background:rgba(255,255,255,0.3)}
    .size-label{color:rgba(255,255,255,0.7);font-size:.72rem;margin:0 2px}

    /* ── Hero ── */
    .hero{background:linear-gradient(135deg,var(--teal) 0%,var(--teal-mid) 100%);color:white;text-align:center;padding:2rem 1rem 0}
    .hero h1{font-size:1.8rem;font-weight:800;margin-bottom:.3rem}
    .hero p{font-size:.95rem;opacity:.85;max-width:520px;margin:0 auto 1rem}
    .tab-bar{display:flex;justify-content:center;gap:3px;padding:0 .5rem;flex-wrap:wrap}
    .tab-btn{background:rgba(255,255,255,0.12);color:rgba(255,255,255,0.75);border:none;
             padding:.6rem 1.1rem;cursor:pointer;font-size:.85rem;font-weight:600;
             border-radius:8px 8px 0 0;transition:all .2s;margin-bottom:2px}
    .tab-btn.active{background:var(--bg);color:var(--teal)}
    .tab-btn:hover:not(.active){background:rgba(255,255,255,0.22);color:#fff}

    /* ── Panels ── */
    .panel{display:none;max-width:720px;margin:0 auto;padding:1.2rem 1rem}
    .panel.active{display:block}
    .card{background:var(--white);border-radius:var(--radius);padding:1.3rem;box-shadow:var(--shadow);margin-bottom:1.2rem}
    .row{display:flex;gap:.6rem}
    .inp{flex:1;padding:.75rem 1rem;border:2px solid #ddd;border-radius:8px;font-size:1rem;
         outline:none;transition:border-color .2s;font-family:inherit}
    .inp:focus{border-color:var(--teal-mid)}
    textarea.inp{resize:vertical;min-height:140px}
    .btn{background:var(--teal);color:white;border:none;padding:.75rem 1.3rem;border-radius:8px;
         font-size:1rem;font-weight:700;cursor:pointer;transition:background .2s;white-space:nowrap}
    .btn:hover{background:var(--teal-mid)}
    .btn:disabled{opacity:.6;cursor:not-allowed}
    .hint{font-size:.82rem;color:var(--grey);margin-top:.5rem}
    .chips{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.5rem}
    .chip{background:var(--teal-light);color:var(--teal);border:none;padding:5px 11px;
          border-radius:20px;font-size:.8rem;cursor:pointer;font-weight:600}
    .chip:hover{background:#c8e6ea}
    .slabel{font-size:.85rem;color:var(--grey);white-space:nowrap;align-self:center}
    .sinp{flex:1;padding:.55rem .9rem;border:2px solid #ddd;border-radius:8px;font-size:.9rem;outline:none}
    .sinp:focus{border-color:var(--teal-mid)}

    /* ── Result card ── */
    .result{background:var(--white);border-radius:var(--radius);padding:1.3rem;
            box-shadow:var(--shadow);display:none;animation:fi .3s ease;margin-bottom:1.2rem}
    @keyframes fi{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
    .risk-high{border-left:6px solid var(--red)}
    .risk-medium{border-left:6px solid var(--orange)}
    .risk-low{border-left:6px solid var(--green)}

    /* Traffic light */
    .traffic-light{display:flex;gap:.5rem;align-items:center;margin:.6rem 0}
    .tl-dot{width:26px;height:26px;border-radius:50%;opacity:.18;transition:opacity .4s}
    .tl-dot.active{opacity:1}
    .tl-red{background:var(--red)}
    .tl-orange{background:#FF9800}
    .tl-green{background:var(--green)}

    .risk-title{font-size:1.3rem;font-weight:800;margin-bottom:.1rem}
    .risk-high .risk-title{color:var(--red)}
    .risk-medium .risk-title{color:var(--orange)}
    .risk-low .risk-title{color:var(--green)}
    .risk-sub{font-size:.8rem;color:var(--grey);word-break:break-all;margin-bottom:.6rem}

    .verdict{font-size:1.1rem;font-weight:700;padding:.7rem 1rem;border-radius:8px;margin-bottom:.8rem;line-height:1.4}
    .verdict.high{background:var(--red-light);color:var(--red)}
    .verdict.medium{background:var(--orange-light);color:var(--orange)}
    .verdict.low{background:var(--green-light);color:var(--green)}

    .expl{padding:.8rem 1rem;border-radius:8px;font-size:.95rem;line-height:1.65;margin-bottom:.8rem;color:#333;background:#f7f7f7}
    .ftitle{font-size:.9rem;font-weight:700;color:var(--teal);margin-bottom:.5rem}
    .flag{font-size:.88rem;color:#444;margin-bottom:.35rem;padding:.4rem .7rem;background:#f0f0f0;border-radius:6px;line-height:1.5}
    .fcat{font-weight:700;color:var(--teal)}
    .noflag{font-size:.88rem;color:var(--green);padding:.3rem 0}
    .dtbtn{background:none;border:1px solid #ddd;border-radius:6px;padding:5px 12px;
           font-size:.82rem;color:var(--grey);cursor:pointer;margin-top:.7rem}
    .dtbtn:hover{background:var(--teal-light);color:var(--teal)}
    .dtsec{display:none;margin-top:.7rem;font-size:.8rem}
    .dtsec table{width:100%;border-collapse:collapse}
    .dtsec th{background:var(--teal-light);color:var(--teal);padding:5px 8px;text-align:left}
    .dtsec td{padding:4px 8px;border-bottom:1px solid #f0f0f0}
    .mbadge{display:inline-block;background:var(--teal-light);color:var(--teal);font-size:.72rem;padding:2px 9px;border-radius:20px;margin-top:.5rem}
    .spin{display:none;width:16px;height:16px;border:3px solid rgba(255,255,255,.4);border-top-color:white;border-radius:50%;animation:sp .7s linear infinite}
    @keyframes sp{to{transform:rotate(360deg)}}
    .bi{display:flex;align-items:center;justify-content:center;gap:.4rem}

    /* Bottom info cards */
    .ag{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:.8rem;margin-top:1.5rem}
    .ac{background:var(--white);border-radius:var(--radius);padding:1rem;box-shadow:var(--shadow);border-top:3px solid var(--teal)}
    .ac h4{font-size:.88rem;font-weight:700;color:var(--teal);margin-bottom:.3rem}
    .ac p{font-size:.8rem;color:#555;line-height:1.5}

    /* ── Education page ── */
    .edu-section{background:var(--white);border-radius:var(--radius);padding:1.3rem;box-shadow:var(--shadow);margin-bottom:1.1rem}
    .edu-section h3{color:var(--teal);font-size:1.05rem;margin-bottom:.8rem;padding-bottom:.4rem;border-bottom:2px solid var(--teal-light)}
    .edu-tip{display:flex;gap:.8rem;margin-bottom:.75rem;align-items:flex-start}
    .edu-num{background:var(--teal);color:white;border-radius:50%;width:26px;height:26px;
             display:flex;align-items:center;justify-content:center;font-size:.82rem;
             font-weight:700;flex-shrink:0;margin-top:2px}
    .edu-tip-text{font-size:.9rem;line-height:1.6;color:#333}
    .edu-tip-text strong{color:var(--teal)}
    .edu-example{background:#f5f5f5;border-left:3px solid var(--teal-mid);padding:.6rem .9rem;
                 border-radius:0 6px 6px 0;font-size:.84rem;margin:.3rem 0 .7rem 2.2rem;color:#444;line-height:1.5}
    .edu-bad{color:var(--red);font-weight:700}
    .edu-good{color:var(--green);font-weight:700}

    /* Quiz */
    .quiz-q{margin-bottom:1.1rem;padding-bottom:1.1rem;border-bottom:1px solid #eee}
    .quiz-q:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0}
    .quiz-text{font-size:.9rem;font-weight:600;margin-bottom:.5rem;color:#222}
    .quiz-example{font-size:.85rem;background:#f5f5f5;padding:.5rem .8rem;border-radius:6px;margin-bottom:.5rem;color:#444}
    .quiz-options{display:flex;flex-wrap:wrap;gap:.4rem}
    .quiz-btn{background:var(--teal-light);color:var(--teal);border:1px solid var(--teal-mid);
              padding:.5rem 1rem;border-radius:8px;cursor:pointer;font-size:.85rem;font-weight:600;transition:all .2s}
    .quiz-btn:hover:not(:disabled){background:var(--teal-mid);color:white}
    .quiz-btn:disabled{cursor:default;opacity:.7}
    .quiz-btn.correct-answer{background:#C8E6C9;color:var(--green);border-color:var(--green)}
    .quiz-btn.wrong-answer{background:#FFCDD2;color:var(--red);border-color:var(--red)}
    .quiz-feedback{font-size:.85rem;padding:.5rem .8rem;border-radius:6px;margin-top:.5rem;display:none;line-height:1.5}
    .quiz-feedback.correct{background:var(--green-light);color:var(--green)}
    .quiz-feedback.wrong{background:var(--red-light);color:var(--red)}
    .quiz-reset-btn{background:var(--teal);color:white;border:none;padding:.6rem 1.2rem;
                    border-radius:8px;font-size:.88rem;font-weight:700;cursor:pointer;margin-top:1rem}
    .quiz-reset-btn:hover{background:var(--teal-mid)}
    .quiz-score{font-size:.95rem;font-weight:700;color:var(--teal);margin-top:.5rem}

    footer{text-align:center;padding:1rem;font-size:.75rem;color:var(--grey);border-top:1px solid #e0e0e0;margin-top:.8rem}
  </style>
</head>
<body>

<nav>
  <span class="logo">ArcticSecurityShield</span>
  <span class="tagline" data-t="tagline">AI Scam & Phishing Detector</span>
  <div class="nav-controls">
    <!-- Language switcher -->
    <button class="lang-btn active" id="btn-en" onclick="setLang('en')">EN</button>
    <button class="lang-btn" id="btn-nl" onclick="setLang('nl')">NL</button>
    <!-- Font size controls -->
    <div class="size-controls">
      <span class="size-label" data-t="text-size">Text</span>
      <button class="size-btn" onclick="changeSize(-1)" title="Smaller text">A-</button>
      <button class="size-btn" onclick="changeSize(1)" title="Larger text">A+</button>
    </div>
  </div>
</nav>

<div class="hero">
  <h1 data-t="hero-title">Stay safe online</h1>
  <p data-t="hero-sub">Check suspicious links, emails, and phone numbers - explained in plain language for everyone.</p>
  <div class="tab-bar">
    <button class="tab-btn active" onclick="sw('url',this)" data-t="tab-url">Link Checker</button>
    <button class="tab-btn" onclick="sw('email',this)" data-t="tab-email">Email Analyser</button>
    <button class="tab-btn" onclick="sw('phone',this)" data-t="tab-phone">Phone Checker</button>
    <button class="tab-btn" onclick="sw('guide',this)" data-t="tab-guide">Stay Safe Guide</button>
  </div>
</div>

<div style="max-width:720px;margin:0 auto;padding:0 1rem">

<!-- URL TAB -->
<div class="panel active" id="p-url">
  <div class="card">
    <div class="row">
      <input class="inp" id="urlI" type="text" autocomplete="off" spellcheck="false"
             onkeydown="if(event.key==='Enter')scanUrl()"
             data-placeholder-t="url-placeholder"/>
      <button class="btn" id="urlB" onclick="scanUrl()">
        <div class="bi"><span id="urlT" data-t="btn-scan">Check</span><div class="spin" id="urlS"></div></div>
      </button>
    </div>
    <p class="hint" data-t="url-examples-label">Examples to try:</p>
    <div class="chips">
      <button class="chip" onclick="su('https://www.google.com')" data-t="chip-safe">google.com (safe)</button>
      <button class="chip" onclick="su('https://rnicrosoft.com')" data-t="chip-typo">rnicrosoft.com (fake domain)</button>
      <button class="chip" onclick="su('http://paypal-login-secure.com/verify')" data-t="chip-phish">paypal-login-secure (scam)</button>
      <button class="chip" onclick="su('http://bit.ly/3xK9mZ')" data-t="chip-short">bit.ly (hidden link)</button>
    </div>
  </div>
  <div class="result" id="r-url"></div>
</div>

<!-- EMAIL TAB -->
<div class="panel" id="p-email">
  <div class="card">
    <div class="row" style="margin-bottom:.55rem">
      <span class="slabel" data-t="sender-label">Sender (optional):</span>
      <input class="sinp" id="sndI" type="text" placeholder="e.g. security@paypa1.com"/>
    </div>
    <textarea class="inp" id="emlI" data-placeholder-t="email-placeholder"></textarea>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:.55rem;flex-wrap:wrap;gap:.4rem">
      <div class="chips">
        <button class="chip" onclick="lse(1)" data-t="load-phish-en">Load phishing example</button>
        <button class="chip" onclick="lse(2)" data-t="load-phish-nl">Load Dutch phishing example</button>
        <button class="chip" onclick="lse(0)" data-t="load-legit">Load normal email</button>
      </div>
      <button class="btn" id="emlB" onclick="scanEmail()">
        <div class="bi"><span id="emlT" data-t="btn-analyse">Analyse</span><div class="spin" id="emlS"></div></div>
      </button>
    </div>
  </div>
  <div class="result" id="r-email"></div>
</div>

<!-- PHONE TAB -->
<div class="panel" id="p-phone">
  <div class="card">
    <div class="row">
      <input class="inp" id="phI" type="text" autocomplete="off"
             onkeydown="if(event.key==='Enter')scanPhone()"
             data-placeholder-t="phone-placeholder"/>
      <button class="btn" id="phB" onclick="scanPhone()">
        <div class="bi"><span id="phT" data-t="btn-check">Check</span><div class="spin" id="phS"></div></div>
      </button>
    </div>
    <p class="hint" data-t="phone-examples-label">Examples to try:</p>
    <div class="chips">
      <button class="chip" onclick="sp('+32 2 123 45 67')" data-t="chip-phone-safe">+32 2 123 45 67 (safe)</button>
      <button class="chip" onclick="sp('+32 0909 12345')" data-t="chip-phone-prem">+32 0909 (premium rate)</button>
      <button class="chip" onclick="sp('+1 876 555 0100')" data-t="chip-phone-scam">+1 876 Jamaica (callback scam)</button>
    </div>
  </div>
  <div class="result" id="r-phone"></div>
</div>

<!-- GUIDE TAB -->
<div class="panel" id="p-guide">

  <div class="edu-section">
    <h3 data-t="guide-links-title">How to recognise a fake link</h3>
    <div class="edu-tip">
      <div class="edu-num">1</div>
      <div class="edu-tip-text" data-t="guide-link-1"><strong>Look at the domain name carefully.</strong> Scammers create addresses that look almost identical to real ones.</div>
    </div>
    <div class="edu-example">
      <span class="edu-bad">paypa1.com</span> &nbsp;(number 1 instead of letter l) &nbsp;|&nbsp;
      <span class="edu-bad">paypal-login-secure.com</span> &nbsp;(extra words)<br>
      <span class="edu-good">paypal.com</span> &nbsp;(the real address)
    </div>
    <div class="edu-tip">
      <div class="edu-num">2</div>
      <div class="edu-tip-text" data-t="guide-link-2"><strong>Look for https:// at the start.</strong> A link starting with http:// (without the s) is less secure.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">3</div>
      <div class="edu-tip-text" data-t="guide-link-3"><strong>Short links hide the real address.</strong> Links like bit.ly/abc123 don't show where they really go. Be very careful with these.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">4</div>
      <div class="edu-tip-text" data-t="guide-link-4"><strong>Hover before you click.</strong> Move your mouse over a link without clicking. The real address appears at the bottom of your screen.</div>
    </div>
  </div>

  <div class="edu-section">
    <h3 data-t="guide-email-title">How to recognise a scam email</h3>
    <div class="edu-tip">
      <div class="edu-num">1</div>
      <div class="edu-tip-text" data-t="guide-email-1"><strong>"Act now" is a warning sign.</strong> Phrases like "Your account will be blocked in 24 hours" are designed to make you panic and act without thinking.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">2</div>
      <div class="edu-tip-text" data-t="guide-email-2"><strong>Real organisations never ask for your password by email.</strong> Banks, PayPal, and government agencies will never ask you to confirm your password or PIN in an email.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">3</div>
      <div class="edu-tip-text" data-t="guide-email-3"><strong>Check who really sent it.</strong> The name may say "ING Bank" but the actual address might be something like ing@nep-domein.ru.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">4</div>
      <div class="edu-tip-text" data-t="guide-email-4"><strong>Friendly emails asking for money are also scams.</strong> Some scam emails are very polite and patient. They promise you a share of a large sum. Always a scam.</div>
    </div>
    <div class="edu-example" data-t="guide-419-example">
      Example: "Dear Friend, I know this message will come to you as a surprise but I need your help to transfer funds..."
    </div>
  </div>

  <div class="edu-section">
    <h3 data-t="guide-phone-title">How to recognise a fraudulent phone number</h3>
    <div class="edu-tip">
      <div class="edu-num">1</div>
      <div class="edu-tip-text" data-t="guide-phone-1"><strong>Numbers starting with 0900 cost money to call.</strong> Calling these can cost several euros per minute. Real organisations never ask you to call them.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">2</div>
      <div class="edu-tip-text" data-t="guide-phone-2"><strong>Do not call back unknown foreign numbers.</strong> Numbers from the Caribbean (+1 473, +1 876) are often used in callback scams. They call once and hope you call back.</div>
    </div>
    <div class="edu-tip">
      <div class="edu-num">3</div>
      <div class="edu-tip-text" data-t="guide-phone-3"><strong>Your bank will never ask you to call a number from a text message.</strong> Always look up the official number yourself — check the back of your bank card.</div>
    </div>
  </div>

  <div class="edu-section" id="quiz-section">
    <h3 data-t="quiz-title">Quick quiz</h3>
    <p style="font-size:.88rem;color:#555;margin-bottom:1rem" data-t="quiz-intro">Can you spot the scam? New questions appear each time you reset.</p>
    <div id="quiz-container"></div>
    <button class="quiz-reset-btn" onclick="initQuiz()" data-t="quiz-reset">Try new questions</button>
    <div class="quiz-score" id="quiz-score"></div>
  </div>

</div><!-- end guide panel -->

<div class="ag" id="bottom-cards">
  <div class="ac"><h4 data-t="card1-title">Who is this for?</h4><p data-t="card1-body">Elderly users, refugees, and people with low digital literacy - most vulnerable to online scams.</p></div>
  <div class="ac"><h4 data-t="card2-title">How it works</h4><p data-t="card2-body">AI models detect scam patterns. Every result is explained in plain language - no technical knowledge needed.</p></div>
  <div class="ac"><h4 data-t="card3-title">SDG 10</h4><p data-t="card3-body">Digital safety should not depend on technical knowledge. Everyone deserves protection online.</p></div>
  <div class="ac"><h4 data-t="card4-title">Privacy</h4><p data-t="card4-body">Nothing is stored. No tracking. Runs on your computer. Free and open source.</p></div>
</div>
</div>
<footer>ArcticSecurityShield - GRAILS 2026 - SDG 10: Reduced Inequalities - MIT License</footer>

<script>
// ── Translations ──────────────────────────────────────────────────────────────
const T = {
  en: {
    "tagline":            "AI Scam & Phishing Detector",
    "hero-title":         "Stay safe online",
    "hero-sub":           "Check suspicious links, emails, and phone numbers - explained in plain language for everyone.",
    "tab-url":            "Link Checker",
    "tab-email":          "Email Analyser",
    "tab-phone":          "Phone Checker",
    "tab-guide":          "Stay Safe Guide",
    "url-placeholder":    "Paste a link here, e.g. https://rnicrosoft.com",
    "email-placeholder":  "Paste the email text here...",
    "phone-placeholder":  "Paste a phone number here, e.g. +32 0909 12345",
    "btn-scan":           "Check",
    "btn-analyse":        "Analyse",
    "btn-check":          "Check",
    "sender-label":       "Sender (optional):",
    "url-examples-label": "Examples to try:",
    "phone-examples-label":"Examples to try:",
    "chip-safe":          "google.com (safe)",
    "chip-typo":          "rnicrosoft.com (fake domain)",
    "chip-phish":         "paypal-login-secure (scam)",
    "chip-short":         "bit.ly (hidden link)",
    "chip-phone-safe":    "+32 2 123 45 67 (safe)",
    "chip-phone-prem":    "+32 0909 (premium rate)",
    "chip-phone-scam":    "+1 876 Jamaica (callback scam)",
    "load-phish-en":      "Load scam example",
    "load-phish-nl":      "Load Dutch scam example",
    "load-legit":         "Load normal email",
    "text-size":          "Text",
    "flagged-title":      "Why was this flagged?",
    "no-flags":           "No suspicious signals found.",
    "tech-details":       "Technical details",
    "hide-details":       "Hide details",
    "verdict-high":       "We think this is a scam.",
    "verdict-medium":     "This looks suspicious. Be careful.",
    "verdict-low":        "This looks safe.",
    "guide-links-title":  "How to recognise a fake link",
    "guide-link-1":       "<strong>Look at the domain name carefully.</strong> Scammers create addresses that look almost identical to real ones.",
    "guide-link-2":       "<strong>Look for https:// at the start.</strong> A link starting with http:// (without the s) is less secure.",
    "guide-link-3":       "<strong>Short links hide the real address.</strong> Links like bit.ly/abc123 don't show where they really go.",
    "guide-link-4":       "<strong>Hover before you click.</strong> Move your mouse over a link without clicking to see the real address.",
    "guide-email-title":  "How to recognise a scam email",
    "guide-email-1":      "<strong>'Act now' is a warning sign.</strong> Phrases like 'Your account will be blocked in 24 hours' are designed to make you panic.",
    "guide-email-2":      "<strong>Real organisations never ask for your password by email.</strong> Banks and government agencies will never ask for your PIN by email.",
    "guide-email-3":      "<strong>Check who really sent it.</strong> The name may say 'ING Bank' but the real address may be something like ing@fake-domain.ru.",
    "guide-email-4":      "<strong>Friendly emails asking for money are also scams.</strong> Some scam emails are very polite. They promise a share of a large sum. Always a scam.",
    "guide-419-example":  "Example: \"Dear Friend, I know this message will come to you as a surprise but I need your help to transfer funds...\"",
    "guide-phone-title":  "How to recognise a fraudulent phone number",
    "guide-phone-1":      "<strong>Numbers starting with 0900 cost money to call.</strong> Calling these can cost several euros per minute. Real organisations never ask you to call them.",
    "guide-phone-2":      "<strong>Do not call back unknown foreign numbers.</strong> Numbers from the Caribbean (+1 473, +1 876) are often used in callback scams.",
    "guide-phone-3":      "<strong>Your bank will never ask you to call a number from a text message.</strong> Always look up the official number yourself.",
    "quiz-title":         "Quick quiz",
    "quiz-intro":         "Can you spot the scam? New questions appear each time you reset.",
    "quiz-reset":         "Try new questions",
    "card1-title":        "Who is this for?",
    "card1-body":         "Elderly users, refugees, and people with low digital literacy - most vulnerable to online scams.",
    "card2-title":        "How it works",
    "card2-body":         "AI models detect scam patterns. Every result is explained in plain language - no technical knowledge needed.",
    "card3-title":        "SDG 10",
    "card3-body":         "Digital safety should not depend on technical knowledge. Everyone deserves protection online.",
    "card4-title":        "Privacy",
    "card4-body":         "Nothing is stored. No tracking. Runs on your computer. Free and open source.",
  },
  nl: {
    "tagline":            "AI Oplichting & Phishing Detector",
    "hero-title":         "Blijf veilig online",
    "hero-sub":           "Controleer verdachte links, e-mails en telefoonnummers - uitgelegd in begrijpelijke taal voor iedereen.",
    "tab-url":            "Link Checker",
    "tab-email":          "E-mail Analyser",
    "tab-phone":          "Telefoon Checker",
    "tab-guide":          "Veiligheids Gids",
    "url-placeholder":    "Plak hier een link, bijv. https://rnicrosoft.com",
    "email-placeholder":  "Plak hier de tekst van de e-mail...",
    "phone-placeholder":  "Plak hier een telefoonnummer, bijv. +32 0909 12345",
    "btn-scan":           "Controleer",
    "btn-analyse":        "Analyseer",
    "btn-check":          "Controleer",
    "sender-label":       "Afzender (optioneel):",
    "url-examples-label": "Voorbeelden om te proberen:",
    "phone-examples-label":"Voorbeelden om te proberen:",
    "chip-safe":          "google.com (veilig)",
    "chip-typo":          "rnicrosoft.com (nep domein)",
    "chip-phish":         "paypal-login-secure (oplichting)",
    "chip-short":         "bit.ly (verborgen link)",
    "chip-phone-safe":    "+32 2 123 45 67 (veilig)",
    "chip-phone-prem":    "+32 0909 (betalend nummer)",
    "chip-phone-scam":    "+1 876 Jamaica (callback oplichting)",
    "load-phish-en":      "Laad oplichting voorbeeld",
    "load-phish-nl":      "Laad Nederlands oplichting voorbeeld",
    "load-legit":         "Laad normale e-mail",
    "text-size":          "Tekst",
    "flagged-title":      "Waarom werd dit gemarkeerd?",
    "no-flags":           "Geen verdachte signalen gevonden.",
    "tech-details":       "Technische details",
    "hide-details":       "Verberg details",
    "verdict-high":       "Wij denken dat dit een oplichting is.",
    "verdict-medium":     "Dit ziet er verdacht uit. Wees voorzichtig.",
    "verdict-low":        "Dit lijkt veilig.",
    "guide-links-title":  "Hoe herken je een neplink",
    "guide-link-1":       "<strong>Bekijk de domeinnaam goed.</strong> Oplichters maken adressen die bijna identiek zijn aan echte websites.",
    "guide-link-2":       "<strong>Let op https:// aan het begin.</strong> Een link die begint met http:// (zonder de s) is minder veilig.",
    "guide-link-3":       "<strong>Korte links verbergen het echte adres.</strong> Links zoals bit.ly/abc123 laten niet zien waar ze echt naartoe gaan.",
    "guide-link-4":       "<strong>Beweeg je muis over de link voor je klikt.</strong> Het echte adres verschijnt dan onderaan je scherm.",
    "guide-email-title":  "Hoe herken je een oplichtingsmail",
    "guide-email-1":      "<strong>'Handel nu' is een waarschuwing.</strong> Zinnen zoals 'Uw account wordt binnen 24 uur geblokkeerd' zijn bedoeld om u in paniek te brengen.",
    "guide-email-2":      "<strong>Echte organisaties vragen nooit uw wachtwoord via e-mail.</strong> Banken en overheidsdiensten vragen nooit uw pincode via e-mail.",
    "guide-email-3":      "<strong>Controleer wie de mail echt stuurde.</strong> De naam kan 'ING Bank' zeggen maar het echte adres kan zoiets zijn als ing@nep-domein.ru.",
    "guide-email-4":      "<strong>Vriendelijke mails die om geld vragen zijn ook oplichting.</strong> Sommige oplichtingsmails zijn heel beleefd. Ze beloven een deel van een groot bedrag. Altijd oplichting.",
    "guide-419-example":  "Voorbeeld: \"Beste vriend, ik weet dat dit bericht u zal verrassen maar ik heb uw hulp nodig om geld over te maken...\"",
    "guide-phone-title":  "Hoe herken je een frauduleus telefoonnummer",
    "guide-phone-1":      "<strong>Nummers die beginnen met 0900 kosten geld om te bellen.</strong> Dit kan meerdere euro's per minuut kosten. Echte organisaties vragen u dit nooit.",
    "guide-phone-2":      "<strong>Bel geen onbekende buitenlandse nummers terug.</strong> Nummers uit het Caribisch gebied (+1 473, +1 876) worden vaak gebruikt voor callback-oplichting.",
    "guide-phone-3":      "<strong>Uw bank zal u nooit vragen een nummer uit een sms te bellen.</strong> Zoek altijd zelf het officiële nummer op - kijk op de achterkant van uw bankkaart.",
    "quiz-title":         "Snelle quiz",
    "quiz-intro":         "Kunt u de oplichting herkennen? Elke keer nieuwe vragen als u reset.",
    "quiz-reset":         "Probeer nieuwe vragen",
    "card1-title":        "Voor wie is dit?",
    "card1-body":         "Oudere gebruikers, vluchtelingen en mensen met beperkte digitale vaardigheden - het meest kwetsbaar voor online oplichting.",
    "card2-title":        "Hoe het werkt",
    "card2-body":         "AI-modellen detecteren oplichtingspatronen. Elk resultaat wordt uitgelegd in begrijpelijke taal - geen technische kennis nodig.",
    "card3-title":        "SDG 10",
    "card3-body":         "Digitale veiligheid mag niet afhangen van technische kennis. Iedereen verdient bescherming online.",
    "card4-title":        "Privacy",
    "card4-body":         "Niets wordt opgeslagen. Geen tracking. Draait op uw computer. Gratis en open source.",
  }
};

// ── Quiz question pool ────────────────────────────────────────────────────────
const QUIZ_POOL = {
  en: [
    {
      q: "You receive this email subject line:",
      example: '"URGENT: Your ING account has been suspended - verify NOW at ing-account-secure.com"',
      options: ["Real - ING sent this", "Scam - this is phishing"],
      correct: 1,
      feedback: {
        correct: "Correct. Two red flags: urgency pressure and the domain is ing-account-secure.com instead of ing.be or ing.nl.",
        wrong: "Not quite. This is phishing. The domain 'ing-account-secure.com' is fake, and real banks never demand you act within hours."
      }
    },
    {
      q: "Which link is safer to click?",
      example: null,
      options: ["http://bit.ly/yourpackage", "https://www.postnl.nl/track-trace"],
      correct: 1,
      feedback: {
        correct: "Correct. The PostNL link is on the real official domain with HTTPS. The bit.ly link hides where it actually goes.",
        wrong: "Not quite. The bit.ly link hides the real destination - always avoid short links in unexpected messages."
      }
    },
    {
      q: "You get a voicemail asking you to call +1 876 555 0199 urgently. You should:",
      example: null,
      options: ["Call back immediately", "Look up the organisation's official number and call that instead"],
      correct: 1,
      feedback: {
        correct: "Correct. +1 876 is Jamaica, commonly used in callback scams. Always find the official number yourself.",
        wrong: "Not quite. +1 876 is a country code linked to callback scams. Never call back unknown numbers - find the official number instead."
      }
    },
    {
      q: "An email says: 'Dear Friend, I have USD 15 million to transfer and need a trusted person. I will give you 30%.'",
      example: null,
      options: ["This could be real", "This is an advance fee scam"],
      correct: 1,
      feedback: {
        correct: "Correct. This is classic advance fee fraud ('Nigerian prince' scam). No one will give you 30% of millions.",
        wrong: "This is advance fee fraud. The polite, unhurried tone is deliberate - these scams ask for fees upfront and deliver nothing."
      }
    },
    {
      q: "A text from 'your bank' asks you to call 0900-1234 to verify your account. You should:",
      example: null,
      options: ["Call 0900-1234 immediately", "Ignore the text and call the number on your bank card"],
      correct: 1,
      feedback: {
        correct: "Correct. 0900 numbers are premium rate and your real bank will never ask you to call one. Use the number on your card.",
        wrong: "0900 numbers cost money per minute, and your real bank never asks you to call one. Always use the official number from your bank card."
      }
    },
    {
      q: "An email from 'PayPal Support' asks you to confirm your password and credit card number to avoid suspension.",
      example: '"support@paypa1-secure.com"',
      options: ["This is legitimate - PayPal needs to verify you", "This is phishing - check the sender address"],
      correct: 1,
      feedback: {
        correct: "Correct. The sender address 'paypa1-secure.com' uses a number 1 instead of the letter l, and real PayPal never asks for your password by email.",
        wrong: "This is phishing. Look closely at the sender: paypa1-secure.com - that's a fake domain. PayPal never asks for passwords by email."
      }
    },
  ],
  nl: [
    {
      q: "U ontvangt dit onderwerp in een e-mail:",
      example: '"DRINGEND: Uw ING-rekening is geblokkeerd - verifieer NU op ing-account-secure.com"',
      options: ["Echt - ING stuurde dit", "Oplichting - dit is phishing"],
      correct: 1,
      feedback: {
        correct: "Correct. Twee waarschuwingstekens: drukuitoefening en het domein is ing-account-secure.com in plaats van ing.be of ing.nl.",
        wrong: "Niet helemaal. Dit is phishing. Het domein 'ing-account-secure.com' is nep, en echte banken vragen u nooit om binnen uren te handelen."
      }
    },
    {
      q: "Welke link is veiliger om op te klikken?",
      example: null,
      options: ["http://bit.ly/uwpakket", "https://www.postnl.nl/track-trace"],
      correct: 1,
      feedback: {
        correct: "Correct. De PostNL link staat op het echte officiële domein met HTTPS. De bit.ly link verbergt waar hij echt naartoe gaat.",
        wrong: "Niet helemaal. De bit.ly link verbergt de echte bestemming - wees altijd voorzichtig met korte links in onverwachte berichten."
      }
    },
    {
      q: "U ontvangt een voicemail om dringend +1 876 555 0199 te bellen. Wat doet u?",
      example: null,
      options: ["Direct terugbellen", "Zelf het officiële nummer opzoeken en dat bellen"],
      correct: 1,
      feedback: {
        correct: "Correct. +1 876 is Jamaica, vaak gebruikt bij callback-oplichting. Zoek altijd zelf het officiële nummer op.",
        wrong: "Niet helemaal. +1 876 is een landnummer gelinkt aan callback-oplichting. Bel nooit onbekende nummers terug."
      }
    },
    {
      q: "Een e-mail zegt: 'Beste vriend, ik heb 15 miljoen dollar te overmaken en zoek een betrouwbaar persoon. U krijgt 30%.'",
      example: null,
      options: ["Dit zou echt kunnen zijn", "Dit is voorschotfraude (oplichting)"],
      correct: 1,
      feedback: {
        correct: "Correct. Dit is klassieke voorschotfraude. Niemand geeft zomaar 30% van miljoenen weg.",
        wrong: "Dit is voorschotfraude. De beleefde, ongeduldige toon is opzettelijk - deze oplichters vragen later om vooruitbetalingen."
      }
    },
    {
      q: "Een sms van 'uw bank' vraagt u 0900-1234 te bellen om uw rekening te verifiëren. Wat doet u?",
      example: null,
      options: ["0900-1234 meteen bellen", "De sms negeren en het nummer op uw bankkaart bellen"],
      correct: 1,
      feedback: {
        correct: "Correct. 0900-nummers zijn betalend en uw echte bank vraagt u dit nooit. Gebruik het nummer op uw bankkaart.",
        wrong: "0900-nummers kosten geld per minuut, en uw echte bank vraagt u dit nooit. Gebruik altijd het officiële nummer van uw bankkaart."
      }
    },
    {
      q: "Een e-mail van 'PayPal Klantenservice' vraagt uw wachtwoord en creditcardnummer te bevestigen.",
      example: '"support@paypa1-secure.com"',
      options: ["Dit is legitiem - PayPal moet u verifiëren", "Dit is phishing - kijk naar het afzenderadres"],
      correct: 1,
      feedback: {
        correct: "Correct. Het adres 'paypa1-secure.com' gebruikt een cijfer 1 in plaats van de letter l, en PayPal vraagt nooit uw wachtwoord per e-mail.",
        wrong: "Dit is phishing. Kijk goed naar de afzender: paypa1-secure.com - dat is een nep-domein. PayPal vraagt nooit wachtwoorden per e-mail."
      }
    },
  ]
};

// ── App state ─────────────────────────────────────────────────────────────────
let currentLang = 'en';
let fontSize = 16;
let quizQuestions = [];
let quizAnswered = 0;
let quizCorrect = 0;

// ── Language & font size ──────────────────────────────────────────────────────
function setLang(lang) {
  currentLang = lang;
  document.getElementById('btn-en').classList.toggle('active', lang === 'en');
  document.getElementById('btn-nl').classList.toggle('active', lang === 'nl');
  applyTranslations();
  initQuiz();
}

function applyTranslations() {
  const t = T[currentLang];
  document.querySelectorAll('[data-t]').forEach(el => {
    const key = el.getAttribute('data-t');
    if (t[key] !== undefined) el.innerHTML = t[key];
  });
  document.querySelectorAll('[data-placeholder-t]').forEach(el => {
    const key = el.getAttribute('data-placeholder-t');
    if (t[key] !== undefined) el.placeholder = t[key];
  });
}

function changeSize(delta) {
  fontSize = Math.max(13, Math.min(22, fontSize + delta));
  document.documentElement.style.setProperty('--base-size', fontSize + 'px');
}

// ── Quiz ──────────────────────────────────────────────────────────────────────
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function initQuiz() {
  const pool = QUIZ_POOL[currentLang] || QUIZ_POOL.en;
  quizQuestions = shuffle(pool).slice(0, 3);
  quizAnswered = 0;
  quizCorrect = 0;
  document.getElementById('quiz-score').textContent = '';
  renderQuiz();
}

function renderQuiz() {
  const container = document.getElementById('quiz-container');
  container.innerHTML = quizQuestions.map((q, i) => `
    <div class="quiz-q" id="qq-${i}">
      <div class="quiz-text">${i + 1}. ${q.q}</div>
      ${q.example ? `<div class="quiz-example">${q.example}</div>` : ''}
      <div class="quiz-options">
        ${q.options.map((opt, j) => `
          <button class="quiz-btn" id="qb-${i}-${j}" onclick="answerQuiz(${i},${j})">${opt}</button>
        `).join('')}
      </div>
      <div class="quiz-feedback" id="qf-${i}"></div>
    </div>
  `).join('');
}

function answerQuiz(qIdx, aIdx) {
  const q = quizQuestions[qIdx];
  const isCorrect = aIdx === q.correct;
  if (isCorrect) quizCorrect++;
  quizAnswered++;

  // Disable all buttons for this question
  q.options.forEach((_, j) => {
    const btn = document.getElementById(`qb-${qIdx}-${j}`);
    btn.disabled = true;
    if (j === q.correct) btn.classList.add('correct-answer');
    else if (j === aIdx && !isCorrect) btn.classList.add('wrong-answer');
  });

  // Show feedback
  const fb = document.getElementById(`qf-${qIdx}`);
  fb.className = 'quiz-feedback ' + (isCorrect ? 'correct' : 'wrong');
  fb.textContent = isCorrect ? q.feedback.correct : q.feedback.wrong;
  fb.style.display = 'block';

  // Show score when all answered
  if (quizAnswered === quizQuestions.length) {
    const scoreEl = document.getElementById('quiz-score');
    const lang = currentLang;
    scoreEl.textContent = lang === 'nl'
      ? `Score: ${quizCorrect} van ${quizQuestions.length} correct`
      : `Score: ${quizCorrect} out of ${quizQuestions.length} correct`;
  }
}

// ── Tab switching ─────────────────────────────────────────────────────────────
function sw(tab, btn) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('p-' + tab).classList.add('active');
  btn.classList.add('active');
  document.getElementById('bottom-cards').style.display = tab === 'guide' ? 'none' : '';
}

// ── Input helpers ─────────────────────────────────────────────────────────────
function su(u) { document.getElementById('urlI').value = u; }
function sp(n) { document.getElementById('phI').value = n; }

const PE  = `Dear Valued Customer,\n\nWe have detected UNUSUAL ACTIVITY on your account. It will be SUSPENDED within 24 hours!!!\n\nClick here to verify NOW: http://paypal-login-secure.com/verify?user=you\n\nEnter your password and credit card number to restore access.\n\nAct NOW - this is your FINAL WARNING!\n\nPayPal Security Team`;
const NLP = `Geachte klant,\n\nWe hebben ONGEWONE ACTIVITEIT op uw rekening gedetecteerd. Uw account wordt binnen 24 uur GEBLOKKEERD!!!\n\nKlik hier om uw gegevens te bevestigen: http://ing-beveiliging-update.com/inloggen\n\nVoer uw wachtwoord en bankrekeningnummer in om toegang te herstellen.\n\nHandel NU - dit is uw LAATSTE WAARSCHUWING!\n\nING Beveiligingsteam`;
const LE  = `Dear John,\n\nThank you for your order #12345. Your package has been dispatched and will arrive on 10 March 2026.\n\nTrack your delivery: https://www.postnl.nl/track-trace\n\nQuestions? Email support@bol.com or call +31 10 230 00 10.\n\nKind regards,\nbol.com Customer Service`;

function lse(p) {
  if (p === 1) { document.getElementById('emlI').value = PE;  document.getElementById('sndI').value = 'security@paypa1.com'; }
  else if (p === 2) { document.getElementById('emlI').value = NLP; document.getElementById('sndI').value = 'beveiliging@ing-update.com'; }
  else { document.getElementById('emlI').value = LE; document.getElementById('sndI').value = 'support@bol.com'; }
}

// ── Result rendering ──────────────────────────────────────────────────────────
function ld(t, s, b, on) {
  document.getElementById(t).style.display = on ? 'none' : 'inline';
  document.getElementById(s).style.display = on ? 'block' : 'none';
  document.getElementById(b).disabled = on;
}

function trafficLight(risk) {
  const dots = {
    high:   '<div class="tl-dot tl-red active"></div><div class="tl-dot tl-orange"></div><div class="tl-dot tl-green"></div>',
    medium: '<div class="tl-dot tl-red"></div><div class="tl-dot tl-orange active"></div><div class="tl-dot tl-green"></div>',
    low:    '<div class="tl-dot tl-red"></div><div class="tl-dot tl-orange"></div><div class="tl-dot tl-green active"></div>',
  };
  return `<div class="traffic-light">${dots[risk] || dots.low}</div>`;
}

function render(cid, d) {
  const c = document.getElementById(cid);
  c.className = 'result risk-' + d.risk_level;
  c.style.display = 'block';

  const lang = d.language || currentLang;
  const t = T[lang] || T.en;
  const sub = d.url || d.number || (d.sender ? (lang === 'nl' ? 'Van: ' : 'From: ') + d.sender : (lang === 'nl' ? 'E-mail geanalyseerd' : 'Email analysed'));

  const flagsHtml = (d.flags && d.flags.length > 0)
    ? d.flags.map(f => typeof f === 'string'
        ? `<div class="flag">${f}</div>`
        : `<div class="flag"><span class="fcat">${f.category}:</span> ${f.detail}</div>`
      ).join('')
    : `<div class="noflag">${t['no-flags']}</div>`;

  const dtRows = d.features
    ? Object.entries(d.features).map(([k, v]) => `<tr><td>${k.replace(/_/g, ' ')}</td><td>${v}</td></tr>`).join('')
    : '';
  const dtHtml = dtRows
    ? `<button class="dtbtn" onclick="toggleDt('${cid}')">${t['tech-details']}</button><div class="dtsec" id="${cid}-dt"><table><thead><tr><th>Feature</th><th>Value</th></tr></thead><tbody>${dtRows}</tbody></table></div>`
    : '';

  c.innerHTML = `
    <div class="risk-title">${d.risk_label}</div>
    <div class="risk-sub">${sub}</div>
    ${trafficLight(d.risk_level)}
    <div class="verdict ${d.risk_level}">${t['verdict-' + d.risk_level] || d.risk_label}</div>
    <div class="expl">${d.explanation}</div>
    <div class="ftitle">${t['flagged-title']}</div>
    ${flagsHtml}
    ${dtHtml}
    ${d.model_used ? `<div class="mbadge">${d.model_used}</div>` : ''}`;

  c.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function toggleDt(cid) {
  const d = document.getElementById(cid + '-dt');
  const b = d.previousElementSibling;
  const open = d.style.display === 'block';
  d.style.display = open ? 'none' : 'block';
  b.textContent = open ? T[currentLang]['tech-details'] : T[currentLang]['hide-details'];
}

// ── API calls ─────────────────────────────────────────────────────────────────
async function post(url, body) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}
async function scanUrl() {
  const v = document.getElementById('urlI').value.trim(); if (!v) return;
  ld('urlT', 'urlS', 'urlB', true);
  try { const d = await post('/predict/url', { url: v }); d.error ? alert(d.error) : render('r-url', d); }
  catch (e) { alert('Cannot connect to server.'); }
  finally { ld('urlT', 'urlS', 'urlB', false); }
}
async function scanEmail() {
  const v = document.getElementById('emlI').value.trim(); if (!v) return;
  ld('emlT', 'emlS', 'emlB', true);
  try { const d = await post('/predict/email', { text: v, sender: document.getElementById('sndI').value.trim() }); d.error ? alert(d.error) : render('r-email', d); }
  catch (e) { alert('Cannot connect to server.'); }
  finally { ld('emlT', 'emlS', 'emlB', false); }
}
async function scanPhone() {
  const v = document.getElementById('phI').value.trim(); if (!v) return;
  ld('phT', 'phS', 'phB', true);
  try { const d = await post('/predict/phone', { number: v }); d.error ? alert(d.error) : render('r-phone', d); }
  catch (e) { alert('Cannot connect to server.'); }
  finally { ld('phT', 'phS', 'phB', false); }
}

// ── Init ──────────────────────────────────────────────────────────────────────
applyTranslations();
initQuiz();
</script>
</body></html>"""


@app.route("/")
def index():
    return render_template_string(INLINE_HTML)


@app.route("/predict/url", methods=["POST"])
def pred_url():
    d = request.get_json()
    if not d or not d.get("url", "").strip():
        return jsonify({"error": "No URL provided"}), 400
    try:
        return jsonify(predict(d["url"].strip()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict/email", methods=["POST"])
def pred_email():
    d = request.get_json()
    if not d or not d.get("text", "").strip():
        return jsonify({"error": "No email text provided"}), 400
    try:
        return jsonify(analyze_email(d["text"].strip(), d.get("sender", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict/phone", methods=["POST"])
def pred_phone():
    d = request.get_json()
    if not d or not d.get("number", "").strip():
        return jsonify({"error": "No phone number provided"}), 400
    try:
        return jsonify(check_phone(d["number"].strip()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("\nArcticSecurityShield - starting on http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
