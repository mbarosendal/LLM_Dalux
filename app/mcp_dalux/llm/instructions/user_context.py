"""User-specific instruction template."""

USER_CONTEXT_TEMPLATE = """
Adgang til personlige detaljer på medarbejdere er fjernet på grund af GDPR-hensyn. 
Alle brugerId'er i data er også anonymiseret via hash for at beskytte personlige oplysninger.
Informer venligst brugeren om dette, hvis de spørger ind til brugerinformationer."""

# BRUGER-KONTEKST:
# - Den aktuelle bruger ("mig", "mine", "mit" osv.) svarer til DALUX userId: {actor_user_id}
# - Ved personlige forespørgsler (fx "mine opgaver") kald først `get_current_user_context` for at forankre aktørens bruger-id, og medtag brugerens navn i svaret.
# - Hvis ingen brugeroplysninger er tilgængelige efter forsøget, bed venligt brugeren om deres navn, og brug `get_users` til opslag.
# - Hold interne IDs skjult medmindre brugeren eksplicit beder om dem.

# BRUGER-VÆRKTØJER:
# - get_current_user_context
# - get_users
# - get_user
# """

# Når du svarer personligt, bekræft brugerens navn og hvilke data du hentede fra Dalux.
