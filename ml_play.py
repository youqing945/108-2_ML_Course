"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

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

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    expect_x = 100
    #vector = [1, 1]
    vector_x = 1
    vector_y = 1
    pass_down = False
    pass_up = False
    l = 0
    w = 0

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

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
            ball_served = True
        else:
            ball_up_x = 0
            ball_up_y = 0
            ball_down_x = 0
            ball_down_y = 0
            ball_x = scene_info.ball[0]
            ball_y = scene_info.ball[1]
            platform_x = scene_info.platform[0]
            l = scene_info.platform[1]

           
            if ball_y < 135 and ball_y >= 125: #up
                ball_up_x = ball_x
                ball_up_y = ball_y
                pass_up = True
                
            if ball_y < 145 and ball_y >= 135 and pass_up == True: #down
                ball_down_x = ball_x
                ball_down_y = ball_y
                pass_down = True
                
            #if ball_down_x - ball_up_x > 0: #right

            if pass_up == True and pass_down == True:
                vector_x = ball_down_x-ball_up_x
                vector_y = ball_down_y-ball_up_y
                expect_x = ((400 - ball_down_y)/(vector_y)) *vector_x + ball_down_x
                while expect_x < 0 or expect_x > 200:
                    if expect_x < 0:
                        expect_x = -expect_x
                    elif expect_x > 200:
                        expect_x = 400 - expect_x
                pass_up = False
                pass_down = False

            if expect_x >= platform_x+20 and expect_x <=platform_x+30:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            elif expect_x < platform_x+20: 
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif expect_x > platform_x+30:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            

            """
            if ball_x < platform_x: 
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif ball_x > platform_x:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            """
