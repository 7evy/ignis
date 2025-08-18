from ignis.core import stat_randomization_strategy
from ignis.core.fe14 import fe14_utils

from ignis.core.randomization_step import RandomizationStep


_ALL_SUPPORT_ROUTES = 7


class FE14GlobalCharacterRandomizationStep(RandomizationStep):
    def should_run(self, user_config) -> bool:
        return True

    def name(self) -> str:
        return "Randomize Global Characters (FE14)"

    def run(self, gd, user_config, dependencies):
        rand = dependencies.rand
        classes = dependencies.classes
        characters = dependencies.characters
        skills = dependencies.skills
        stat_strategy = stat_randomization_strategy.from_algorithm(
            user_config.stat_randomization_algorithm
        )
        for original, replacement in characters.swaps:
            # Read cached data from the original character in each slot
            #  and write it to the new character's address
            original_rid = characters.get_original(original.pid)
            replacement_rid = characters.to_rid(replacement.pid)
            replacement_aid = gd.string(original_rid, "aid")
            if user_config.randomize_personal_skills:
                fe14_utils.apply_randomized_skills(
                    gd, characters, user_config, skills, replacement_aid, replacement_rid
                )
            if user_config.randomize_join_order:
                fe14_utils.apply_randomized_bitflags(
                    gd, characters, replacement_aid, replacement_rid, original_rid
                )
                gd.set_int(replacement_rid, "level", gd.int(original_rid, "level"))
                gd.set_int(
                    replacement_rid, "internal_level", gd.int(original_rid, "internal_level")
                )
                gd.set_int(replacement_rid, "support_route", _ALL_SUPPORT_ROUTES)
                gd.set_rid(replacement_rid, "parent", characters.get_parent(original_rid))
            if user_config.randomize_classes:
                fe14_utils.apply_randomized_class_set(
                    gd,
                    characters,
                    classes,
                    replacement_aid,
                    replacement_rid,
                    original_rid,
                    rand,
                    replacement.gender,
                    original.class_level,
                )

            if user_config.characters_keep_their_own_stats:
                # In this case, use the new character's own stats and read/write in place
                fe14_utils.apply_randomized_stats(
                    gd, rand, replacement_rid, replacement_rid, stat_strategy, user_config.passes
                )
            else:
                fe14_utils.apply_randomized_stats(
                    gd, rand, original_rid, replacement_rid, stat_strategy, user_config.passes
                )
        gd.set_store_dirty("gamedata", True)
