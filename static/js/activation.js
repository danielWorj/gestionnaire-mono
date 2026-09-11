/**
 * static/js/activation.js
 * ========================
 * Frontend de l'écran de verrouillage / activation de licence.
 *
 * Ce script ne contient AUCUNE logique de sécurité : toute la vérification
 * (signature ECDSA, HWID, expiration, anti-recul d'horloge) est faite côté
 * Flask dans `licensing/`. Ce fichier se contente :
 *   1. d'interroger GET  /api/license/status  au chargement pour savoir s'il
 *      faut afficher l'application ou l'écran de blocage ;
 *   2. d'envoyer POST /api/activate avec la clé saisie/collée par le
 *      proviseur, et d'afficher le message d'erreur correspondant ;
 *   3. d'appeler GET /api/license/challenge et de générer le QR code du
 *      "code d'installation" (100% hors-ligne, via static/js/lib/qrcode.min.js).
 *
 * Contrat DOM attendu (à placer dans le template de l'écran de blocage,
 * ex: static/templates/verrouillage.html) :
 *
 *   <div id="lock-screen" hidden>
 *     <p id="lock-message"></p>
 *
 *     <form id="activation-form">
 *       <textarea id="license-key-input" placeholder="Collez la clé de licence (Base64)"></textarea>
 *       <input type="file" id="license-key-file" accept=".lic,.txt,.json" />
 *       <button type="submit" id="activation-submit">Activer</button>
 *       <p id="activation-error" class="error" hidden></p>
 *     </form>
 *
 *     <section id="challenge-block">
 *       <p>Code d'installation : <strong id="installation-code">----</strong></p>
 *       <div id="qrcode-container"></div>
 *       <button type="button" id="refresh-challenge">Actualiser</button>
 *     </section>
 *   </div>
 *
 *   <div id="app-root" hidden> ... reste de l'application ... </div>
 *
 * Ordre de chargement des scripts (100% local, pas de CDN) :
 *   <script src="/static/js/lib/qrcode.min.js"></script>
 *   <script src="/static/js/activation.js"></script>
 */

(function () {
  'use strict';

  // ------------------------------------------------------------------
  // Config
  // ------------------------------------------------------------------

  const ENDPOINTS = {
    activate: '/api/activate',
    status: '/api/license/status',
    challenge: '/api/license/challenge',
  };

  // Traduction des statuts renvoyés par licensing/license_manager.py en
  // messages compréhensibles par le proviseur. Garde les clés synchronisées
  // avec licensing/license_manager.py (STATUS_*).
  const STATUS_MESSAGES = {
    invalid: "Clé de licence invalide : le fichier est corrompu ou la signature ne correspond pas.",
    hwid_mismatch: "Cette licence a été générée pour un autre ordinateur. Utilisez le code d'installation ci-dessous pour en demander une nouvelle.",
    expired: "L'abonnement de cette licence est arrivé à échéance. Contactez l'administrateur pour la renouveler.",
    no_license: "Aucune licence n'est installée sur cet ordinateur.",
    clock_rollback_detected: "L'horloge de cet ordinateur a été modifiée de façon anormale. L'application reste bloquée ; contactez l'administrateur.",
  };

  const DEFAULT_ERROR_MESSAGE = "Une erreur inattendue est survenue. Réessayez ou contactez l'administrateur.";

  // ------------------------------------------------------------------
  // Références DOM (résolues au DOMContentLoaded ; certaines peuvent être
  // absentes selon la page, d'où les vérifications avant usage)
  // ------------------------------------------------------------------

  let els = {};

  function cacheDom() {
    els = {
      lockScreen: document.getElementById('lock-screen'),
      lockMessage: document.getElementById('lock-message'),
      appRoot: document.getElementById('app-root'),

      form: document.getElementById('activation-form'),
      keyInput: document.getElementById('license-key-input'),
      keyFile: document.getElementById('license-key-file'),
      submitBtn: document.getElementById('activation-submit'),
      errorBox: document.getElementById('activation-error'),

      challengeBlock: document.getElementById('challenge-block'),
      installationCode: document.getElementById('installation-code'),
      qrContainer: document.getElementById('qrcode-container'),
      refreshChallengeBtn: document.getElementById('refresh-challenge'),
    };
  }

  // ------------------------------------------------------------------
  // Helpers UI
  // ------------------------------------------------------------------

  function showError(message) {
    if (!els.errorBox) return;
    els.errorBox.textContent = message || DEFAULT_ERROR_MESSAGE;
    els.errorBox.hidden = false;
  }

  function clearError() {
    if (!els.errorBox) return;
    els.errorBox.textContent = '';
    els.errorBox.hidden = true;
  }

  function setSubmitting(isSubmitting) {
    if (!els.submitBtn) return;
    els.submitBtn.disabled = isSubmitting;
    els.submitBtn.textContent = isSubmitting ? 'Vérification…' : 'Activer';
  }

  function showLockScreen(statusKey, message) {
    if (els.appRoot) els.appRoot.hidden = true;
    if (els.lockScreen) els.lockScreen.hidden = false;
    if (els.lockMessage) {
      els.lockMessage.textContent = message || STATUS_MESSAGES[statusKey] || DEFAULT_ERROR_MESSAGE;
    }
    // On ne montre le bloc "code d'installation / QR" que dans les cas où
    // il est réellement utile (pas de licence, ou mauvaise machine) : sur
    // une clé simplement invalide/malformée, le proviseur doit d'abord
    // réessayer de coller/saisir la bonne clé.
    const needsChallenge = statusKey === 'no_license' || statusKey === 'hwid_mismatch';
    if (els.challengeBlock) {
      els.challengeBlock.hidden = !needsChallenge;
    }
    if (needsChallenge) {
      loadChallenge();
    }
  }

  function showApp() {
    if (els.lockScreen) els.lockScreen.hidden = true;
    if (els.appRoot) els.appRoot.hidden = false;
  }

  // ------------------------------------------------------------------
  // Appel réseau générique (JSON in / JSON out)
  // ------------------------------------------------------------------

  async function callJson(url, options) {
    let response;
    try {
      response = await fetch(url, options);
    } catch (networkError) {
      // Flask tourne en local (127.0.0.1) : une erreur ici signifie
      // généralement que le serveur n'est pas démarré, pas un problème
      // de connectivité internet (l'app est conçue pour être hors-ligne).
      throw new Error("Impossible de contacter le serveur local. Vérifiez que l'application est bien démarrée.");
    }

    let body = null;
    try {
      body = await response.json();
    } catch (_parseError) {
      body = null;
    }

    return { ok: response.ok, httpStatus: response.status, body };
  }

  // ------------------------------------------------------------------
  // 1. Statut courant au chargement de la page
  // ------------------------------------------------------------------

  async function checkLicenseStatus() {
    try {
      const { body } = await callJson(ENDPOINTS.status, { method: 'GET' });
      if (!body) {
        showLockScreen('invalid', DEFAULT_ERROR_MESSAGE);
        return;
      }
      if (body.success && body.status === 'valid') {
        showApp();
        return;
      }
      showLockScreen(body.status, body.message);
    } catch (err) {
      showLockScreen('invalid', err.message);
    }
  }

  // ------------------------------------------------------------------
  // 2. Soumission du formulaire d'activation
  // ------------------------------------------------------------------

  function readKeyFromFileInput() {
    if (!els.keyFile || !els.keyFile.files || els.keyFile.files.length === 0) {
      return Promise.resolve(null);
    }
    const file = els.keyFile.files[0];
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || '').trim());
      reader.onerror = () => reject(new Error("Impossible de lire le fichier de licence."));
      reader.readAsText(file);
    });
  }

  async function handleActivateSubmit(event) {
    event.preventDefault();
    clearError();

    let licenseKey = (els.keyInput && els.keyInput.value || '').trim();

    // Le fichier (si fourni) a priorité sur le texte collé.
    try {
      const fromFile = await readKeyFromFileInput();
      if (fromFile) licenseKey = fromFile;
    } catch (fileErr) {
      showError(fileErr.message);
      return;
    }

    if (!licenseKey) {
      showError("Collez la clé de licence ou sélectionnez le fichier fourni par l'administrateur.");
      return;
    }

    setSubmitting(true);
    try {
      const { body } = await callJson(ENDPOINTS.activate, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ license_key: licenseKey }),
      });

      if (!body) {
        showError(DEFAULT_ERROR_MESSAGE);
        return;
      }

      if (body.success && body.status === 'valid') {
        // Licence acceptée : on recharge pour repasser par
        // checkLicenseStatus() et laisser Flask/le middleware
        // re-évaluer proprement toutes les routes protégées.
        window.location.reload();
        return;
      }

      // Échec "métier" (signature invalide, mauvaise machine, expirée…) :
      // on affiche le message renvoyé par Flask, avec repli sur notre
      // dictionnaire local si jamais Flask ne renvoie pas de message.
      const message = body.message || STATUS_MESSAGES[body.status] || DEFAULT_ERROR_MESSAGE;
      showError(message);

      // Si l'échec est dû à un mauvais HWID ou à une absence de licence,
      // on réaffiche/rafraîchit le code d'installation pour que le
      // proviseur puisse immédiatement demander la bonne clé.
      if (body.status === 'hwid_mismatch' || body.status === 'no_license') {
        if (els.challengeBlock) els.challengeBlock.hidden = false;
        loadChallenge();
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  // ------------------------------------------------------------------
  // 3. Code d'installation (HWID) + QR code, pour le dépannage/renouvellement
  // ------------------------------------------------------------------

  async function loadChallenge() {
    if (!els.installationCode && !els.qrContainer) return; // rien à afficher

    try {
      const { body } = await callJson(ENDPOINTS.challenge, { method: 'GET' });
      if (!body || !body.success) {
        if (els.installationCode) els.installationCode.textContent = '----';
        return;
      }

      if (els.installationCode) {
        els.installationCode.textContent = body.installation_code;
      }
      renderQrCode(body.installation_code);
    } catch (_err) {
      // Le code d'installation n'est qu'un confort (le HWID reste lisible
      // en gros caractères) : on échoue silencieusement plutôt que de
      // bloquer l'écran d'activation avec une deuxième erreur réseau.
      if (els.installationCode) els.installationCode.textContent = '----';
    }
  }

  function renderQrCode(text) {
    if (!els.qrContainer) return;
    els.qrContainer.innerHTML = '';

    // `QRCode` est fourni par static/js/lib/qrcode.min.js (vendoré, pas de
    // CDN — l'app doit fonctionner 100% hors-ligne). API classique du
    // paquet "davidshimjs/qrcodejs" :
    //   new QRCode(domElement, { text, width, height, correctLevel });
    if (typeof QRCode === 'undefined') {
      // Librairie non chargée : on retombe sur le code en gros caractères
      // déjà affiché dans #installation-code, qui suffit pour la photo
      // WhatsApp décrite dans le protocole de dépannage.
      return;
    }

    // eslint-disable-next-line no-undef
    new QRCode(els.qrContainer, {
      text: text,
      width: 180,
      height: 180,
      correctLevel: QRCode.CorrectLevel.M,
    });
  }

  // ------------------------------------------------------------------
  // Init
  // ------------------------------------------------------------------

  function init() {
    cacheDom();

    if (els.form) {
      els.form.addEventListener('submit', handleActivateSubmit);
    }
    if (els.refreshChallengeBtn) {
      els.refreshChallengeBtn.addEventListener('click', loadChallenge);
    }

    checkLicenseStatus();
  }

  document.addEventListener('DOMContentLoaded', init);
})();