
# ProductCard

Komponent til at vise et produkt med navn, beskrivelse og køb-knap.

## Brug
```django
{% render_component "product_card" context %}
```

## Parametre

- `product` (dict): fx `{ id, name, description }`
- `theme` (str): `"bootstrap"`, `"custom"`
- `button_class` (str): ekstra klasser til køb-knappen

## Tags
produkt, CTA,
