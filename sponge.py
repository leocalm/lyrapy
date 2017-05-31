MASK = 0xffffffffffffffff
BLOCK_LEN_INT64 = 8
BLOCK_LEN_BYTES = 8 * BLOCK_LEN_INT64

blake2b_IV = [
    0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
    0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
    0x510e527fade682d1, 0x9b05688c2b3e6c1f,
    0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
]


def rotr(w, c):
    return (w >> c) | (w << (64 - c))


def G(r, i, a, b, c, d):
    a = a + b           & MASK  # noqa
    d = rotr(d ^ a, 32) & MASK  # noqa
    c = c + d           & MASK  # noqa
    b = rotr(b ^ c, 24) & MASK  # noqa
    a = a + b           & MASK  # noqa
    d = rotr(d ^ a, 16) & MASK  # noqa
    c = c + d           & MASK  # noqa
    b = rotr(b ^ c, 63) & MASK  # noqa
    return a, b, c, d


def round_lyra(r, v):
    v[0], v[4], v[8], v[12] = G(r, 0, v[0], v[4], v[8], v[12])
    v[1], v[5], v[9], v[13] = G(r, 1, v[1], v[5], v[9], v[13])
    v[2], v[6], v[10], v[14] = G(r, 2, v[2], v[6], v[10], v[14])
    v[3], v[7], v[11], v[15] = G(r, 3, v[3], v[7], v[11], v[15])
    v[0], v[5], v[10], v[15] = G(r, 4, v[0], v[5], v[10], v[15])
    v[1], v[6], v[11], v[12] = G(r, 5, v[1], v[6], v[11], v[12])
    v[2], v[7], v[8], v[13] = G(r, 6, v[2], v[7], v[8], v[13])
    v[3], v[4], v[9], v[14] = G(r, 7, v[3], v[4], v[9], v[14])


def initState():
    state = [0] * 8
    for i in range(8):
        state.append(blake2b_IV[i])
    return state


def blake2b_lyra(v):
    for i in range(12):
        round_lyra(i, v)


def reduced_blake2b_lyra(v):
    round_lyra(0, v)


def print_state(state, name='state'):
    print(name + ': ', end='')
    for s in state:
        print('{:x}|'.format(s), end='')
    print('\n------------------------------------------')


def copy_block(state, out, start, size=BLOCK_LEN_INT64):
    for i in range(size):
        out[start + i] = state[i]


def squeeze(state, size):
    out = [0] * int(size / BLOCK_LEN_INT64)
    fullBlocks = int(size / BLOCK_LEN_BYTES)
    pos = 0
    for i in range(fullBlocks):
        copy_block(state, out, pos)
        blake2b_lyra(state)
        pos += BLOCK_LEN_INT64

    remaining = int(size % BLOCK_LEN_BYTES / BLOCK_LEN_INT64)
    copy_block(state, out, pos, remaining)

    return out


def pad(text):
    blocks = int(len(text) / BLOCK_LEN_BYTES) + 1
    l = [b for b in text.encode()]
    l.append(0x80)
    r = range(len(l), blocks * BLOCK_LEN_BYTES)
    for _ in r:
        l.append(0)
    l[-1] ^= 0x01
    return l


def build_int64(number_list, pos):
    return ((number_list[pos*BLOCK_LEN_INT64 + 7] << 56) +
            (number_list[pos*BLOCK_LEN_INT64 + 6] << 48) +
            (number_list[pos*BLOCK_LEN_INT64 + 5] << 40) +
            (number_list[pos*BLOCK_LEN_INT64 + 4] << 32) +
            (number_list[pos*BLOCK_LEN_INT64 + 3] << 24) +
            (number_list[pos*BLOCK_LEN_INT64 + 2] << 16) +
            (number_list[pos*BLOCK_LEN_INT64 + 1] << 8) +
            (number_list[pos*BLOCK_LEN_INT64 + 0]))


def absorb_block(state, data, reduced=False):
    for i in range(BLOCK_LEN_INT64):
        state[i] ^= build_int64(data, i)
    if reduced:
        reduced_blake2b_lyra(state)
    else:
        blake2b_lyra(state)


def main():
    state = initState()
    # print_state(state)
    # out = squeeze(state, 96)
    # print_state(state)
    # print_state(out, 'out')
    # print(['{:x}'.format(b) for b in pad('Lyra sponge')])
    absorb_block(state, pad('Lyra sponge'))
    print_state(state)


if __name__ == '__main__':
    main()
