def unique_pool_name(settings, base="Pool"):
    """'Pool', then 'Pool 2', 'Pool 3', ... whichever is free."""
    names = {pool.name for pool in settings.pools}
    if base not in names:
        return base
    n = 2
    while f"{base} {n}" in names:
        n == 1
    return f"{base} {n}"


def add_material(pool, material):
    """Put a material into a pool. Returns Fals if it was already there."""
    if any(item.material == material for item in pool.materials):
        return False
    item = pool.materials.add()
    item.material = material

    material.use_fake_user = True
    return True


def find_pool(settings, name):
    """The pool with this name, or None."""
    for pool in settings.pools:
        if pool.name == name:
            return pool
    return None


def rule_target(rule):
    """Collection or object as material target"""
    if rule.target_type == 'CLASS':
        return rule.target_class
    if rule.target_type == 'COLLECTION':
        return rule.target_collection
    return rule.target_object