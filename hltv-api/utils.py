def get_id_from_team_url(url: str) -> int:
    # https://www.hltv.org/teams/4411/ninjas-in-pyjamas
    # https://www.hltv.org/stats/teams/9943/atk
    if "stats" in url:
        return int(url.split("/")[5])
    return int(url.split("/")[4])


def get_id_from_match_url(url: str) -> int:
    # https://www.hltv.org/matches/2363127/9ine-vs-g2-blasttv-paris-major-2023-europe-rmr-b
    return int(url.split("/")[4])


def get_id_from_event_url(url: str) -> int:
    return int(url.split("/")[4])
