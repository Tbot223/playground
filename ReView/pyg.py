import pygame
import random
import math
import sys
import requests
import os
import zipfile
import platform

# --- 게임 설정 ---
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# --- 폰트 설정 ---
ZIP_URL = "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip"
ZIP_FILENAME = "./Pretendard-1.3.9.zip"
FONT_FILENAME = "./public/static/Pretendard-Black.otf"
if platform.system() == 'Windows':  # Windows
    EMOJI_FONT = "Segoe UI Emoji"
elif platform.system() == 'Darwin':  # macOS
    EMOJI_FONT = "Apple Color Emoji"
else:
    # not Supported OS
    EMOJI_FONT = None
    

# 색상
RED = (242, 89, 89)
BLUE = (89, 137, 242)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Pygame 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 100)) # 하단에 난이도 표시 영역 추가
pygame.display.set_caption('AI 틱택토 (Minimax)')
screen.fill(WHITE)
try:
    if not os.path.exists(FONT_FILENAME):
        print("폰트를 다운로드 중...")
        response = requests.get(ZIP_URL)
        with open(ZIP_FILENAME, "wb") as f:
            f.write(response.content)
        print("다운로드 완료!")
        print("압축을 해제하는 중...")
        with zipfile.ZipFile(ZIP_FILENAME, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("압축 해제 완료!")
        os.remove(ZIP_FILENAME)
        print("ZIP 파일 삭제 완료!")
    else:
        print("이미 폰트가 존재합니다.")
except Exception as e:
    print(f"폰트 다운로드 중 오류 발생: {e}")
font = pygame.font.Font(FONT_FILENAME, 40)
small_font = pygame.font.Font(FONT_FILENAME, 24)
emoji_font = pygame.font.SysFont(EMOJI_FONT, 32) if EMOJI_FONT is not None else None

# 게임 변수
board = [' '] * 9
human_player = 'X'
ai_player = 'O'
current_player = human_player
game_over = False
difficulty = 0 # 1: 쉬움, 2: 보통, 3: 어려움

# --- AI (미니맥스 알고리즘) 함수 ---

def get_possible_moves(board):
    return [i for i, spot in enumerate(board) if spot == ' ']

def check_win(board, player):
    win_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # 행
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # 열
        (0, 4, 8), (2, 4, 6)             # 대각선
    ]
    for combo in win_combinations:
        if all(board[i] == player for i in combo):
            return True
    return False

def check_game_over(board):
    if check_win(board, human_player): return human_player
    if check_win(board, ai_player): return ai_player
    if not get_possible_moves(board): return 'Tie'
    return None

def minimax(board, depth, is_maximizing, ai_player, human_player, max_depth):
    game_result = check_game_over(board)
    
    if game_result is not None or depth >= max_depth:
        if game_result == ai_player: return 10 - depth
        elif game_result == human_player: return -10 + depth
        return 0
    
    if is_maximizing:
        best_score = -math.inf
        for move in get_possible_moves(board):
            board[move] = ai_player
            score = minimax(board, depth + 1, False, ai_player, human_player, max_depth)
            board[move] = ' '
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = math.inf
        for move in get_possible_moves(board):
            board[move] = human_player
            score = minimax(board, depth + 1, True, ai_player, human_player, max_depth)
            board[move] = ' '
            best_score = min(best_score, score)
        return best_score

def ai_move(board, ai_player, human_player, difficulty):
    possible_moves = get_possible_moves(board)
    if not possible_moves: return None

    # 난이도별 설정
    if difficulty == 1: # 쉬움
        max_depth = 2
        random_chance = 0.8
    elif difficulty == 2: # 보통
        max_depth = 4
        random_chance = 0.3
    elif difficulty == 3: # 어려움 (수정된 설정)
        max_depth = 8
        random_chance = 0.1
    else:
        return random.choice(possible_moves) # 난이도 미선택 시 랜덤

    # 랜덤 수 두기 (난이도 3의 10% 실수를 포함)
    if random.random() < random_chance:
        return random.choice(possible_moves)

    # 미니맥스 기반 최적의 수 찾기
    best_score = -math.inf
    best_move = None
    
    for move in possible_moves:
        board[move] = ai_player
        score = minimax(board, 0, False, ai_player, human_player, max_depth)
        board[move] = ' '
        
        if score > best_score:
            best_score = score
            best_move = move
            
    return best_move

# --- Pygame 그리기 함수 ---

def draw_lines():
    """틱택토 보드 선을 그립니다."""
    # 1. 수평선
    pygame.draw.line(screen, GRAY, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, GRAY, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    # 2. 수직선
    pygame.draw.line(screen, GRAY, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, GRAY, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures():
    """보드에 X와 O 마크를 그립니다."""
    for i in range(BOARD_ROWS):
        for j in range(BOARD_COLS):
            index = i * BOARD_COLS + j
            center_x = j * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = i * SQUARE_SIZE + SQUARE_SIZE // 2
            
            if board[index] == 'O':
                pygame.draw.circle(screen, RED, (center_x, center_y), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[index] == 'X':
                # 첫 번째 대각선
                pygame.draw.line(screen, BLUE, 
                                 (center_x - SPACE, center_y - SPACE), 
                                 (center_x + SPACE, center_y + SPACE), CROSS_WIDTH)
                # 두 번째 대각선
                pygame.draw.line(screen, BLUE, 
                                 (center_x + SPACE, center_y - SPACE), 
                                 (center_x - SPACE, center_y + SPACE), CROSS_WIDTH)

def draw_status(message, color=BLACK, y_offset=0, emoji=None):
    """하단에 게임 상태 메시지를 출력합니다."""
    # 하단 100px 영역을 흰색으로 채움
    pygame.draw.rect(screen, WHITE, (0, HEIGHT, WIDTH, 100)) 
    text_surface = small_font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT + 50 + y_offset))
    if emoji is not None:
        emoji_surface = emoji_font.render(emoji, True, color)
        emoji_rect = emoji_surface.get_rect(center=(WIDTH // 2 - text_rect.width // 2 - 20, HEIGHT + 50 + y_offset))
        screen.blit(emoji_surface, emoji_rect)
    screen.blit(text_surface, text_rect)

def draw_difficulty_buttons():
    """난이도 선택 버튼을 그립니다."""
    # 난이도 선택은 게임 시작 전에만 필요하므로, 게임이 시작되지 않았을 때만 표시
    if difficulty == 0:
        draw_status("난이도 선택: (1)쉬움 (2)보통 (3)어려움", BLACK, -30)
        draw_status("숫자 키 1, 2, 3을 누르세요. (R: 재시작)", BLUE, 10)
    else:
        level_map = {1: "쉬움", 2: "보통", 3: "어려움"}
        draw_status(f"현재 난이도: {level_map.get(difficulty)} (R: 재시작)", BLACK, 0)


def reset_game():
    """게임을 초기화합니다."""
    global board, current_player, game_over, difficulty
    board = [' '] * 9
    current_player = human_player
    game_over = False
    screen.fill(WHITE)
    draw_lines()
    difficulty = 0 # 난이도 재선택

# --- 메인 게임 루프 ---

def main():
    global current_player, game_over, difficulty

    # 초기 화면 그리기
    draw_lines()
    draw_difficulty_buttons()
    pygame.display.update()

    running = True
    ai_turn_active = False # AI 턴 플래그
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            # --- 키 입력 처리 (난이도 선택/재시작) ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # 'R' 키는 재시작
                    reset_game()
                elif difficulty == 0: # 난이도 선택
                    if event.key == pygame.K_1: difficulty = 1
                    elif event.key == pygame.K_2: difficulty = 2
                    elif event.key == pygame.K_3: difficulty = 3
                    
                    if difficulty != 0:
                        screen.fill(WHITE)
                        draw_lines()
                        draw_difficulty_buttons()
                        draw_status(f"난이도 {difficulty} 선택! 먼저 시작하세요 (X)", BLACK, -30)
                        pygame.display.update()
                        
            # --- 마우스 클릭 처리 (사용자 수) ---
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and difficulty != 0:
                if current_player == human_player:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]

                    # 3x3 보드 내에서만 클릭 처리
                    if mouseY < HEIGHT:
                        clicked_col = mouseX // SQUARE_SIZE
                        clicked_row = mouseY // SQUARE_SIZE
                        index = clicked_row * BOARD_COLS + clicked_col

                        if board[index] == ' ':
                            board[index] = human_player
                            current_player = ai_player
                            ai_turn_active = True
                            
                            draw_figures()
                            pygame.display.update()

        # --- AI 턴 처리 ---
        if current_player == ai_player and not game_over and difficulty != 0 and ai_turn_active:
            # AI의 계산을 보여주기 위한 딜레이 (선택 사항)
            pygame.time.wait(500) 
            
            move = ai_move(board, ai_player, human_player, difficulty)
            if move is not None:
                board[move] = ai_player
                draw_figures()
                current_player = human_player
                ai_turn_active = False # AI 턴 완료
                pygame.display.update()

        # --- 게임 종료 상태 확인 ---
        if not game_over and difficulty != 0:
            result = check_game_over(board)
            if result is not None:
                game_over = True
                if result == human_player:
                    draw_status("축하합니다! 당신(X)이 이겼습니다! (R: 재시작)", BLUE, -10, "🎉")
                elif result == ai_player:
                    draw_status("AI(O)가 이겼습니다. (R: 재시작)", RED, -10, "😥")
                else:
                    draw_status("무승부입니다! (R: 재시작)", BLACK, -10, "🤝")
                
                pygame.display.update()

        # 난이도 선택 버튼이 사라지지 않도록 매 루프마다 다시 그림
        if not game_over:
            draw_difficulty_buttons() 
            pygame.display.update()

# 메인 함수 실행
if __name__ == '__main__':
    main()