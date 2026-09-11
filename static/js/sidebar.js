(function () {
  "use strict";

  /* ═══════════════════════════════════════════════
     CONFIGURATION DU MENU
     Modifier ici pour ajouter / retirer des entrées.
     "key" correspond à la valeur de data-page="..."
  ════════════════════════════════════════════════ */
  const MENU = [
    /* ── Pédagogie : structure et paramétrage de l'établissement ── */
    {
      section: "Pédagogie",
      items: [
        {
          key: "config",
          label: "Configuration",
          icon: "fa-sliders",
          href: "/config",
        },
        {
          key: "enseignant",
          label: "Enseignants",
          icon: "fa-chalkboard-user",
          href: "/enseignant",
        },
        {
          key: "matiere",
          label: "Matières",
          icon: "fa-book",
          href: "/matiere",
        },
        {
          key: "horaire",
          label: "Emploi du temps",
          icon: "fa-calendar-days",
          href: "/horaire",
        },
      ],
    },

    /* ── Scolarité : gestion des acteurs (élèves, parents, inscriptions) ── */
    {
      section: "Scolarité",
      items: [
        {
          key: "inscription",
          label: "Inscriptions",
          icon: "fa-file-signature",
          href: "/inscription",
        },
        {
          key: "eleve",
          label: "Élèves",
          icon: "fa-user-graduate",
          href: "/eleve",
        },
        {
          key: "parent",
          label: "Parents",
          icon: "fa-people-roof",
          href: "/parent",
        },
      ],
    },

    /* ── Suivi & Finances : évaluations et flux financiers ── */
    {
      section: "Suivi & Finances",
      items: [
        {
          key: "evaluation",
          label: "Évaluations",
          icon: "fa-clipboard-check",
          href: "/evaluation",
        },
        {
          key: "paiements",
          label: "Paiements",
          icon: "fa-money-bill-wave",
          href: "/paiements",
        },
        {
          key: "finances",
          label: "Finances",
          icon: "fa-chart-pie",
          href: "/finances",
        },
      ],
    },
  ];

  /* ═══════════════════════════════════════════════
     HELPERS
  ════════════════════════════════════════════════ */

  const ACTIVE_KEY_STORAGE = "gestionnaire_active_page";

  /**
   * Retourne la page active.
   * Priorité : data-page sur <body>/<main> (source de vérité côté serveur).
   * Si absent, on retombe sur la dernière rubrique cliquée (sessionStorage),
   * ce qui évite que le lien perde son état "actif" sur des pages qui
   * n'auraient pas encore été mises à jour avec l'attribut data-page.
   */
  function getActivePage() {
    const fromDom =
      document.body.dataset.page ||
      document.querySelector("main")?.dataset.page ||
      "";
    if (fromDom) return fromDom;

    try {
      return sessionStorage.getItem(ACTIVE_KEY_STORAGE) || "";
    } catch (e) {
      return "";
    }
  }

  /** Construit le HTML d'un lien de sous-menu. */
  function buildSubmenuItem(sub, activePage) {
    const isActive = activePage === sub.key ? " active" : "";
    return `<li class="nav-item">
      <a class="nav-link${isActive}" href="${sub.href}" data-key="${sub.key}">${sub.label}</a>
    </li>`;
  }

  /** Construit le HTML d'un item de menu (avec ou sans sous-menu). */
  function buildMenuItem(item, activePage) {
    const hasSubmenu = item.submenu && item.submenu.length > 0;

    /* Vérifier si l'item ou l'un de ses enfants est actif */
    const isSelfActive = activePage === item.key;
    const isChildActive =
      hasSubmenu && item.submenu.some((s) => s.key === activePage);
    const isActive = isSelfActive || isChildActive;

    const activeClass = isActive ? " active" : "";
    const expandedAttr = isActive && hasSubmenu ? ' aria-expanded="true"' : ' aria-expanded="false"';

    /* Badge optionnel */
    const badgeHtml = item.badge
      ? `<span class="nav-badge">${item.badge}</span>`
      : "";

    /* Chevron pour les sous-menus */
    const chevronHtml = hasSubmenu
      ? `<i class="fa-solid fa-chevron-down nav-chevron"></i>`
      : "";

    if (!hasSubmenu) {
      return `<li class="nav-item">
        <a class="nav-link${activeClass}" href="${item.href}" data-key="${item.key}">
          <span class="nav-icon"><i class="fa-solid ${item.icon}"></i></span>
          <span class="nav-label">${item.label}</span>
          ${badgeHtml}
        </a>
      </li>`;
    }

    /* Avec sous-menu */
    const submenuId = `submenu-${item.key}`;
    const submenuShow = isActive ? " show" : "";
    const submenuHtml = item.submenu.map((s) => buildSubmenuItem(s, activePage)).join("");

    return `<li class="nav-item">
      <button class="nav-link${activeClass}" ${expandedAttr}
              data-submenu="${submenuId}" type="button">
        <span class="nav-icon"><i class="fa-solid ${item.icon}"></i></span>
        <span class="nav-label">${item.label}</span>
        ${badgeHtml}
        ${chevronHtml}
      </button>
      <ul class="nav-submenu${submenuShow}" id="${submenuId}">
        ${submenuHtml}
      </ul>
    </li>`;
  }

  /** Construit le HTML d'un groupe de menu (section + items). */
  function buildMenuGroup(group, activePage) {
    const sectionHtml = group.section
      ? `<li><p class="section-label">${group.section}</p></li>`
      : "";
    const itemsHtml = group.items.map((i) => buildMenuItem(i, activePage)).join("");
    return `${sectionHtml}${itemsHtml}`;
  }

  /** Construit l'avatar (img ou initiales). */
  function buildAvatar(user, cssClass, size) {
    if (user.avatar) {
      return `<img src="${user.avatar}" alt="${user.nom}"
               class="${cssClass}" width="${size}" height="${size}">`;
    }
    const initials = user.nom
      .split(" ")
      .slice(0, 2)
      .map((w) => w[0].toUpperCase())
      .join("");
    return `<div class="${cssClass} eleve-avatar-placeholder"
                 style="width:${size}px;height:${size}px;font-size:${Math.round(size * 0.36)}px;">
               ${initials}
             </div>`;
  }

  /* ═══════════════════════════════════════════════
     TEMPLATE HTML
  ════════════════════════════════════════════════ */

  function buildSidebarHTML() {
    const activePage = getActivePage();
    const user = window.GESTIONNAIRE_USER || { nom: "Utilisateur", role: "Admin" };

    const navHTML = MENU.map((g) => buildMenuGroup(g, activePage)).join("");
    const avatarHTML = buildAvatar(user, "sidebar-user-avatar", 34);

    return `
    <!-- ── Overlay mobile ── -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <!-- ── Sidebar ── -->
    <aside class="sidebar" id="appSidebar" role="navigation" aria-label="Menu principal">

      <!-- Logo -->
      <div class="sidebar-logo">
        <div style="
          width:32px;height:32px;
          background:var(--ta-primary);
          border-radius:var(--ta-radius-sm);
          display:flex;align-items:center;justify-content:center;
          flex-shrink:0;">
          <i class="fa-solid fa-graduation-cap" style="color:#fff;font-size:15px;"></i>
        </div>
        <span class="sidebar-logo-text">
          Gestionnaire<span>.</span>
        </span>
      </div>

      <!-- Zone de scroll / Navigation -->
      <div class="sidebar-scroll">
        <ul class="sidebar-nav">
          ${navHTML}
        </ul>
      </div>

      <!-- Pied de sidebar — utilisateur connecté -->
      <div class="sidebar-footer">
        <div class="sidebar-user">
          ${avatarHTML}
          <div class="sidebar-user-info">
            <div class="sidebar-user-name">${user.nom}</div>
            <div class="sidebar-user-role">${user.role}</div>
          </div>
          <a href="/deconnexion" title="Se déconnecter"
             style="margin-left:auto;color:var(--ta-text-light);font-size:14px;
                    transition:color var(--ta-transition);"
             onmouseover="this.style.color='var(--ta-danger)'"
             onmouseout="this.style.color='var(--ta-text-light)'">
            <i class="fa-solid fa-right-from-bracket"></i>
          </a>
        </div>
      </div>
    </aside>`;
  }

  /* ═══════════════════════════════════════════════
     TOPBAR — barre sticky (optionnelle, injectée si
     #mainContent ne contient pas déjà .topbar)
  ════════════════════════════════════════════════ */

  function buildTopbarHTML() {
    const user = window.GESTIONNAIRE_USER || { nom: "Utilisateur", role: "Admin" };
    const avatarHTML = buildAvatar(user, "topbar-avatar", 34);

    return `
    <header class="topbar" role="banner">
      <!-- Bouton toggle sidebar -->
      <button class="topbar-toggle" id="sidebarToggle"
              aria-label="Ouvrir/Fermer le menu" type="button">
        <i class="fa-solid fa-bars"></i>
      </button>

      <!-- Recherche rapide -->
      <div class="topbar-search">
        <div class="input-group input-group-sm">
          <span class="input-group-text">
            <i class="fa-solid fa-magnifying-glass" style="font-size:12px;"></i>
          </span>
          <input type="search" class="form-control"
                 placeholder="Rechercher un élève, une classe…"
                 aria-label="Recherche">
        </div>
      </div>

      <!-- Actions droite -->
      <div class="topbar-right">
        <!-- Notifications -->
        <button class="topbar-icon-btn" title="Notifications" type="button">
          <i class="fa-regular fa-bell"></i>
          <span class="topbar-badge"></span>
        </button>

        <!-- Aide -->
        <button class="topbar-icon-btn" title="Aide" type="button">
          <i class="fa-regular fa-circle-question"></i>
        </button>

        <!-- Séparateur -->
        <div style="width:1px;height:20px;background:var(--ta-border);margin:0 4px;"></div>

        <!-- Profil utilisateur -->
        ${avatarHTML}
        <div class="topbar-user-info">
          <span class="topbar-user-name">${user.nom}</span>
          <span class="topbar-user-role">${user.role}</span>
        </div>
      </div>
    </header>`;
  }

  /* ═══════════════════════════════════════════════
     INJECTION
  ════════════════════════════════════════════════ */

  function inject() {
    const wrapper = document.querySelector(".app-wrapper");
    if (!wrapper) {
      console.warn("[sidebar.js] Élément .app-wrapper introuvable. Le sidebar ne peut pas être injecté.");
      return;
    }

    /* Injecter sidebar + overlay avant le .main-content */
    const mainContent = wrapper.querySelector(".main-content") || wrapper.querySelector("#mainContent");
    wrapper.insertAdjacentHTML("afterbegin", buildSidebarHTML());

    /* Injecter la topbar si elle n'existe pas déjà */
    if (mainContent && !mainContent.querySelector(".topbar")) {
      mainContent.insertAdjacentHTML("afterbegin", buildTopbarHTML());
    }
  }

  /* ═══════════════════════════════════════════════
     COMPORTEMENTS INTERACTIFS
  ════════════════════════════════════════════════ */

  function bindEvents() {
    const sidebar  = document.getElementById("appSidebar");
    const overlay  = document.getElementById("sidebarOverlay");
    const toggle   = document.getElementById("sidebarToggle");
    const mainContent = document.querySelector(".main-content") || document.getElementById("mainContent");

    if (!sidebar) return;

    /* ── Ouvrir / Fermer le sidebar ── */
    function openSidebar() {
      sidebar.classList.add("sidebar-open");
      overlay.classList.add("show");
    }

    function closeSidebar() {
      sidebar.classList.remove("sidebar-open");
      overlay.classList.remove("show");
    }

    function isDesktop() {
      return window.innerWidth > 991;
    }

    /* Toggle sur desktop : masquer/afficher avec translation */
    function toggleDesktop() {
      const hidden = sidebar.classList.toggle("sidebar-hidden");
      if (mainContent) {
        mainContent.classList.toggle("sidebar-collapsed", hidden);
      }
    }

    if (toggle) {
      toggle.addEventListener("click", () => {
        if (isDesktop()) {
          toggleDesktop();
        } else {
          sidebar.classList.contains("sidebar-open") ? closeSidebar() : openSidebar();
        }
      });
    }

    if (overlay) {
      overlay.addEventListener("click", closeSidebar);
    }

    /* Fermer avec Échap */
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeSidebar();
    });

    /* ── Sous-menus ── */
    sidebar.querySelectorAll("[data-submenu]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.dataset.submenu;
        const submenu = document.getElementById(targetId);
        if (!submenu) return;

        const isOpen = submenu.classList.contains("show");

        /* Fermer tous les sous-menus ouverts */
        sidebar.querySelectorAll(".nav-submenu.show").forEach((el) => {
          el.classList.remove("show");
          const parentBtn = sidebar.querySelector(`[data-submenu="${el.id}"]`);
          if (parentBtn) parentBtn.setAttribute("aria-expanded", "false");
        });

        /* Ouvrir le cible si elle était fermée */
        if (!isOpen) {
          submenu.classList.add("show");
          btn.setAttribute("aria-expanded", "true");
        }
      });
    });

    /* ── Liens de navigation : rester actif après un clic ──
       On applique l'état "actif" tout de suite (retour visuel instantané,
       avant même que la nouvelle page ne soit chargée) et on mémorise la
       clé cliquée pour que getActivePage() puisse s'y référer si la page
       de destination n'a pas encore l'attribut data-page. */
    sidebar.querySelectorAll(".nav-link[data-key]").forEach((link) => {
      link.addEventListener("click", () => {
        const key = link.dataset.key;
        if (!key) return;

        try {
          sessionStorage.setItem(ACTIVE_KEY_STORAGE, key);
        } catch (e) {
          /* stockage indisponible (navigation privée, etc.) : on ignore */
        }

        /* Retirer l'état actif de tous les liens/boutons */
        sidebar.querySelectorAll(".nav-link.active").forEach((el) => {
          el.classList.remove("active");
        });

        /* Marquer le lien cliqué comme actif */
        link.classList.add("active");

        /* Si le lien est dans un sous-menu, garder le parent actif/ouvert */
        const parentSubmenu = link.closest(".nav-submenu");
        if (parentSubmenu) {
          const parentBtn = sidebar.querySelector(`[data-submenu="${parentSubmenu.id}"]`);
          if (parentBtn) {
            parentBtn.classList.add("active");
            parentBtn.setAttribute("aria-expanded", "true");
          }
          parentSubmenu.classList.add("show");
        }
      });
    });

    /* ── Responsive : fermer le sidebar au redimensionnement ── */
    window.addEventListener("resize", () => {
      if (isDesktop()) {
        closeSidebar();
      }
    });
  }

  /* ═══════════════════════════════════════════════
     POINT D'ENTRÉE
  ════════════════════════════════════════════════ */

  function init() {
    inject();
    bindEvents();
  }

  /* Attendre que le DOM soit prêt */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();