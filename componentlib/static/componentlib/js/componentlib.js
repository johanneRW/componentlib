function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
      const originalText = btn.innerHTML;
      btn.innerHTML = "✅ Kopieret!";
      btn.disabled = true;

      setTimeout(() => {
          btn.innerHTML = originalText;
          btn.disabled = false;
      }, 1500); // Beskeden forsvinder efter 1.5 sekunder
  }).catch(err => {
      console.error('Kunne ikke kopiere tekst: ', err);
  });
}

function copySpecificCode(codeId) {
  const codeElement = document.getElementById(codeId);
  if (!codeElement) {
      console.error('Kunne ikke finde elementet med id: ', codeId);
      return;
  }

  const btn = event.target;
  const textToCopy = codeElement.innerText;
  copyToClipboard(textToCopy, btn);
}

  
  let currentlyOpenButton = null;

async function toggleCode(button, filename) {
    const target = document.getElementById('code-block-' + filename);
    const loaded = button.getAttribute('data-loaded') === 'true';

    // Hvis der er en anden åben knap, luk den først
    if (currentlyOpenButton && currentlyOpenButton !== button) {
        const currentTarget = document.getElementById('code-block-' + currentlyOpenButton.getAttribute('data-filename'));
        currentTarget.style.display = 'none';
        currentlyOpenButton.textContent = currentlyOpenButton.textContent.replace('Skjul', 'Vis');
    }

    if (!loaded) {
        const url = button.getAttribute('data-url');
        try {
            const res = await fetch(url);
            const rawContent = await res.text();

            if (filename === 'readme') {
                // Render markdown til HTML
                target.innerHTML = `<div class="markdown-body">${marked.parse(rawContent)}</div>`;
            } else {
                // Brug som raw HTML (serveren leverer <pre><code>)
                target.innerHTML = rawContent;
            }

            target.style.display = 'block';
            button.textContent = button.textContent.replace('Vis', 'Skjul');
            button.setAttribute('data-loaded', 'true');
            button.setAttribute('data-filename', filename);
            currentlyOpenButton = button;
        } catch (err) {
            target.innerHTML = '<p>Fejl ved hentning af kode.</p>';
            target.style.display = 'block';
            currentlyOpenButton = button;
        }
    } else {
        const isVisible = target.style.display !== 'none';
        if (isVisible) {
            target.style.display = 'none';
            button.textContent = button.textContent.replace('Skjul', 'Vis');
            currentlyOpenButton = null;
        } else {
            target.style.display = 'block';
            button.textContent = button.textContent.replace('Vis', 'Skjul');
            currentlyOpenButton = button;
        }
    }
}


document.addEventListener("DOMContentLoaded", function() {
  const grid = document.querySelector('.component-grid');
  if (grid) {
    const items = grid.querySelectorAll('.component-list-item');

    if (items.length > 10) {
      // Flyt kortene til den anden kolonne, hvis der er mere end 10 kort
      items.forEach((item, index) => {
        if (index >= 10) {
          item.style.gridColumn = '2';
        }
      });
    }
  }
});
