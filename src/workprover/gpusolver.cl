constant ulong k[80] = {
    0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817
};

constant ulong h[8] = {
    0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
    0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
};

#define ROTATE(x, n) ((x) >> (n) | (x) << 64 - (n))

#define C(x, y, z) ((x) & (y) ^ ~(x) & (z))
#define M(x, y, z) ((x) & (y) ^ (x) & (z) ^ (y) & (z))
#define S0(x) (ROTATE((x), 28) ^ ROTATE((x), 34) ^ ROTATE((x), 39))
#define S1(x) (ROTATE((x), 14) ^ ROTATE((x), 18) ^ ROTATE((x), 41))
#define s0(x) (ROTATE((x), 1) ^ ROTATE((x), 8) ^ (x) >> 7)
#define s1(x) (ROTATE((x), 19) ^ ROTATE((x), 61) ^ (x) >> 6)

void sha512_process_block(ulong *state, ulong *block) {
    ulong a = state[0];
    ulong b = state[1];
    ulong c = state[2];
    ulong d = state[3];
    ulong e = state[4];
    ulong f = state[5];
    ulong g = state[6];
    ulong h = state[7];

    ulong *w = block;

    #pragma unroll

    for (size_t i = 0; i < 16; i++) {
        ulong t = k[i] + w[i & 15] + h + S1(e) + C(e, f, g);

        h = g;
        g = f;
        f = e;
        e = d + t;
        t += M(a, b, c) + S0(a);
        d = c;
        c = b;
        b = a;
        a = t;
    }

    #pragma unroll 16

    for (size_t i = 16; i < 80; i++) {
        w[i & 15] += s0(w[i + 1 & 15]) + s1(w[i + 14 & 15]) + w[i + 9 & 15];

        ulong t = k[i] + w[i & 15] + h + S1(e) + C(e, f, g);

        h = g;
        g = f;
        f = e;
        e = d + t;
        t += M(a, b, c) + S0(a);
        d = c;
        c = b;
        b = a;
        a = t;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
    state[5] += f;
    state[6] += g;
    state[7] += h;
}

ulong compute_trial(ulong nonce, global const ulong *initial_hash) {
    ulong fisrt_block[16] = {
        nonce,
        initial_hash[0], initial_hash[1], initial_hash[2], initial_hash[3],
        initial_hash[4], initial_hash[5], initial_hash[6], initial_hash[7],
        0x8000000000000000, 0, 0, 0, 0, 0, 8 * (8 + 64)
    };

    ulong second_block[16] = {
        h[0], h[1], h[2], h[3],
        h[4], h[5], h[6], h[7],
        0x8000000000000000, 0, 0, 0, 0, 0, 0, 8 * 64
    };

    ulong double_hash[8] = {
        h[0], h[1], h[2], h[3],
        h[4], h[5], h[6], h[7]
    };

    sha512_process_block(second_block, fisrt_block);
    sha512_process_block(double_hash, second_block);

    return double_hash[0];
}

kernel void search(global unsigned int *output, global ulong *input) {
    size_t thread_number = get_global_id(0);

    global unsigned int *solutions_count = output;
    global unsigned int *solutions = output + 1;

    global ulong *nonce = input;
    global ulong *initial_hash = input + 1;
    global ulong *target = input + 9;

    ulong trial = compute_trial(*nonce + thread_number, initial_hash);

    if (trial <= *target) {
        unsigned int index = atom_inc(solutions_count);

        solutions[index] = thread_number;
    }
}
