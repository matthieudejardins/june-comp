# web/ — Page vocale (phase A)

> Placeholder. `index.html` est créé en **phase A**.

Spécifications (voir plan §A.3) :
- Web Speech API : `SpeechRecognition` (STT, `lang='fr-FR'`) + `speechSynthesis` (TTS).
- UI : **très gros texte**, fort contraste, **un seul** gros bouton « Parler » (ou démarrage
  auto en mode kiosque), aucun menu.
- Endpointing patient : silence de fin de tour allongé (**≈8 s** ; doc « Orthophonie et
  Démence » : tolérer 8–10 s) pour respecter l'anomie ; ne pas couper sur un souffle.
- Débit TTS : **120–130 mots/min** (posé) — `rate≈0.82` (doc CPT).
- La page parle à Hermes via un petit endpoint local ; lit la réponse en TTS.
