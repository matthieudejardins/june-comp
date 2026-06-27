# SOP — Initiation proactive (cron) d'une séance Cognitive Companion

> Layer 1 (Architect). « Proactif » dans le pilote = le cron **ouvre** la séance et la tablette
> en kiosque l'affiche/la joue ; l'aidant n'a rien à lancer. La vraie proactivité mains-libres
> (l'appareil parle sans qu'on touche l'écran) est zone R&D → V2 (cf. plan §A.4, §5).

## Cadence (décidée le 18 juin)
Mode **supervisé** : ex. **09:00, un jour sur deux**.

## Via le scheduler natif d'Hermes (réutilise l'OS existant)
Hermes embarque un cron (dossier `~/.hermes/cron/`). Planifier l'ouverture de séance :

```bash
# Vérifier la commande exacte sur l'install locale (hermes v0.16.0) :
hermes cron --help          # ou : hermes jobs --help

# Exemple (syntaxe à confirmer selon la version) — lancer le skill à 9h, un jour sur deux :
hermes cron add \
  --name "cognitive-companion-mme-durand" \
  --schedule "0 9 */2 * *" \
  --command 'hermes run -s companion-session --patient mme-durand'
```

> ⚠️ La syntaxe exacte (`cron add` / `jobs` / endpoint `/api/jobs`) dépend de la version
> d'Hermes installée. Vérifier `hermes --help` avant de figer. Tracer la commande retenue
> dans `progress.md` (Self-Annealing : si erreur, corriger ici AVANT le code).

## Côté tablette (kiosque) — fast-follow
- iPad/Android en **mode kiosque** (Fully Kiosk), page `web/index.html` plein écran.
- **Écarter Echo Show** (Fire OS verrouillé — exploitation commerciale impossible).
- À l'heure du cron : la séance s'ouvre ; le patient n'a qu'à parler (ou rien, en mains-libres V2).

## Critère d'acceptation (A.4)
- [ ] Le cron déclenche bien l'ouverture de la séance à l'horaire défini (test : planifier à +2 min, observer).
