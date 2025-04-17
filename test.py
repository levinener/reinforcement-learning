from pyboy import PyBoy
from pyboy.utils import WindowEvent


def main():
    # 初始化 PyBoy 并加载俄罗斯方块 ROM
    tetris_rom = "Tetris.gb"  # 请替换为实际的俄罗斯方块 ROM 文件路径
    pyboy = PyBoy(tetris_rom)
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "TETRIS"

    # 获取游戏包装器
    tetris = pyboy.game_wrapper
    tetris.game_area_mapping(tetris.mapping_compressed, 0)
    tetris.start_game(timer_div=0x00)  # The timer_div works like a random seed in Tetris
    pyboy.tick()  # To render screen after.start_game
    pyboy.screen.image.save("Tetris1.png")

    # 发送屏幕录制切换事件
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)

    # 检查下一个方块
    tetromino_at_0x00 = tetris.next_tetromino()
    assert tetromino_at_0x00 == "Z", tetris.next_tetromino()
    assert tetris.score == 0
    assert tetris.level == 0
    assert tetris.lines == 0

    # 检查重置游戏后的方块是否相同
    tetris.reset_game(timer_div=0x00)
    assert tetris.next_tetromino() == tetromino_at_0x00, tetris.next_tetromino()

    blank_tile = 0
    first_brick = False
    for frame in range(2000):  # Enough frames for the test. Otherwise do: while pyboy.tick():
        pyboy.tick(1, True)

        # 简单的操作策略，将方块向右移动
        if frame % 4 == 0:  # Even frames to let PyBoy release the button on odd frames
            pyboy.button("left")
        elif frame % 3==0:
            pyboy.button("right")
        elif frame % 2==0:
            pyboy.button("down")            
        else:
            pyboy.button("up")

        # 提取游戏棋盘状态
        game_area = tetris.game_area()
        # game_area 以 [<row>, <column>] 方式访问代表这个图
        # 'game_area[-1,:]' 是获取最后一行的所有列
        if not first_brick and any(filter(lambda x: x != blank_tile, game_area[-1, :])):
            first_brick = True
            print("First brick touched the bottom!")
            print(tetris)

    # 打印最终游戏状态
    print("Final game board:")
    print(tetris)
    pyboy.screen.image.save("Tetris2.png")
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)

    # 验证游戏状态没有改变
    assert tetris.score == 0
    assert tetris.level == 0
    assert tetris.lines == 0

    # 断言游戏底部有方块
    assert any(filter(lambda x: x != blank_tile, game_area[-1, :]))

    # 重置游戏并检查下一个方块
    tetris.reset_game(timer_div=0x00)
    assert tetris.next_tetromino() == tetromino_at_0x00, tetris.next_tetromino()

    tetris.reset_game(timer_div=0x00)
    assert tetris.next_tetromino() == tetromino_at_0x00, tetris.next_tetromino()
    # 重置后，游戏区域应该是干净的
    assert all(filter(lambda x: x != blank_tile, game_area[-1, :]))

    tetris.reset_game(timer_div=0x55)  # The timer_div works like a random seed in Tetris
    assert tetris.next_tetromino() != tetromino_at_0x00, tetris.next_tetromino()

    # 测试默认情况下的随机方块
    selection = set()
    for _ in range(10):
        tetris.reset_game()
        selection.add(tetris.next_tetromino())
    assert len(selection) > 1  # If it's random, we will see more than one kind

    pyboy.stop()


if __name__ == "__main__":
    main()