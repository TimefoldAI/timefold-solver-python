from timefold.solver.score import SimpleScore, HardSoftScore, HardMediumSoftScore, BendableScore


def test_simple_score():
    uninit_score = SimpleScore(10, init_score=-2)
    score = SimpleScore.of(10)

    assert str(uninit_score) == '-2init/10'
    assert str(score) == '10'

    assert SimpleScore.parse('-2init/10') == uninit_score
    assert SimpleScore.parse('10') == score


def test_hard_soft_score():
    uninit_score = HardSoftScore(100, 20, init_score=-3)
    score = HardSoftScore.of(100, 20)

    assert str(uninit_score) == '-3init/100hard/20soft'
    assert str(score) == '100hard/20soft'

    assert HardSoftScore.parse('-3init/100hard/20soft') == uninit_score
    assert HardSoftScore.parse('100hard/20soft') == score


def test_hard_medium_soft_score():
    uninit_score = HardMediumSoftScore(1000, 200, 30, init_score=-4)
    score = HardMediumSoftScore.of(1000, 200, 30)

    assert str(uninit_score) == '-4init/1000hard/200medium/30soft'
    assert str(score) == '1000hard/200medium/30soft'

    assert HardMediumSoftScore.parse('-4init/1000hard/200medium/30soft') == uninit_score
    assert HardMediumSoftScore.parse('1000hard/200medium/30soft') == score


def test_bendable_score():
    uninit_score = BendableScore((1, -2, 3), (-30, 40), init_score=-500)
    score = BendableScore.of((1, -2, 3), (-30, 40))

    assert str(uninit_score) == '-500init/[1/-2/3]hard/[-30/40]soft'
    assert str(score) == '[1/-2/3]hard/[-30/40]soft'

    assert BendableScore.parse('-500init/[1/-2/3]hard/[-30/40]soft') == uninit_score
    assert BendableScore.parse('[1/-2/3]hard/[-30/40]soft') == score
