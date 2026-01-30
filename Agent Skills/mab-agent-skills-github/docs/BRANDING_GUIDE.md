# MAB AI Strategies Branding & Experience Guide

![MAB AI Strategies logo](assets/mab-logo.svg)

![Mark Bockrath headshot](assets/mark-headshot.svg)

## Brand Palette (Required)

| Token | Hex | Usage |
| --- | --- | --- |
| Dark Blue | `#0B1E3A` | Primary background, headers, hero panels |
| Glimmering Gold | `#D6A756` | Accents, buttons, highlights, icons |
| Off-White | `#F7F4EF` | Body text, surfaces, contrast panels |

### CSS Tokens
```css
:root {
  --mab-dark-blue: #0B1E3A;
  --mab-gold: #D6A756;
  --mab-off-white: #F7F4EF;
}
```

## Logo Usage
- Always use the official logo asset provided in `docs/assets/mab-logo.svg`.
- Maintain clear space equal to the logo icon width on all sides.
- Do not alter colors or stretch the logo.

## Headshot Usage
- Use the professional headshot for executive bios, proposal covers, and demo splash screens.
- Maintain a dark blue background or a high-contrast off-white surface.

## Hyper-Interactive Experience Standards
- **Engagement prompts:** Always include a clear CTA on dashboards (e.g., “Generate Playbook”, “Spin Up Demo”).
- **Purposeful buttons:** Every action must route to a live workflow or an error-handled state.
- **Subtle motion:** Use 150-250ms easing for hover states, with light gold glow effects.
- **Micro-animations:** Pulse status indicators when new insights are ready.
- **Deep interactivity:** Provide hover-to-explain tooltips and inline drill-down panels.

### Example UI Treatment
```css
.button-primary {
  background: var(--mab-gold);
  color: var(--mab-dark-blue);
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(214, 167, 86, 0.35);
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.button-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 18px rgba(214, 167, 86, 0.55);
}
```

## Content Voice
- **Tone:** Confident, data-driven, executive-ready
- **CTA Style:** Direct and action-oriented ("Launch Demo", "Book Strategy Call")
- **Messaging:** Highlight outcomes, ROI, and competitive advantage

## Asset Locations
- Logo: `docs/assets/mab-logo.svg`
- Headshot: `docs/assets/mark-headshot.svg`
