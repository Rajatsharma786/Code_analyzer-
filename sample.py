def is_prime(n):
    """Check if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def list_primes(limit):
    """Return a list of prime numbers up to a limit."""
    primes = []
    for num in range(2, limit + 1):
        if is_prime(num):
            primes.append(num)
    return primes

def main():
    limit = 30
    print(f"Prime numbers up to {limit}:")
    primes = list_primes(limit)
    for p in primes:
        print(p, end=\" \")

if __name__ == \"__main__\":
    main()