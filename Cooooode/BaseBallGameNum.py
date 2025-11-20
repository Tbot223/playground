from random import randint

answer = []
while len(answer) < 3:
    num = randint(0, 9)
    if num not in answer:
        answer.append(num)

Win = False
enter_count = 0

while(True):
    Num = 000
    Num = input("세 자리 숫자 입력: ")
    S = 0
    B = 0
    enter_count += 1

    if Win == True:
        break

    Num_list = [int(i) for i in Num]
    for i in range(3):
        if Num_list[i] == answer[i]:
            Num_list[i] = -1  # 중복 카운팅 방지
            S += 1
        elif Num_list[i] in answer:
            B += 1

    
    if S == 3:
        Win = True
        print(f"축하합니다! {enter_count}번 만에 정답을 맞혔습니다!")
        break
    else:
        print(f"{S}S {B}B")