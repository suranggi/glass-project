# class Solution:
#     def romanToInt(self, s='III') -> int:
#         ROMAN = {'I': 1,
#                  'V': 5,
#                  'X': 10,
#                  'L': 50,
#                  'C': 100,
#                  'D': 500,
#                  'M': 1000}
#
#         solution = 0
#
#         for i in range(0, len(s)):
#             if ROMAN[s[i]] > ROMAN[s[i+1]]:
#                 solution += ROMAN[s[i]]
#             else:
#                 solution -= ROMAN[s[i]]
#
#         return solution
#
#
# Solution.romanToInt()

class Solution:
    def romanToInt(self, s: str) -> int:
        SYMBOLS = {'I': 1,
                   'V': 5,
                   'X': 10,
                   'L': 50,
                   'C': 100,
                   'D': 500,
                   'M': 1000}

        solution = 0;

        # s[sym + 1] will be out of array bounds if you loop to len(s)
        for sym in range(0, len(s) - 1):
            if SYMBOLS[s[sym]] < SYMBOLS[s[sym + 1]]:
                solution -= SYMBOLS[s[sym]]
            else:
                solution += SYMBOLS[s[sym]]

        solution += SYMBOLS[s[-1]]  # account for last character

        return solution

print(Solution().romanToInt('III'))
