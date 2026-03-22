from typing import Generator

def accumulator() -> Generator[int, int, None]:
    total = 0
    while True:
        x = yield total   # yield current total, then wait for input 
        if x:
            total += x

gen = accumulator()

print(next(gen))        # Start generator → 0 
print(next(gen))        # Start generator → 0 
print(next(gen))        # Start generator → 0 
print(gen.send(10))     # total = 10 → yields 10
print(next(gen))        # Start generator → 0 
print(gen.send(5))      # total = 15 → yields 15
print(next(gen))        # Start generator → 0 