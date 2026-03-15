# AUTHORA Troubleshooting

Common issues and fixes.

## Login & Auth

**Can't sign in**
- Clear cookies and try again.
- Check that `NEXT_PUBLIC_API_URL` points to your API (or leave empty for same-origin).
- For SSO: verify IdP configuration and redirect URIs.

**Session expired**
- Sign out and sign back in. Tokens refresh automatically; if refresh fails, re-login is required.

## Editor & Saving

**Changes not saving**
- Check network tab for failed requests.
- Ensure you're online. Autosave retries when connection returns.
- If "Failed to save" appears, copy your text elsewhere and refresh. Contact support if it persists.

**Editor blank or frozen**
- Refresh the page. Content is saved; you won't lose work.
- Disable browser extensions that might block scripts.
- Try a different browser (Chrome, Firefox, Safari, Edge).

## AI Features

**AI actions not working**
- Add an API key in Settings → AI (OpenAI or Anthropic).
- Check API key validity and quota.
- Without a key, some actions may be limited.

**Slow AI responses**
- Depends on provider and model. Large selections take longer.
- Try shorter selections for rewrite/expand.

## Export

**Export fails or downloads empty**
- Ensure the book has at least one chapter with content.
- Check API logs for export errors.
- Try a different format (e.g. TXT if DOCX fails).

**Formatting looks wrong**
- DOCX/PDF use manuscript styling. Adjust in Word or your layout tool after export.
- EPUB: some e-readers render differently. Test on target device.

## Performance

**App feels slow**
- Clear browser cache.
- Close other tabs. Large manuscripts use more memory.
- Check [SERVER-SIZING.md](SERVER-SIZING.md) for backend requirements.

## Still stuck?

- **Help center** – Open from the sidebar (Help) for in-app articles.
- **Contact** – Use the contact form on the marketing site.
- **Logs** – For self-hosted: check API and web logs. See [LOGGING.md](LOGGING.md).
