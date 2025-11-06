from random import randint

answer = []
while len(answer) < 3:
    answer.append(randint(0, 9))

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

    for i in range(3):
        if int(Num[i]) == answer[i]:
            S += 1
        elif int(Num[i]) in answer:
            B += 1

    if S == 3:
        Win = True
        print(f"축하합니다! {enter_count}번 만에 정답을 맞혔습니다!")
        break
    else:
        print(f"{S}S {B}B")