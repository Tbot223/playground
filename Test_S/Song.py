# external Modules
import sys
import time
from typing import List, Union, Any, Dict, Tuple

# internal Modules


def 사랑하게_될_거야():
    lyrics = [
        ("아", 2),
        ("뭐가 그리 샘이 났길래", 0.05),
        ("그토록 휘몰아쳤던가", 0.05),
        ("그럼에도 불구하고", 0.05),
        ("나는 너를 용서하고", 0.05),
        ("사랑하게 될 거야", 0.05)
    ]

    Utils_S().typewriter_lines(lyrics, line_delay=0.3)
    
class Utils_S:
    def __init__(self):
        pass

    def typewriter_effect(self, text: str, delay: float = 0.05) -> None:
        """
        Simulate a typewriter effect by printing one character at a time with a delay.
        """

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

    def typewriter_lines(self, texts: List[Tuple[str, float]], line_delay: float = 0.05) -> None:
        """
        Simulate a typewriter effect for a line of text, ending with a newline.
        """

        for text, delay in texts:
            self.typewriter_effect(text, delay=delay)
            sys.stdout.write('\n')
            sys.stdout.flush()
            time.sleep(line_delay)

if __name__ == "__main__":
    사랑하게_될_거야()