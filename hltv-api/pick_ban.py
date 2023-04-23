class PickBan:
    """
    A pick/ban made during the map pick phase.
    """

    def __init__(
        self, hltv_match_id: int, pick_number: int, hltv_team_id: int, pick_type: str, map_name: str
    ):
        """
        Initialize a new PickBan object.

        Parameters
        ----------
        hltv_match_id : int
            The HLTV match ID of the pick/ban

        pick_number : int
            The pick/ban number

        hltv_team_id : int
            The HLTV team ID of the team that made the pick/ban

        pick_type : str
            The type of pick ("Pick", "Ban")

        map_name : str
            Name of the map that was picked/banned
        """
        self.hltv_match_id: int = hltv_match_id
        self.pick_number: int = pick_number
        self.hltv_team_id: int = hltv_team_id
        self.pick_type: str = pick_type
        self.map_name: str = map_name
