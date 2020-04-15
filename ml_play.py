"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def predict(x, l_x, y, l_y):
    m = (y - l_y)/(x - l_x)
    predict_x = (395 - y)/m + x
    for i in range(10):
        if (predict_x > 195):
            predict_x = 390 - predict_x
        elif (predict_x < 0):
            predict_x = 0 - predict_x
        else:
            break
    return predict_x


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    last_x = 75
    last_y = 400
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        (ball_x,ball_y) = scene_info.ball
        platform_x = scene_info.platform[0]
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
                comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
                ball_served = True
        else:
                if (last_y - ball_y) < 0 and ball_y > 300:
                    x = predict(ball_x,last_x,ball_y,last_y)
                    if x < (platform_x + 20):
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                    elif x > (platform_x + 25):
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    else:
                        comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                else:
                    if ball_x < (platform_x + 20):
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                    elif ball_x > (platform_x + 25):
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    else:
                        comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                last_x = ball_x
                last_y = ball_y