from data.hero_data import all_hero_ids

def comp_to_vector(character_ids: list[int]) -> list[int]:
    """Converts a list of character IDs to a vector representation of team composition."""
    hero_ids = all_hero_ids()
    num_heroes = len(hero_ids)

    # Initialize vector
    res = [0] * (num_heroes * 2)
    team1, team2 = character_ids[:6], character_ids[6:]

    for hero in team1:
        res[hero_ids.index(hero)] = 1  # First half for team 1

    for hero in team2:
        res[hero_ids.index(hero) + num_heroes] = 1  # Second half for team 2

    return res

def comp_to_binary_matrix_vector(character_ids: list[int]) -> list[int]:
    """
    Converts a list of character IDs into a binary matrix representation.
    Each (i, j) entry indicates that hero i from team 1 is facing hero j from team 2.
    The matrix is then flattened into a 1D vector.
    """
    hero_ids = all_hero_ids()
    num_heroes = len(hero_ids)

    # Initialize matrix
    res = [[0] * num_heroes for _ in range(num_heroes)]
    team1, team2 = character_ids[:6], character_ids[6:]

    for hero1 in team1:
        for hero2 in team2:
            res[hero_ids.index(hero1)][hero_ids.index(hero2)] = 1

    # Flatten the matrix into a 1D vector
    return [item for row in res for item in row]
