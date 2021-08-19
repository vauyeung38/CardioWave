import unittest
import numpy as np
import pandas as pd
from cdwave import param

parameters = ['up_length', 'down_length', 'avg_amplitude', 'std_amplitude',
              'full_down', 'rd_ratio', 'freq', 'maximum', 'max_combo_peaks',
              'std_lambda']


def generate_random_params():
    df = pd.DataFrame({
        'plate': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'],
        'compound': ['NegCtrl', 'NegCtrl', 'A', 'A', 'NegCtrl', 'NegCtrl', 'A', 'A'],
        'well': ['A1', 'A1', 'A2', 'A2', 'B1', 'B1', 'B2', 'B2'],
        'state': ['prior', 'treat', 'prior', 'treat', 'prior', 'treat', 'prior', 'treat'],
        'concentration': [0, 0, 10, 5, 0, 0, 10, 5],
        'index': [1, 2, 3, 4, 5, 6, 7, 8],
        'vendor': ['AstraZeneca'] * 8
    })
    for p in parameters:
        df[p] = np.random.random(8)
    df['fail_analysis'] = False
    return df


class TestParam(unittest.TestCase):
    _data = generate_random_params()

    def test_normalise_baseline(self):
        sub_params = ['rd_ratio']
        div_params = ['up_length', 'down_length', 'avg_amplitude',
                      'full_down', 'maximum']
        div_only_params = ['freq']
        std_params = {'std_amplitude': 'avg_amplitude'}
        all_params = sub_params + div_params + div_only_params + ['std_amplitude']
        df = param.normalise_by_baseline(
            self._data, sub_params, div_params, divide_only_params=div_only_params,
            std_params=std_params)
        self.assertTrue(df[all_params].notna().all().all())

    def test_normalise_negctrl(self):
        sub_params = ['rd_ratio']
        div_params = ['up_length', 'down_length', 'avg_amplitude',
                      'full_down', 'freq', 'maximum', 'std_amplitude']
        all_params = sub_params + div_params
        data = self._data.query('state=="treat"')
        df = param.normalise_by_negctrl(
            data, standardisers={'sm': sub_params, 'sdm': div_params}, control_compound='NegCtrl')
        self.assertTrue(df[all_params].notna().all().all())

    def test_low_quality(self):
        df = self._data
        df, removed_wells = param.remove_low_quality(df)
        for plate in removed_wells:
            wells = removed_wells[plate]
            self.assertEqual(len(df[(df['plate']==plate)&(df['well'].isin(wells))]), 0)
