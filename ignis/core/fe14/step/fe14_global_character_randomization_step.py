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
        for char, replacing in characters.swaps:
            rid = characters.to_rid(char.pid)
            replacing_rid = characters.get_original(replacing.pid)
            aid = gd.string(rid, "aid")
            if user_config.randomize_personal_skills:
                fe14_utils.apply_randomized_skills(
                    gd, characters, user_config, skills, aid, rid
                )
            if user_config.randomize_join_order:
                fe14_utils.apply_randomized_bitflags(
                    gd, characters, aid, rid, replacing_rid
                )
                gd.set_int(rid, "level", gd.int(replacing_rid, "level"))
                gd.set_int(
                    rid, "internal_level", gd.int(replacing_rid, "internal_level")
                )
                gd.set_int(rid, "support_route", _ALL_SUPPORT_ROUTES)
                gd.set_rid(rid, "parent", characters.get_parent(replacing_rid))
            if user_config.randomize_classes:
                fe14_utils.apply_randomized_class_set(
                    gd,
                    characters,
                    classes,
                    aid,
                    rid,
                    replacing_rid,
                    rand,
                    char.gender,
                    replacing.class_level,
                )

            if user_config.characters_keep_their_own_stats:
                cached_rid = characters.get_original(char.pid)
                fe14_utils.apply_randomized_stats(
                    gd, rand, cached_rid, rid, stat_strategy, user_config.passes
                )
            else:
                fe14_utils.apply_randomized_stats(
                    gd, rand, replacing_rid, rid, stat_strategy, user_config.passes
                )
        gd.set_store_dirty("gamedata", True)
