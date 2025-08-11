from typing import Dict
from .db import db

async def update_poll_results(poll_id: str) -> None:
    votes = await db.votes.find({"poll_id": poll_id}).to_list(1000)
    vote_counts: Dict[str, int] = {}
    for vote in votes:
        option_id = vote["option_id"]
        vote_counts[option_id] = vote_counts.get(option_id, 0) + 1
    poll = await db.polls.find_one({"id": poll_id})
    if poll:
        for option in poll["options"]:
            option["votes"] = vote_counts.get(option["id"], 0)
        await db.polls.update_one({"id": poll_id}, {"$set": {"options": poll["options"]}})
