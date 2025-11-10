# external Modules
import sys
import time
from typing import List, Union, Any, Dict, Tuple

# internal Modules


def 사랑하게_될_거야():
    lyrics = [
        "아",
        "뭐가 그리 샘이 났길래",
        "그토록 휘몰아쳤던가",
        "그럼에도 불구하고",
        "나는 너를 용서하고",
        "사랑하게 될 거야"
    ]

    delay_map = [
        [1.5],  # 아
        [0.32, 0.32, 0.05, 0.3, 0.4, 0.05, 0.35, 0.35, 0.05, 0.63, 0.68, 0.4],  # 뭐가 그리 샘이 났길래
        [0.1, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2],  # 그토록 휘몰아쳤던가
        [0.1, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1],  # 그럼에도 불구하고
        [0.1, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2],  # 나는 너를 용서하고
        [0.1, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1]   # 사랑하게 될 거야
    ]

    delay_lyrics = (lyrics, delay_map)

    Utils_S().typewriter_lines(delay_lyrics, line_delay=0.3)
    
class Utils_S:
    def __init__(self):
        pass

    def typewriter_effect(self, text: str, delay_map: float) -> None:
        """
        Simulate a typewriter effect by printing one character at a time with a delay.
        """

        for idx, char in enumerate(text):
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay_map[idx])

    def typewriter_lines(self, delay_lyrics: Tuple[List[str], List[float]], line_delay: float = 0.02) -> None:
        """
        Simulate a typewriter effect for a line of text, ending with a newline.
        """

        for text, delay_map in zip(*delay_lyrics):
            self.typewriter_effect(text, delay_map)
            sys.stdout.write('\n')
            sys.stdout.flush()
            time.sleep(line_delay)

if __name__ == "__main__":
    사랑하게_될_거야()