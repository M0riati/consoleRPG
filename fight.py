from character import Character


class Fight:
    def __init__(self, party, enemies):
        self.enemies = enemies
        self.party = party
        for character in self.enemies + self.party:
            character.fight = self
        self.currentTurn = None
        self.awaitingPlayerInput = False
        self.combatLog = []

    @property
    def aliveParticipants(self):
        return list(filter(lambda character: not character.dead, self.party + self.enemies))

    @property
    def aliveEnemies(self):
        return list(filter(lambda enemy: not enemy.dead, self.enemies))

    @property
    def aliveParty(self):
        return list(filter(lambda pc: not pc.dead, self.party))

    @property
    def deadParticipants(self):
        return list(filter(lambda character: character.dead, self.party + self.enemies))

    @property
    def deadEnemies(self):
        return list(filter(lambda enemy: enemy.dead, self.enemies))

    @property
    def deadParty(self):
        return list(filter(lambda pc: pc.dead, self.party))

    @property
    def participants(self):
        return self.party + self.enemies

    def update(self, delta):
        if not self.awaitingPlayerInput:
            candidatesForNextTurn = []
            for character in self.aliveParticipants:
                character.update(delta)
                if character.initiative > 100:
                    candidatesForNextTurn.append(character)
            if len(candidatesForNextTurn) > 0:
                winner = (Character('placeholder'), 0)
                for character in candidatesForNextTurn:
                    if winner[1] < character.initiative:
                        winner = (character, character.initiative)
                winner = winner[0]
                winner.initiative = 0
                self.currentTurn = winner
                self.awaitingPlayerInput = winner.turn(self)
