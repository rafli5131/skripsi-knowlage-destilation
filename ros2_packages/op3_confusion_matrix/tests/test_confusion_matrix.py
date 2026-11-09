import numpy as np
import pytest

from op3_confusion_matrix.report import frame_matrix


def test_true_positive_and_duplicate_false_positive():
    gt = [(0, .5, .5, .2, .2)]
    box = [256., 192., 384., 288.]
    result = frame_matrix(gt, [
        {'class_id': 0, 'confidence': .9, 'xyxy': box},
        {'class_id': 0, 'confidence': .8, 'xyxy': box},
    ])
    assert result[0, 0] == 1 and result[3, 0] == 1
    assert result.sum() == 2


def test_wrong_class_is_one_false_positive_and_one_false_negative():
    gt = [(1, .5, .5, .2, .2)]
    result = frame_matrix(gt, [{'class_id': 2, 'confidence': .9, 'xyxy': [256., 192., 384., 288.]}])
    assert result[1, 2] == 1 and result.sum() == 1
    assert result[1, :].sum() - result[1, 1] == 1
    assert result[:, 2].sum() - result[2, 2] == 1


def test_t38_same_class_match_has_priority_over_wrong_class():
    gt = [(1, .5, .5, .2, .2)]
    result = frame_matrix(gt, [
        {'class_id': 2, 'confidence': .95, 'xyxy': [256., 192., 384., 288.]},
        {'class_id': 1, 'confidence': .30, 'xyxy': [256., 192., 384., 288.]},
    ])
    assert result[1, 1] == 1 and result[3, 2] == 1
    assert result[1, 2] == 0


def test_empty_prediction_and_empty_ground_truth():
    missed = frame_matrix([(2, .5, .5, .2, .2)], [])
    assert missed[2, 3] == 1
    empty = frame_matrix([], [])
    assert np.array_equal(empty, np.zeros((4, 4), dtype=int))


def test_low_overlap_is_missed_target_and_unmatched_prediction():
    result = frame_matrix([(0, .5, .5, .2, .2)], [
        {'class_id': 0, 'confidence': .9, 'xyxy': [0., 0., 20., 20.]},
    ])
    assert result[0, 3] == 1 and result[3, 0] == 1


def test_confidence_threshold_is_strict():
    with pytest.raises(ValueError, match='ambang'):
        frame_matrix([], [{'class_id': 0, 'confidence': .25, 'xyxy': [0., 0., 20., 20.]}])
