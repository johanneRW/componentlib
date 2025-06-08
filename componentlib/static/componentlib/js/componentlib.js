htmx.config.allowEval = false;

function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
      const originalText = btn.innerHTML;
      btn.innerHTML = "✅ Copied!";
      btn.disabled = true;

      setTimeout(() => {
          btn.innerHTML = originalText;
          btn.disabled = false;
      }, 1500); // The message disappears after 1.5 seconds
  }).catch(err => {
      console.error('Could not copy text: ', err);
  });
}

function copySpecificCode(codeId, btn) {
  const codeElement = document.getElementById(codeId);
  if (!codeElement) {
      console.error('Could not find element with id: ', codeId);
      return;
  }

  const textToCopy = codeElement.innerText;
  copyToClipboard(textToCopy, btn);
}

let currentlyOpenButton = null;

async function toggleCode(button, filename) {
    const target = document.getElementById('code-block-' + filename);
    const loaded = button.getAttribute('data-loaded') === 'true';

    // If another button is open, close it first
    if (currentlyOpenButton && currentlyOpenButton !== button) {
        const currentTarget = document.getElementById('code-block-' + currentlyOpenButton.getAttribute('data-filename'));
        currentTarget.style.display = 'none';
        currentlyOpenButton.textContent = currentlyOpenButton.textContent.replace('Hide', 'Show');
    }

    if (!loaded) {
        const url = button.getAttribute('data-url');
        try {
            const res = await fetch(url);
            const rawContent = await res.text();

            if (filename === 'readme') {
                // Render markdown to HTML
                target.innerHTML = `<div class="markdown-body">${marked.parse(rawContent)}</div>`;
            } else {
                // Use as raw HTML (server delivers <pre><code>)
                target.innerHTML = rawContent;
            }

            target.style.display = 'block';
            button.textContent = button.textContent.replace('Show', 'Hide');
            button.setAttribute('data-loaded', 'true');
            button.setAttribute('data-filename', filename);
            currentlyOpenButton = button;
        } catch (err) {
            target.innerHTML = '<p>Error fetching code.</p>';
            target.style.display = 'block';
            currentlyOpenButton = button;
        }
    } else {
        const isVisible = target.style.display !== 'none';
        if (isVisible) {
            target.style.display = 'none';
            button.textContent = button.textContent.replace('Hide', 'Show');
            currentlyOpenButton = null;
        } else {
            target.style.display = 'block';
            button.textContent = button.textContent.replace('Show', 'Hide');
            currentlyOpenButton = button;
        }
    }
}

document.addEventListener("DOMContentLoaded", function() {
  document.body.addEventListener('htmx:configRequest', function(evt) {
    const btn = evt.target;
    const codeId = btn.getAttribute('data-code-id');
  
    if (codeId) {
        evt.preventDefault(); // Prevent the actual HTTP request
        copySpecificCode(codeId, btn);
    }
  });

  // Add event listeners to all buttons with the class 'toggle-button'
  document.querySelectorAll('.toggle-button').forEach(button => {
      button.addEventListener('click', function() {
          const filename = this.getAttribute('data-filename');
          toggleCode(this, filename);
      });
  });
});
