from functools import update_wrapper


def lru_cache(maxsize=100, get_space=lambda obj: 1):
    assert maxsize > 0

    def decorating_function(user_function):
        cache = dict()
        cache_get = cache.get
        _get_space = get_space
        total_space = [0]
        root = []
        nonlocal_root = [root]
        root[:] = [root, root, None, None, 0]
        prev, next_element = 0, 1

        def wrapper(*args):
            key = tuple(args)
            link = cache_get(key)
            if link is not None:
                root_node, = nonlocal_root
                link_prev, link_next, key, result, _space = link
                link_prev[next_element] = link_next
                link_next[prev] = link_prev
                last = root_node[prev]
                last[next_element] = root_node[prev] = link
                link[prev] = last
                link[next_element] = root_node
                return result

            # MISS
            result = user_function(*args)
            space = _get_space(result)
            total_space[0] += space

            root_node = nonlocal_root[0]

            last = root_node[prev]
            link = [last, root_node, key, result, space]
            cache[key] = last[next_element] = root_node[prev] = link

            while total_space[0] > maxsize:
                _old_prev, old_next, old_key, _old_result, space = root_node[next_element]
                total_space[0] -= space
                root_node[next_element] = old_next
                old_next[prev] = root_node
                del cache[old_key]

            return result

        def cache_clear():
            total_space = [0]
            cache.clear()
            root = nonlocal_root[0]
            root[:] = [root, root, None, None, 0]

        wrapper.__wrapped__ = user_function
        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function
