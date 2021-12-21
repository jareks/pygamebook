from gamebook import Gamebook, Scene

class Dino(Scene):
    def setup(self):
        robot1 = self.new_actor('crocodile')
        robot1.set_position(250, 450)
        robot1.set_dialog('Hej! Jestem Krokodylek')
        robot1.wait(2)
        robot1.set_dialog('Jak masz na imię?')
        robot1.wait(2)
        robot1.set_dialog(None)

        robot2 = self.new_actor('crocodile', hidden = True, orientation='left')
        robot2.set_position(1350, 450)
        robot2.wait(4)
        robot2.set_hidden(False)
        robot2.wait(0.5)
        robot2.set_dialog('Cześć, jestem Frytka!')

game = Gamebook()
game.set_scene(Dino())
game.run()
