# Viral Loop Summary

Share → Signup → Reward flow for AUTHORA.

---

## Flow

1. **User achieves milestone** (words, chapter, badge)
2. **Share prompt** (optional; show after achievement toast)
3. **User creates share** → `POST /growth/share` with type + payload
4. **API returns** share_url, card, caption, social_links
5. **User shares** on Twitter, LinkedIn, or copy link
6. **Friend visits** `/share/{slug}` → sees branded card + CTA
7. **Friend registers** with `?ref={code}` in URL
8. **Referral resolved** → inviter gets credit (reward logic in incentives config)

---

## Share Types

| Type | Payload keys | Example caption |
|------|--------------|-----------------|
| progress | words, display_name | "I wrote 1,000 words today. AUTHORA" |
| milestone | milestone, display_name | "Hit 50,000 words. AUTHORA" |
| achievement | badge_name, display_name | "Earned Week Warrior. AUTHORA" |
| book_finished | display_name | "I finished my book. AUTHORA" |

---

## Referral Code

- **Get**: `GET /growth/referral/code` → `{ code, invite_url }`
- **Invite URL**: `https://authora.studio/register?ref={code}`
- **Register**: Include `referral_code` in `POST /auth/register`

---

## Share Page

- **URL**: `/share/{slug}`
- **Public**: No auth
- **Content**: Card (title, subtitle, CTA), product name, share buttons (X, LinkedIn)
- **OG**: Add `generateMetadata` to fetch from API for og:image, og:title
