class PickBan:
    """
    A pick/ban made during the map pick phase.
    """

    def __init__(
        self, hltv_match_id: int, pick_number: int, hltv_team_id: int, pick_type: str, map_name: str
    ):
        self.hltv_match_id: int = hltv_match_id
        self.pick_number: int = pick_number
        self.hltv_team_id: int = hltv_team_id
        self.pick_type: str = pick_type
        self.map_name: str = map_name
