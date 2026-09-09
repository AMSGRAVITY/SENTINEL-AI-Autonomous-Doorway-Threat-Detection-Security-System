from typing import Dict
from threat_detection.core.person_track import PersonTrack

class PersonManager:
    def __init__(self):
        self.people: Dict[int, PersonTrack] = {}
    
    def exists(self, track_id: int) -> bool:
        return track_id in self.people
    
    def get(self, track_id: int) -> PersonTrack | None:
        return self.people.get(track_id)
    
    def get_or_create(self, track_id: int) -> PersonTrack:
        person = self.people.get(track_id)
        if person is None:
            person = PersonTrack(track_id=track_id)
            self.people[track_id] = person
        return person
    
    def remove(self, track_id: int):
        self.people.pop(track_id, None)
    
    def all(self):
        return self.people.values()
    
    def items(self):
        return self.people.items()

    def clear(self):
        self.people.clear()
    
    def __len__(self):
        return len(self.people)