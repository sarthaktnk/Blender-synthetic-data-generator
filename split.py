def split_of(index, val_percent):
    before = (index * val_percent) // 100
    after = ((index + 1) * val_percent) // 100
    return "val" if after > before else "train"


def count_val(total, val_percent):
    return (total * val_percent) // 100

