import models

if __name__ == "__main__":
    racedate_db = PostgresqlExtDatabase('elex_%s' % os.environ.get('RACEDATE', None),
        user=os.environ.get('ELEX_ADMIN_USER', 'elex'),
        host=os.environ.get('ELEX_ADMIN_HOST', '127.0.0.1')
    )
    models.database_proxy.initialize(racedate_db)
    models.OverrideCandidate.add_candidates()
    models.OverrideRace.create_override_races()