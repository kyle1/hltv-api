def get_id_from_match_url(url: str) -> int:
    # https://www.hltv.org/matches/2363127/9ine-vs-g2-blasttv-paris-major-2023-europe-rmr-b
    return int(url.split("/")[4])
