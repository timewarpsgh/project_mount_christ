def calc_move_timer(self):
    if self.is_dir_diagnal():
        move_timer = 1.41 * c.PIXELS_COVERED_EACH_MOVE / self.speed
    else:
        move_timer = c.PIXELS_COVERED_EACH_MOVE / self.speed
    return move_timer = 1
