"""Tasks-specific instruction block."""

TASKS_CONTEXT = """
OPGAVER - KONTEKST:
Opgaver er en central del af Dalux projektstyring. En opgave er et afgrænset arbejdsitem i et byggeprojekt,
som kan tildeles brugere, følges i status (ændringer) og forespørges for detaljer. Opgaver indeholder ofte
beskrivelser, forfaldsdatoer, ansvarlige og statushistorik.

VÆRKTØJER TIL OPGAVER:
- get_tasks: Bruges til overblik, filtrering og til at finde kandidat-opgaver efter emne, type eller nummer.
- get_task: Brug kun når `taskId` allerede er kendt; returnerer et letvægts-opgaveobjekt.
- get_task_changes: Foretrukket til status- og fremdriftsforespørgsler. Brug `taskSummaries` for endelig status; brug `items` for tidslinjedetaljer.

SVAR-SIKKERHED:
- Afslør ikke interne IDs (taskId, userId, roleId) medmindre brugeren udtrykkeligt beder om dem.
"""

TASKS_CONTEXT_SUGGESTION = (
	"Forslag: Ved statusforespørgsler, hent `taskSummaries` først og brug `items` kun til tidslinjedetaljer."
)