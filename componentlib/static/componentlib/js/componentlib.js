function copyToClipboard(btn) {
    const code = btn.closest(".import-block").querySelector("code");
    if (!code) return;
  
    navigator.clipboard.writeText(code.innerText).then(() => {
      const original = btn.innerText;
      btn.innerText = "✅ Kopieret!";
      btn.disabled = true;
      setTimeout(() => {
        btn.innerText = original;
        btn.disabled = false;
      }, 1500);
    });
  }
  
  async function toggleCode(button, filename) {
    const target = document.getElementById('code-block-' + filename);
    const loaded = button.getAttribute('data-loaded') === 'true';
  
    if (!loaded) {
      const url = button.getAttribute('data-url');
      try {
        const res = await fetch(url);
        const html = await res.text();
        target.innerHTML = html;
        target.style.display = 'block';
        button.textContent = button.textContent.replace('Vis', 'Skjul');
        button.setAttribute('data-loaded', 'true');
      } catch (err) {
        target.innerHTML = '<p>Fejl ved hentning af kode.</p>';
        target.style.display = 'block';
      }
    } else {
      const isVisible = target.style.display !== 'none';
      target.style.display = isVisible ? 'none' : 'block';
      button.textContent = button.textContent.replace(isVisible ? 'Skjul' : 'Vis', isVisible ? 'Vis' : 'Skjul');
    }
  }
  
  async function toggleImport(button, key) {
    const block = document.getElementById('import-' + key);
    const loaded = button.getAttribute('data-loaded') === 'true';
  
    if (!loaded) {
      const url = button.getAttribute('data-url');
      try {
        button.textContent = "⏳ Henter importvejledning...";
        const res = await fetch(url);
        const html = await res.text();
        block.innerHTML = html;
        block.style.display = 'block';
        button.textContent = "🔽 Skjul importvejledning";
        button.setAttribute('data-loaded', 'true');
      } catch (err) {
        block.innerHTML = "<p>Der opstod en fejl.</p>";
        block.style.display = 'block';
        button.textContent = "📦 Prøv igen";
      }
    } else {
      const isVisible = block.style.display !== 'none';
      block.style.display = isVisible ? 'none' : 'block';
      button.textContent = isVisible 
        ? "📦 Vis hvordan du importerer" 
        : "🔽 Skjul importvejledning";
    }
  }
  