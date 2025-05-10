"""Simple regex"""

from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """Base class for all states"""
    next_states: list[State] = []

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """Checks whether occured character is handled by current state"""

    def check_next(self, next_char: str) -> State | Exception:
        """Check if state accepts the given character"""
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    """Starting state"""
    next_states: list[State] = []

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class TerminationState(State):
    """Accepting state: indicates end of pattern"""
    next_states: list[State] = []

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """State for . character (any character accepted)"""
    next_states: list[State] = []

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    """State for alphabet letters or numbers"""
    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.curr_sym = symbol
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return char == self.curr_sym


class StarState(State):
    """State for '*' (zero or more of previous)"""
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.checking_state = checking_state
        self.next_states = [checking_state]

    def check_self(self, char: str) -> bool:
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):
    """State for '+' (one or more of previous)"""
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.checking_state = checking_state
        self.next_states = [checking_state]

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)


class RegexFSM:
    """Finite-state machine for simple regex"""
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.regex_expr = regex_expr
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            prev_state.next_states.append(tmp_next_state)

        prev_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state: State

        match next_token:
            case ".":
                new_state = DotState()
            case "*":
                new_state = StarState(tmp_next_state)
            case "+":
                new_state = PlusState(tmp_next_state)
            case token if token.isascii():
                new_state = AsciiState(token)
            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, input_str: str) -> bool:
        """Check if input_str matches the regex"""
        return self._match(input_str, 0, self.regex_expr, 0)

    def _match(self, s: str, i: int, p: str, j: int) -> bool:
        if j == len(p):
            return i == len(s)

        next_is_quant = (j + 1 < len(p)) and p[j+1] in '*+'
        char = p[j]
        first_match = i < len(s) and char in (s[i], '.')

        if next_is_quant:
            if p[j+1] == '*':
                if self._match(s, i, p, j+2):
                    return True
                if first_match and self._match(s, i+1, p, j):
                    return True
                return False

            if not first_match:
                return False
            return self._match(s, i+1, p, j) or self._match(s, i+1, p, j+2)

        if first_match:
            return self._match(s, i+1, p, j+1)
        return False


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)
    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
