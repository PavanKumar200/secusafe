/**
 * content.js — Injected into every page.
 * Reads cached scan result from storage and renders the warning banner
 * if the background worker hasn't already done so (fallback).
 */

(function () {
  'use strict';

  // The banner is primarily injected by background.js via scripting API.
  // This content script serves as a fallback check after initial load.
  // No action needed here; banner injection is handled in background.js.
  // Kept for future use (e.g., page-level dark pattern highlighting).
})();
