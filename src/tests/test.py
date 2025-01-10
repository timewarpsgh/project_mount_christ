def earn_xp(self, amount, duty_type):
    # Send XP earned pack
    pack = pb.XpEarned(
        mate_id=self.id,
        duty_type=duty_type,
        amount=amount
    )
    self.mate_mgr.role.session.send(pack)

    # Define a mapping of the duty types to their respective XP and level variables
    duty_map = {
        pb.DutyType.CHIEF_NAVIGATOR: ('xp_in_nav', 'lv_in_nav', self.navigation),
        pb.DutyType.ACCOUNTANT: ('xp_in_acc', 'lv_in_acc', self.accounting),
        pb.DutyType.FIRST_MATE: ('xp_in_bat', 'lv_in_bat', self.battle)
    }

    # Retrieve the appropriate variables based on the duty type
    xp_var_name, lv_var_name, duty_value = duty_map.get(duty_type, (None, None, None))
    if xp_var_name is None:
        return

    # Retrieve the current XP and level
    xp_variable = getattr(self, xp_var_name)
    lv_variable = getattr(self, lv_var_name)

    # Handle XP increase and leveling up logic
    if lv_variable >= c.MAX_LV:
        return

    xp_variable += amount

    has_lved_up = False
    while xp_variable >= c.LV_2_MAX_XP[lv_variable]:
        if lv_variable >= c.MAX_LV:
            break

        xp_at_next_lv = xp_variable - c.LV_2_MAX_XP[lv_variable]
        self.lv_up(duty_type, xp_at_next_lv)
        has_lved_up = True

    if has_lved_up:
        # Send level-up pack
        pack = pb.LvUped(
            mate_id=self.id,
            duty_type=duty_type,
            lv=lv_variable,
            xp=xp_variable,
            value=duty_value,
        )
        self.mate_mgr.role.session.send(pack)


def lv_up(self, duty_type, xp_at_next_lv):
    talent_chance = 0.5

    # Define a mapping of duty types to their respective level variables and talent increase values
    duty_map = {
        pb.DutyType.CHIEF_NAVIGATOR: ('lv_in_nav', 'xp_in_nav', self.navigation, self.talent_in_navigation),
        pb.DutyType.ACCOUNTANT: ('lv_in_acc', 'xp_in_acc', self.accounting, self.talent_in_accounting),
        pb.DutyType.FIRST_MATE: ('lv_in_bat', 'xp_in_bat', self.battle, self.talent_in_battle)
    }

    # Retrieve the appropriate variables based on the duty type
    lv_var_name, xp_var_name, duty_value, talent_value = duty_map.get(duty_type, (None, None, None, None))
    if lv_var_name is None:
        return

    # Level up the character and set XP to the value at the next level
    setattr(self, lv_var_name, getattr(self, lv_var_name) + 1)
    setattr(self, xp_var_name, xp_at_next_lv)

    # Hard increase in the specified attribute
    setattr(self, lv_var_name.split('_')[1], duty_value + 1)

    # Talent-based increase (if applicable)
    if random.random() < talent_chance:
        setattr(self, lv_var_name.split('_')[1], getattr(self, lv_var_name.split('_')[1]) + talent_value)
