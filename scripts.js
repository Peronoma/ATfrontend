document.addEventListener("DOMContentLoaded", () => {
  // Typed.js greeting
  if (window.Typed) {
    new window.Typed("#typed-greeting", {
      strings: ["Hola, amigo!", "Hello, friend!", "Namaste!"],
      typeSpeed: 60,
      backSpeed: 40,
      backDelay: 1200,
      smartBackspace: true,
      loop: true,
      showCursor: true,
      cursorChar: "|",
    });
  }

  // Skills toggle
  const skillsGrid = document.getElementById("skills-grid");
  if (skillsGrid) {
    skillsGrid.addEventListener("click", (e) => {
      const card = e.target.closest(".skill-card");
      if (!card) return;
      const descEl = card.querySelector(".skill-desc");
      const text = card.getAttribute("data-description") || "";

      if (text && !descEl.dataset.initialized) {
        descEl.textContent = text;
        descEl.dataset.initialized = "true";
      }
      document.querySelectorAll("#skills-grid .skill-desc").forEach((d) => {
        if (d !== descEl) d.classList.add("hidden");
      });
      descEl.classList.toggle("hidden");
    });
  }

  // Projects tech breakdown toggle
  const projectsGrid = document.getElementById("projects-grid");
  if (projectsGrid) {
    projectsGrid.addEventListener("click", (e) => {
      const card = e.target.closest(".project-card");
      if (!card) return;
      if (e.target.closest("a[href]")) return;

      const details = card.querySelector(".tech-details");
      const container = details?.querySelector(".space-y-2");
      if (!details || !container) return;

      document.querySelectorAll("#projects-grid .tech-details").forEach((d) => {
        if (d !== details) d.classList.add("hidden");
      });

      if (!details.dataset.initialized) {
        try {
          const tech = JSON.parse(card.getAttribute("data-tech") || "{}");
          container.innerHTML = "";
          Object.entries(tech).forEach(([name, pct]) => {
            const row = document.createElement("div");
            row.className = "flex items-center gap-3";
            row.innerHTML = `
              <p class="w-28 text-sm text-muted-dark">${name}</p>
              <div class="h-2 flex-1 rounded-full bg-card-dark">
                <div class="gradient-flow h-2 rounded-full" style="width: ${pct}%"></div>
              </div>
              <p class="w-10 text-right text-sm font-medium text-foreground-dark">${pct}%</p>
            `;
            container.appendChild(row);
          });
          details.dataset.initialized = "true";
        } catch (err) {
          console.error("Invalid data-tech on project-card", err);
        }
      }

      details.classList.toggle("hidden");
    });
  }
  // Mobile drawer toggle
  const menuBtn = document.getElementById("mobile-menu-button");
  const closeBtn = document.getElementById("mobile-close-button");
  const drawer = document.getElementById("mobile-drawer");
  const backdrop = document.getElementById("mobile-backdrop");

  function openDrawer() {
    if (!drawer || !backdrop) return;
    drawer.classList.remove("translate-x-full");
    backdrop.classList.remove("hidden");
  }
  function closeDrawer() {
    if (!drawer || !backdrop) return;
    drawer.classList.add("translate-x-full");
    backdrop.classList.add("hidden");
  }

  if (menuBtn) menuBtn.addEventListener("click", openDrawer);
  if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
  if (backdrop) backdrop.addEventListener("click", closeDrawer);
  drawer?.querySelectorAll("a[href^='#']").forEach((a) => a.addEventListener("click", closeDrawer));

  // Contact form handler with backend connection
  const form = document.getElementById("contact-form");
  const statusEl = document.getElementById("contact-status");
  
  if (form && statusEl) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      statusEl.textContent = "Sending...";
      statusEl.className = "mt-3 text-sm text-muted-dark";
      
      try {
        const formData = new FormData(form);
        const body = Object.fromEntries(formData.entries());
        
        // Use absolute URL when opened as file://, relative in production
        const API_BASE = "http://127.0.0.1:5000";
        
        const res = await fetch(`${API_BASE}/api/contact`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        
        const data = await res.json();
        
        if (!res.ok) {
          throw new Error(data.error || "Request failed");
        }
        
        statusEl.textContent = data.message || "Message sent successfully!";
        statusEl.className = "mt-3 text-sm text-green-400";
        form.reset();
        
      } catch (err) {
        statusEl.textContent = err.message || "Failed to send. Please try again.";
        statusEl.className = "mt-3 text-sm text-red-400";
        console.error("Contact form error:", err);
      }
    });
  }
});