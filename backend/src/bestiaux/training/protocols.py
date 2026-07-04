from bestiaux.creature.protocols import ICreatureRepository

# Training uses the full ICreatureRepository (which includes get_mentor_data)
ITrainingCreatureRepository = ICreatureRepository
