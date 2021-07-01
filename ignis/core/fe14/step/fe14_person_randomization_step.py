from ignis.model.stat_randomization_algorithm import StatRandomizationAlgorithm

from ignis.core import stat_randomization_strategy

from ignis.core.fe14 import fe14_utils
from ignis.model.fe14_route import FE14Route

from ignis.core.randomization_step import RandomizationStep


class FE14PersonRandomizationStep(RandomizationStep):
    def should_run(self, user_config) -> bool:
        return user_config.randomize_join_order

    def name(self) -> str:
        return "Chapter Character/Person Randomization (FE14)"

    def run(self, gd, user_config, dependencies):
        rand = dependencies.rand
        chapters = dependencies.chapters
        characters = dependencies.characters

        # Get the target files
        files = fe14_utils.get_all_files(gd, "GameData/Person", ".bin.lz", chapters)

        # Randomize each file
        for f in files:
            dirty = False
            rid = gd.multi_open("person", f)
            people = gd.items(rid, "people")
            for rid in people:
                has_changes = self._randomize_person(
                    gd, rid, rand, user_config, characters
                )
                dirty = dirty or has_changes
            if dirty:
                gd.multi_set_dirty("person", f, True)

    @staticmethod
    def _randomize_person(gd, rid, rand, user_config, characters):
        # See if the character matches one that we're randomizing
        dirty = False
        char = characters.get_global_character(gd.key(rid), gd.string(rid, "aid"))
        if not char:
            return dirty
        replacement = characters.get_replacement(gd.key(char))
        replacement_rid = characters.to_rid(replacement)
        aid = gd.string(replacement_rid, "aid")

        # Randomize them
        if user_config.randomize_join_order:
            dirty = True
            fe14_utils.apply_randomized_bitflags(
                gd, characters, aid, rid, replacement_rid
            )
            fe14_utils.morph_character(gd, replacement_rid, rid)

        # Randomizing some character classes/stats can lead to soft locks.
        # Chapter 1 is the biggest issue since MU can get one shot by certain classes.
        if gd.key(rid) == "PID_A001_ボス":
            return dirty

        if user_config.randomize_skills and gd.rid(rid, "personal_skill_normal"):
            dirty = True
            fe14_utils.apply_randomized_skills(gd, characters, aid, rid)
        if user_config.randomize_classes:
            dirty = True
            # TODO: Just copy weapon ranks from global character to the new one?
            #       This avoids edge cases with weapon reassignment
            fe14_utils.apply_randomized_class_set(gd, characters, aid, rid, rid, rand)
        if user_config.stat_randomization_algorithm != StatRandomizationAlgorithm.NONE:
            dirty = True
            stat_strategy = stat_randomization_strategy.from_algorithm(
                user_config.stat_randomization_algorithm
            )
            fe14_utils.apply_randomized_stats(gd, rand, rid, rid, stat_strategy)
        return dirty

    @staticmethod
    def _get_handover_files(gd, user_config):
        handovers = []
        if FE14Route.BIRTHRIGHT in user_config.routes and gd.file_exists(
            "GameData/Person/A_HANDOVER.bin.lz", False
        ):
            handovers.append("GameData/Person/A_HANDOVER.bin.lz")
        if FE14Route.CONQUEST in user_config.routes and gd.file_exists(
            "GameData/Person/B_HANDOVER.bin.lz", False
        ):
            handovers.append("GameData/Person/B_HANDOVER.bin.lz")
        if FE14Route.REVELATION in user_config.routes and gd.file_exists(
            "GameData/Person/C_HANDOVER.bin.lz", False
        ):
            handovers.append("GameData/Person/C_HANDOVER.bin.lz")
        return handovers