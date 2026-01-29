from unox import plotting as uplt
from unox import data as udata
from unox.HPC.data0.dataset import uarray
import xarray as xr

def test_select_time():
    """Test the select_time function."""
    # Define xarray objects
    ds_no2_ex = uarray('no2_example_run', is_predict=True).xr
    # Define valid test cases
    test_cases = [
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2020-12-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': '2019-01-15',
            'end_date': None,
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-15 to 2020-12-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': '2019-01-15',
            'end_date': '2019-01-31',
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-15 to 2019-01-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': '2019-01-15',
            'end_date': '2019-01-15',
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'on 2019-01-15',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': '2019-01-31',
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2019-01-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3M',
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2019-04-02 (3 M)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3D',
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2019-01-05 (3 D)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '0D',
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'on 2019-01-02 (0 D)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3M',
            'avg_over': True,
            'sum_over': False,
            'expected_title': 'Averaged from 2019-01-02 to 2019-04-02 (3 M)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3D',
            'avg_over': False,
            'sum_over': True,
            'expected_title': 'Summed from 2019-01-02 to 2019-01-05 (3 D)',
        },
    ]
    # Test each case
    for case in test_cases:
        # Get the actual output
        actual_xr, actual_title = uplt.select_time(
            case['dataset'],
            start_date=case['start_date'],
            end_date=case['end_date'],
            interval=case['interval'],
            avg_over=case['avg_over'],
            sum_over=case['sum_over'],
        )
        # Compare the titles
        assert actual_title == case['expected_title'], f"Expected title '{case['expected_title']}', but got '{actual_title}'"

    # Define invalid dates
    invalid_dates = [
        '2019-02-30',
        '2019-13-01',
        '2019-00-10',
        '2019-01-32',
        'invalid_date',
        123456,
        False,
        [],
        {},
    ]
    # Test invalid dates
    for invalid_date in invalid_dates:
        try:
            uplt.select_time(
                ds_no2_ex,
                start_date=invalid_date,
                end_date=None,
                interval=None,
                avg_over=False,
                sum_over=False,
            )
            assert False, f"Expected an exception for invalid date '{invalid_date}' in `start_date`."
        except Exception:
            pass
        try:
            uplt.select_time(
                ds_no2_ex,
                start_date=None,
                end_date=invalid_date,
                interval=None,
                avg_over=False,
                sum_over=False,
            )
            assert False, f"Expected an exception for invalid date '{invalid_date}' in `start_date`."
        except Exception:
            pass
    # Test when both `avg_over` and `sum_over` are True
    try:
        uplt.select_time(
            ds_no2_ex,
            start_date=None,
            end_date=None,
            interval=None,
            avg_over=True,
            sum_over=True,
        )
        assert False, "Expected an exception when both `avg_over` and `sum_over` are True."
    except Exception:
        pass