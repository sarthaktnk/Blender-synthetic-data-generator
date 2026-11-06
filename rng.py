import random

def make_rng(master_seed, image_index, topic):
    """Return a random generator that belongs to ONE topic of ONE image.
    
    The same three inputs always give the same sequence of numbers.
    Different topics (or different images) give unrelated sequences."""

    return random.Random(f"{master_seed}-{image_index}-{topic}")

if __name__== "__main__":
    a = make_rng(42, 0, "objects")
    b = make_rng(42, 0, "objects")
    print("same seed, same topic:", a.random(), b.random())
    print("different topic:     ", make_rng(42, 0, "lights").random())
    print("different image:     ", make_rng(42, 1, "objects").random())