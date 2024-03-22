def assertHash(test, hash_p, hash):
    for k, v in hash_p.items():
        test.assertTrue(k.value in hash)
        test.assertEqual(v.value, hash[k.value])
    test.assertEqual(len(hash_p.keys()), len(hash.keys()))


def assertArray(test, array_p, array):
    for i in range(len(array)):
        test.assertEqual(array_p[i].value, array[i])

    test.assertEqual(len(array), len(array_p))
