# Makefile — pilote Cognitive Companion
.PHONY: demo demo-open test graph clean

demo:            ## Rejoue 3 séances → signal famille + rapport ortho (courbe)
	@bash demo.sh

demo-open:       ## Idem + ouvre les rapports dans le navigateur
	@OPEN=1 bash demo.sh

test:            ## Auto-tests : garde-fou détresse + automate SRT/SFA
	@python3 tools/safety.py --selftest
	@echo "" && python3 tools/srt.py --selftest

dataset:         ## (Re)génère le dataset d'exercices (SRT depuis carnet + SFA curés)
	@python3 tools/build_exercise_dataset.py

sovereignty:     ## Audit de souveraineté (cerveau/voix local vs cloud)
	@bash tools/sovereignty_check.sh

graph:           ## (Re)construit le graphe patient via le rotateur Gemini local
	@cd patients/mme-durand && \
	  OPENAI_API_KEY="$$(grep -E '^GEMINI_API_KEY=' $$HOME/.hermes/.env | head -1 | cut -d= -f2- | tr -d '\"')" \
	  OPENAI_BASE_URL="http://127.0.0.1:8765/v1" \
	  GRAPHIFY_OPENAI_MODEL="gemini-2.5-flash" \
	  GRAPHIFY_ALLOW_LOCAL_PROVIDERS=1 \
	  graphify . --no-viz

clean:           ## Vide le journal et les rapports générés
	@: > journal/sessions.jsonl && rm -f rapports/*.html && echo "cleaned"
