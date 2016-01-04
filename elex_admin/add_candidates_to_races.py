import models
import utils


def add_candidates():
    races = models.ElexRace.select()

    for race in list(races):
        # if not race.nyt_race_name:
        #     try:
        #         r = models.OverrideRace.get(models.OverrideRace.race_raceid == race.raceid)
        #     except models.OverrideRace.DoesNotExist:
        #         r = models.OverrideRace.create(race_raceid=race.raceid)
        #     r.nyt_race_name == race.__unicode__()
        #     r.save()

        candidates = list(race.state())

        for candidate in candidates:
            try:
                oc = models.OverrideCandidate.get(models.OverrideCandidate.candidate_candidateid == candidate.candidateid)
            except models.OverrideCandidate.DoesNotExist:
                oc = models.OverrideCandidate.create(candidate_candidateid=candidate.candidateid)

            oc.nyt_races = [int(race.raceid)]
            oc.save()
            print oc.candidate_candidateid

    models.database.execute_sql(utils.ELEX_RESULTS_VIEW_COMMAND)
    models.database.execute_sql(utils.ELEX_CANDIDATE_VIEW_COMMAND)

if __name__ == "__main__":
    add_candidates()