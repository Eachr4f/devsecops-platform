def test_ci_blocks_failing_tests():
    assert 1 == 2, "Échec volontaire pour vérifier le blocage de la fusion"
